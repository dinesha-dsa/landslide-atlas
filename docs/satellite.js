export function ageLabel(timestamp, now = Date.now()) {
  const hours = (now - Date.parse(timestamp)) / 3600000;
  if (!Number.isFinite(hours) || hours < 0) return 'Timestamp needs review';
  return `${hours.toFixed(1)} hours old${hours > 24 ? ' · refresh recommended' : ''}`;
}

const host = typeof document === 'undefined' ? null : document.querySelector('#satellite-content');
if (host) load();

function element(tag, text, parent) {
  const node = document.createElement(tag);
  node.textContent = text;
  parent.append(node);
  return node;
}
function link(text, url, parent) {
  if (!url?.startsWith('https://')) return;
  const a = element('a', text, parent);
  a.href = url; a.target = '_blank'; a.rel = 'noopener noreferrer';
}
async function load() {
  try {
    const response = await fetch('data/satellite-feeds.json', {cache:'no-store'});
    if (!response.ok) throw Error('Snapshot unavailable');
    const data = await response.json();
    host.replaceChildren();
    element('p', `Snapshot retrieved: ${data.generated_utc} · ${ageLabel(data.generated_utc)}. Updates are manual; reloading this page does not query the satellites.`, host);
    const cards = element('div', '', host); cards.className = 'satellite-cards';
    const rain = element('article', '', cards);
    element('h3', 'NASA IMERG Early · rainfall', rain);
    const r = data.rainfall;
    const m = r.measurement;
    const hasValue = m && m.mean_rate_mm_hr !== null;
    element('strong', hasValue ? `${m.mean_rate_mm_hr.toFixed(2)} mm/h · pilot area mean` : 'No rainfall measurement ingested', rain);
    element('p', `Status: ${r.status.replaceAll('_',' ')}. ` + (r.status === 'auth_required' ? 'NASA returned an authentication requirement for the numerical data download.' : 'See provenance for the catalogue and import status.'), rain);
    if (r.observation_end_utc) element('p', `Latest listed interval ends: ${r.observation_end_utc} (exclusive UTC). This is catalogue evidence, not a measured value on this page.`, rain);
    if (m) {
      element('p', `Imported interval: ${m.observation_start_utc} to ${m.observation_end_utc} · ${ageLabel(m.observation_end_utc)}. Valid cells: ${m.valid_cells}/${m.selected_cells}.`, rain);
      if (hasValue) element('p', `30-minute mean depth: ${m.mean_depth_mm_30min.toFixed(2)} mm. ${m.method}`, rain);
    }
    element('p', 'Native sampling: about 0.1° (~10 km), every 30 minutes; Early delivery has a nominal delay of about four hours. These are precipitation estimates, not a rainfall forecast or slope sensor.', rain);
    link('NASA product documentation ↗', 'https://gpm.nasa.gov/data/imerg', rain);
    link('Open rainfall catalogue ↗', r.catalogue_url, rain);
    const radar = element('article', '', cards);
    element('h3', 'Sentinel-1 SLC · radar catalogue', radar);
    const s = data.radar;
    element('strong', s.status === 'available' ? 'Acquisitions found · metadata only' : `Catalogue ${s.status}`, radar);
    element('p', 'No radar images have been processed and no ground displacement has been estimated. Footprints intersect the pilot box; this does not establish full coverage or InSAR suitability.', radar);
    if (s.records?.length) {
      const list = element('ul', '', radar);
      for (const item of s.records.slice(0,3)) {
        const row = element('li', `${item.acquired_utc} · ${item.platform} · orbit ${item.relative_orbit} ${item.orbit_direction}. `, list);
        link('Inspect source metadata ↗', item.metadata_url, row);
      }
      element('p', `Showing newest ${Math.min(3,s.records.length)} of ${s.records.length} returned records (limit ${s.record_limit}, ${s.window_days}-day search). ${s.more_results ? 'Further records exist.' : ''} Same-orbit, overlapping bursts and coherence checks are required before deformation analysis.`, radar);
    }
    link('Reproduce radar search ↗', s.query_url, radar);
  } catch {
    host.textContent = 'Satellite snapshot could not be loaded. No current data or safety inference is available. Use the repository instructions to refresh and inspect the source status.';
  }
}
