export const SCHEMA='landslide-atlas-project-v1';
export const STORAGE_KEY='landslide-atlas-session-v1';
export function safeUrl(value){try{const u=new URL(value);return ['https:','http:'].includes(u.protocol)?u.href:null;}catch{return null;}}
export function validDate(value){return typeof value==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(value)&&!Number.isNaN(Date.parse(value))&&new Date(value).toISOString().slice(0,10)===value;}
export function normalizeRecord(r,id){
 if(!r||typeof r!=='object')throw Error('Record must be an object');
 const lat=Number(r.latitude),lon=Number(r.longitude);
 if(r.latitude===''||r.longitude===''||r.latitude==null||r.longitude==null||!Number.isFinite(lat)||!Number.isFinite(lon)||Math.abs(lat)>90||Math.abs(lon)>180)throw Error('Valid WGS84 latitude and longitude are required');
 if(!String(r.title||'').trim())throw Error('An observation title is required');
 const source=safeUrl(r.source_url);if(!source)throw Error('A valid HTTP(S) source URL is required');
 if(!String(r.license||'').trim()||!String(r.source_name||'').trim())throw Error('Source name and licence / permission statement are required');
 if(r.date&&!validDate(r.date))throw Error('Event date must be a real date in YYYY-MM-DD format');
 return {id,title:String(r.title).trim().slice(0,200),latitude:lat,longitude:lon,date:r.date||null,category:String(r.category||'Unknown').slice(0,80),trigger:String(r.trigger||'Unknown').slice(0,80),source_url:source,source_name:String(r.source_name).slice(0,160),license:String(r.license).slice(0,250),citation:String(r.citation||'').slice(0,2000),location_accuracy:String(r.location_accuracy||'Not specified by contributor').slice(0,300),source_id:'local-contribution',verification:'Unreviewed local contribution; not independently verified',added_utc:new Date().toISOString()};
}
export function filterRecords(records,f){return records.filter(r=>{
 if(f.state&&r.state!==f.state)return false;if(f.district&&r.district_id!==f.district)return false;
 if(f.trigger&&r.trigger!==f.trigger)return false;
 if(!r.date)return f.includeUndated;
 const y=Number(r.date.slice(0,4));return (!f.from||y>=f.from)&&(!f.to||y<=f.to);
});}
export function counts(records,key){const m=new Map();for(const r of records){const k=String(r[key]||'Unknown');m.set(k,(m.get(k)||0)+1);}return [...m.entries()].sort((a,b)=>b[1]-a[1]||a[0].localeCompare(b[0]));}
export function csvCell(value){let s=value==null?'':String(value);if(typeof value==='string'&&/^[\s]*[=+\-@]/.test(s))s="'"+s;return '"'+s.replaceAll('"','""')+'"';}
export function toCSV(records,columns){return [columns.map(csvCell).join(','),...records.map(r=>columns.map(c=>csvCell(r[c])).join(','))].join('\r\n');}
export function parseCSV(text){
 const rows=[];let row=[],cell='',quoted=false;
 for(let i=0;i<text.length;i++){const c=text[i];if(c==='"'){if(quoted&&text[i+1]==='"'){cell+='"';i++;}else if(quoted||cell==='')quoted=!quoted;else throw Error('Malformed CSV quote');}
 else if(c===','&&!quoted){row.push(cell);cell='';}
 else if((c==='\n'||c==='\r')&&!quoted){if(c==='\r'&&text[i+1]==='\n')i++;row.push(cell);if(row.some(x=>x.trim()))rows.push(row);row=[];cell='';}
 else cell+=c;}
 if(quoted)throw Error('Unclosed CSV quote');row.push(cell);if(row.some(x=>x.trim()))rows.push(row);
 if(rows.length<2)throw Error('CSV needs a header and at least one record');
 const headers=rows.shift().map(x=>x.replace(/^\uFEFF/,'').trim());if(new Set(headers).size!==headers.length)throw Error('Duplicate CSV headers');
 return rows.map((cells,i)=>{if(cells.length!==headers.length)throw Error('CSV column mismatch on row '+(i+2));return Object.fromEntries(headers.map((h,j)=>[h,cells[j]]));});
}
function onSegment(p,a,b){const cross=(p[0]-a[0])*(b[1]-a[1])-(p[1]-a[1])*(b[0]-a[0]);return Math.abs(cross)<1e-10&&p[0]>=Math.min(a[0],b[0])&&p[0]<=Math.max(a[0],b[0])&&p[1]>=Math.min(a[1],b[1])&&p[1]<=Math.max(a[1],b[1]);}
function ringContains(p,ring){let inside=false;for(let i=0,j=ring.length-1;i<ring.length;j=i++){const a=ring[j],b=ring[i];if(onSegment(p,a,b))return true;if((b[1]>p[1])!==(a[1]>p[1])&&p[0]<(a[0]-b[0])*(p[1]-b[1])/(a[1]-b[1])+b[0])inside=!inside;}return inside;}
export function pointInGeometry(point,g){if(!g)return false;const polys=g.type==='Polygon'?[g.coordinates]:g.type==='MultiPolygon'?g.coordinates:[];return polys.some(poly=>ringContains(point,poly[0])&&!poly.slice(1).some(r=>ringContains(point,r)));}
export function assignRegion(r,states,districts){const p=[r.longitude,r.latitude],ds=districts.filter(f=>pointInGeometry(p,f.geometry));if(ds.length===1){const d=ds[0].properties;return {...r,state:d.state,district:d.name,district_id:d.id,boundary_assignment:'single polygon intersection'};}const ss=states.filter(f=>pointInGeometry(p,f.geometry));return {...r,state:ss.length===1?ss[0].properties.state:'Unassigned',district:'Unassigned',district_id:'',boundary_assignment:ds.length?'ambiguous border':'outside boundary snapshot'};}
export function geometryBounds(features){let b=[Infinity,Infinity,-Infinity,-Infinity];function visit(a){if(typeof a[0]==='number'){b[0]=Math.min(b[0],a[0]);b[1]=Math.min(b[1],a[1]);b[2]=Math.max(b[2],a[0]);b[3]=Math.max(b[3],a[1]);}else for(const c of a)visit(c);}for(const f of features)visit(f.geometry.coordinates);return Number.isFinite(b[0])?b:[67,6,99,38];}
export function gridCounts(records,size=.25){const cells=new Map();for(const r of records){const x=Math.floor(r.longitude/size)*size,y=Math.floor(r.latitude/size)*size,k=x+','+y;const v=cells.get(k)||{x,y,count:0};v.count++;cells.set(k,v);}return [...cells.values()];}
