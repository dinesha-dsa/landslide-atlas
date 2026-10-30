"""Snapshot official catalogues; optionally summarize an authorized IMERG HDF5 file.

No credentials are needed for catalogue queries. No satellite measurements are
invented when a download is unavailable. See research/satellite-feeds/README.md.
"""
import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import urljoin
import requests

ROOT = Path(__file__).resolve().parents[1]
BBOX = [73.02, 17.8, 73.7, 18.6]
NASA = 'https://gpm1.gesdisc.eosdis.nasa.gov/data/GPM_L3/GPM_3IMERGHHE.07/'
STAC = 'https://stac.dataspace.copernicus.eu/v1/search'

def iso(value):
    return value.isoformat().replace('+00:00', 'Z')

def granule_interval(name):
    match = re.search(r'\.(\d{8})-S(\d{6})-E(\d{6})\.', name)
    if not match:
        raise ValueError('Not a timestamped IMERG granule')
    day, start, end = match.groups()
    a = datetime.strptime(day + start, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
    b = datetime.strptime(day + end, '%Y%m%d%H%M%S').replace(tzinfo=timezone.utc)
    if b < a:
        b += timedelta(days=1)
    return a, b + timedelta(seconds=1)  # half-open observation interval

def radar_snapshot(session, now):
    params = {'collections': 'sentinel-1-slc', 'bbox': ','.join(map(str, BBOX)),
              'datetime': iso(now-timedelta(days=60))+'/'+iso(now), 'limit': 12, 'sortby': '-datetime'}
    response = session.get(STAC, params=params, timeout=45)
    response.raise_for_status()
    payload = response.json()
    records = []
    for item in payload['features']:
        if item.get('collection') != 'sentinel-1-slc':
            raise ValueError('Unexpected radar collection')
        p = item['properties']
        acquired = datetime.fromisoformat(p['datetime'].replace('Z', '+00:00'))
        if acquired > now:
            raise ValueError('Future acquisition in catalogue')
        records.append({'id': item['id'], 'acquired_utc': p['datetime'],
                        'published_utc': p.get('published'), 'platform': p.get('platform'),
                        'relative_orbit': p.get('sat:relative_orbit'),
                        'orbit_direction': p.get('sat:orbit_state'), 'bbox': item['bbox'],
                        'metadata_url': next(x['href'] for x in item['links'] if x['rel']=='self')})
    return {'status': 'available' if records else 'empty', 'query_url': response.url,
            'response_sha256': hashlib.sha256(response.content).hexdigest(),
            'retrieved_utc': iso(now), 'window_days': 60, 'record_limit': 12,
            'more_results': any(x['rel']=='next' for x in payload.get('links', [])),
            'records': records, 'measurements_processed': False}

def rainfall_catalogue(session, now):
    # Check today and yesterday: a new UTC day can have no published files yet.
    for offset in range(2):
        day = now - timedelta(days=offset)
        directory = NASA + day.strftime('%Y/%j/')
        response = session.get(directory, timeout=40)
        if response.status_code == 404:
            continue
        response.raise_for_status()
        names = sorted(set(re.findall(r'href="([^"/]+\.HDF5)"', response.text)))
        names = [n for n in names if granule_interval(n)[1] <= now]
        if not names:
            continue
        name = names[-1]
        url = urljoin(directory, name)
        with session.get(url, stream=True, timeout=40) as probe:
            code = probe.status_code
            if code not in (200, 401, 403):
                probe.raise_for_status()
        start, end = granule_interval(name)
        return {'status': 'auth_required' if code in (401,403) else 'download_available',
                'catalogue_status': 'available', 'catalogue_url': directory,
                'retrieved_utc': iso(now), 'granule': name, 'download_url': url,
                'observation_start_utc': iso(start), 'observation_end_utc': iso(end),
                'download_probe_http': code, 'measurement': None,
                'response_sha256': hashlib.sha256(response.content).hexdigest()}
    return {'status': 'empty', 'catalogue_status': 'empty', 'measurement': None,
            'retrieved_utc': iso(now), 'catalogue_url': NASA}

def summarize_imerg(path, now):
    import h5py
    import numpy as np
    if not path.name.startswith('3B-HHR-E.') or '.V07' not in path.name:
        raise ValueError('Expected an IMERG Early V07 HDF5 granule')
    start, end = granule_interval(path.name)
    if end > now or (end-start).total_seconds() != 1800:
        raise ValueError('Expected a completed 30-minute observation')
    with h5py.File(path) as f:
        grid = f['Grid']
        dataset = grid['precipitation']
        unit = dataset.attrs.get('units', '')
        if isinstance(unit, bytes):
            unit = unit.decode()
        if str(unit).strip().lower() not in ('mm/hr', 'mm/h'):
            raise ValueError('Unknown precipitation units; refusing an assumed conversion')
        lat, lon = grid['lat'][:], grid['lon'][:]
        raw = dataset[:]
        # IMERG native dimensions are time, longitude, latitude. Fail closed.
        if raw.shape != (1, len(lon), len(lat)):
            raise ValueError('Unexpected IMERG axis order or shape')
        xs = np.flatnonzero((lon >= BBOX[0]) & (lon <= BBOX[2]))
        ys = np.flatnonzero((lat >= BBOX[1]) & (lat <= BBOX[3]))
        if not len(xs) or not len(ys):
            raise ValueError('No grid-cell centres in pilot box')
        values = raw[0][np.ix_(xs, ys)].astype(float)
        fill = dataset.attrs.get('_FillValue', -9999.9)
        valid = np.isfinite(values) & (values != fill) & (values >= 0)
        scale = float(dataset.attrs.get('scale_factor', 1))
        offset = float(dataset.attrs.get('add_offset', 0))
        values = values * scale + offset
        valid &= values >= 0
        weights = np.broadcast_to(np.cos(np.deg2rad(lat[ys])), values.shape)
        mean = float(np.average(values[valid], weights=weights[valid])) if valid.any() else None
        return {'source_file': path.name, 'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'observation_start_utc': iso(start), 'observation_end_utc': iso(end),
                'mean_rate_mm_hr': mean, 'mean_depth_mm_30min': None if mean is None else mean*0.5,
                'valid_cells': int(valid.sum()), 'selected_cells': int(values.size),
                'scale_factor': scale, 'add_offset': offset,
                'method': 'Cosine-latitude weighted mean of valid cells whose centres lie inside pilot rectangle; not a district polygon or point measurement.'}

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--imerg-file', type=Path)
    parser.add_argument('--output', type=Path, default=ROOT/'docs/data/satellite-feeds.json')
    args = parser.parse_args()
    now = datetime.now(timezone.utc)
    session = requests.Session()
    session.headers['User-Agent'] = 'LandslideAtlasResearch/1.0'
    output = {'schema_version': 1, 'generated_utc': iso(now),
              'aoi': {'name': 'Southern Raigad pilot rectangle', 'bbox': BBOX,
                      'crs': 'EPSG:4326', 'scope': 'Fixed pilot; independent of state/district explorer filters.'},
              'forecast_validated': False}
    for key, function in [('radar',radar_snapshot), ('rainfall',rainfall_catalogue)]:
        try:
            output[key] = function(session, now)
        except (requests.RequestException, ValueError, KeyError, StopIteration) as error:
            output[key] = {'status': 'failed', 'error_type': type(error).__name__,
                           'retrieved_utc': iso(now), 'measurement': None}
    if args.imerg_file:
        # Invalid input aborts without overwriting an earlier good snapshot.
        measurement = summarize_imerg(args.imerg_file, now)
        output['rainfall']['measurement'] = measurement
        output['rainfall']['status'] = 'imported' if measurement['valid_cells'] else 'no_valid_cells'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix('.tmp')
    temporary.write_text(json.dumps(output, indent=2)+'\n', encoding='utf-8')
    temporary.replace(args.output)
    print(json.dumps({'output': str(args.output), 'radar': output['radar']['status'],
                      'rainfall': output['rainfall']['status']}))

if __name__ == '__main__':
    main()
