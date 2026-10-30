"""Fetch attributable public snapshots; never substitutes invented observations."""
from __future__ import annotations
import hashlib,json,sys,time
from datetime import datetime,timezone
from pathlib import Path
import geopandas as gpd
import requests

ROOT=Path(__file__).resolve().parents[1]
CACHE=ROOT/'.cache';CACHE.mkdir(exist_ok=True)
OUT=ROOT/'docs/data';OUT.mkdir(parents=True,exist_ok=True)
session=requests.Session()
session.headers['User-Agent']='Landslide-Research-Atlas/1.0 (public research snapshot)'
sources=[]
def get(url,name,params=None):
    path=CACHE/name
    if not path.exists():
        for attempt in range(3):
            try:
                r=session.get(url,params=params,timeout=90);r.raise_for_status()
                path.write_bytes(r.content);break
            except requests.RequestException:
                if attempt==2:raise
                time.sleep(2)
    data=path.read_bytes()
    return json.loads(data),hashlib.sha256(data).hexdigest()
def save(name,data):
    (OUT/name).write_text(json.dumps(data,ensure_ascii=False,separators=(',',':')),encoding='utf-8')
def boundary(level):
    api=f'https://www.geoboundaries.org/api/current/gbOpen/IND/ADM{level}/'
    meta,_=get(api,f'adm{level}_metadata.json')
    geo,sha=get(meta['simplifiedGeometryGeoJSON'],f'adm{level}_simplified.json')
    frame=gpd.GeoDataFrame.from_features(geo['features'],crs=4326)
    frame.geometry=frame.to_crs(6933).geometry.simplify(300,preserve_topology=True).to_crs(4326)
    sources.append({'id':f'boundaries-adm{level}','title':f'geoBoundaries India ADM{level}',
      'url':api,'download_url':meta['simplifiedGeometryGeoJSON'],'sha256':sha,
      'license':meta['boundaryLicense'],'year_represented':meta['boundaryYearRepresented'],
      'boundary_id':meta['boundaryID'],'original_sources':meta['boundarySource'],
      'citation':'Runfola et al. (2020), geoBoundaries: A global database of political administrative boundaries, PLOS ONE 15(4): e0231866. DOI:10.1371/journal.pone.0231866',
      'upstream_declared_units':meta['admUnitCount'],'downloaded_units':len(frame),
      'transformations':'Simplified download, further simplified with 300 m tolerance in EPSG:6933, topology preserved within each feature; ADM2 parent assigned by greatest area overlap in EPSG:6933. Coordinates rounded to 4 decimals. Dated research snapshot; not survey-grade geometry.'})
    return frame,meta

def main():
    states,sm=boundary(1);districts,dm=boundary(2)
    # Name assignment uses polygon overlap, not centroids on irregular coastal borders.
    sp=states.to_crs(6933);dp=districts.to_crs(6933)
    parents=[]
    for geom in dp.geometry:
        candidates=list(sp.sindex.query(geom,predicate='intersects'))
        if not candidates:parents.append('Unassigned');continue
        parent=max(candidates,key=lambda i:geom.intersection(sp.geometry.iloc[i]).area)
        parents.append(str(states.iloc[parent]['shapeName']))
    districts['state']=parents
    states['state']=states['shapeName'].astype(str)
    states['id']=states['shapeID'].astype(str)
    districts['id']=districts['shapeID'].astype(str)
    def feature_rows(frame,kind):
        features=[]
        for _,r in frame.iterrows():
            props={'id':r['id'],'name':str(r['shapeName']),'state':r['state'],'kind':kind}
            features.append({'type':'Feature','properties':props,'geometry':r.geometry.__geo_interface__})
        return {'type':'FeatureCollection','features':features}
    # GeoJSON is kept as separate licensed boundary datasets, not relicensed as app code.
    def rounded(value):
        if isinstance(value,float):return round(value,4)
        if isinstance(value,list):return [rounded(x) for x in value]
        if isinstance(value,dict):return {k:rounded(v) for k,v in value.items()}
        return value
    save('states.geojson',rounded(feature_rows(states,'state')))
    save('districts.geojson',rounded(feature_rows(districts,'district')))
    save('regions.json',{'states':sorted(states['state'].tolist()),'districts':[
        {'id':r['id'],'name':str(r['shapeName']),'state':r['state']} for _,r in districts.sort_values(['state','shapeName']).iterrows()],
        'state_boundary_year':sm['boundaryYearRepresented'],'district_boundary_year':dm['boundaryYearRepresented']})
    service='https://gis.earthdata.nasa.gov/portal/rest/services/Landslides/COOLR_Reports_Points/MapServer/0'
    metadata,_=get(service,'nasa_reports_metadata.json',{'f':'json'})
    if 'error' in metadata:raise ValueError(metadata['error'])
    where="country_name = 'India'"
    ids,_=get(service+'/query','nasa_india_ids.json',{'f':'json','where':where,'returnIdsOnly':'true'})
    if 'error' in ids:raise ValueError(ids['error'])
    object_ids=sorted(ids.get('objectIds') or [])
    if not object_ids:raise ValueError('No report IDs returned; inspect source rather than fabricating data')
    features=[];batch_hashes=[]
    for i in range(0,len(object_ids),500):
        batch,sha=get(service+'/query',f'nasa_india_batch_{i}.json',{'f':'geojson','objectIds':','.join(map(str,object_ids[i:i+500])),
            'outFields':'*','outSR':4326,'returnGeometry':'true'})
        if 'error' in batch:raise ValueError(batch['error'])
        if batch.get('exceededTransferLimit'):raise ValueError('Incomplete NASA batch; reduce batch size')
        features.extend(batch['features']);batch_hashes.append(sha)
    if len(features)!=len(object_ids):raise ValueError('NASA ID/query count mismatch')
    records=[];excluded=0
    for feature in features:
        p=feature['properties'];g=feature.get('geometry')
        if not g or g.get('type')!='Point':excluded+=1;continue
        lon,lat=g['coordinates'][:2]
        if not(-180<=lon<=180 and -90<=lat<=90):excluded+=1;continue
        dt=p.get('event_date');date=None
        if dt:
            try:
                date=datetime.fromtimestamp(dt/1000,timezone.utc).date().isoformat() if isinstance(dt,(int,float)) else str(dt)[:10]
            except (ValueError,OverflowError,OSError):pass
        records.append({'id':'nasa-'+str(p.get('objectid',p.get('OBJECTID',len(records)))),
          'title':p.get('event_title') or p.get('location_description') or 'COOLR landslide report',
          'longitude':lon,'latitude':lat,'date':date,
          'category':p.get('landslide_category') or 'Unknown','trigger':p.get('landslide_trigger') or 'Unknown',
          'source_name':p.get('source_name') or 'NASA COOLR','source_url':p.get('source_link') or 'https://landslides.nasa.gov/',
          'citation':p.get('citation') or '',
          'location_accuracy':p.get('location_accuracy') or 'Not specified in snapshot',
          'fatalities':p.get('fatality_count'),'source_id':'nasa-coolr-reports','license':'NASA COOLR: preserve original contributor citation; see source manifest',
          'verification':'Repository report; not independently field-verified by this project'})
    points=gpd.GeoDataFrame(records,geometry=gpd.points_from_xy([r['longitude'] for r in records],[r['latitude'] for r in records]),crs=4326)
    # Boundary association is a reproducible display join, not a claim about original reporting jurisdiction.
    d_index=districts.sindex;s_index=states.sindex
    for idx,point in enumerate(points.geometry):
        matches=sorted(d_index.query(point,predicate='intersects'))
        state_matches=sorted(s_index.query(point,predicate='intersects'))
        if len(matches)==1:
            r=districts.iloc[matches[0]];records[idx].update(state=r['state'],district=str(r['shapeName']),district_id=r['id'],boundary_assignment='single polygon intersection')
        else:
            state=str(states.iloc[state_matches[0]]['state']) if len(state_matches)==1 else 'Unassigned'
            records[idx].update(state=state,district='Unassigned',district_id='',boundary_assignment='ambiguous border' if matches else 'outside boundary snapshot')
    sources.insert(0,{'id':'nasa-coolr-reports','title':'NASA COOLR landslide report points - India country-name query',
      'url':'https://landslides.nasa.gov/','api':service,'query':where,'retrieved_ids':len(object_ids),'usable_points':len(records),
      'excluded_geometry':excluded,'batch_sha256':batch_hashes,'copyright':metadata.get('copyrightText'),
      'license':'Publicly accessible NASA repository; retain contributor/source attribution and review linked dataset terms. No third-party GSI inventory is bundled.',
      'citation':'Juang, Stanley and Kirschbaum (2019), Using citizen science to expand the global map of landslides: Introducing COOLR, PLOS ONE 14(7): e0218657. DOI:10.1371/journal.pone.0218657',
      'transformations':'Country-name query; point geometries only; UTC event dates; selected source attributes; point-in-polygon assignment to dated boundary snapshots.',
      'limitations':'Report locations and dates can be uncertain. Coverage is incomplete and reporting-biased. Zero reports does not indicate zero hazard. Report counts are not independent event counts. No automatic de-duplication across sources is claimed.'})
    save('observations.json',records)
    manifest={'schema_version':'1.0','prepared_utc':datetime.now(timezone.utc).isoformat(),
      'sources':sources,'counts':{'states':len(states),'districts':len(districts),'observations':len(records),'unassigned_district':sum(not r['district_id'] for r in records)},
      'exclusions':['Unpublished manuscripts and author emails','Downloaded journal PDFs','GSI-attributed third-party mirror and exact model training points','Unvalidated national susceptibility predictions'],
      'refresh':'Manual, reproducible snapshot. Run scripts/prepare_data.py after reviewing upstream changes; remove only the desired .cache files to refetch.',
      'boundary_notice':'Snapshot geography for research, not an official or current administrative or territorial representation. State and district vintages differ. ADM2 metadata declares 736 units, while its simplified file contains 735; this discrepancy is preserved rather than filled with invented geometry.'}
    save('manifest.json',manifest)
    print(json.dumps(manifest['counts']),flush=True)

if __name__=='__main__':main()
