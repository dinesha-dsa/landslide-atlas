import test from 'node:test';
import assert from 'node:assert/strict';
import {readFile} from 'node:fs/promises';
import {filterRecords,counts,parseCSV,toCSV,csvCell,normalizeRecord,pointInGeometry,assignRegion,geometryBounds,gridCounts,safeUrl,validDate} from '../docs/core.js';
const row={title:'Field record',latitude:18,longitude:73,date:'2021-07-22',trigger:'rain',source_name:'Field team',source_url:'https://example.org/record',license:'Own observation'};
test('year filters preserve explicit undated policy and regional intersection',()=>{
 const records=[{state:'A',district_id:'a',date:'2020-01-01',trigger:'rain'},{state:'A',district_id:'a',date:null,trigger:'rain'},{state:'B',district_id:'b',date:'2021-01-01',trigger:'rain'}];
 assert.equal(filterRecords(records,{state:'A',from:2021,includeUndated:true}).length,1);
 assert.equal(filterRecords(records,{state:'A',from:2021,includeUndated:false}).length,0);
 assert.equal(filterRecords(records,{district:'b',includeUndated:true}).length,1);
});
test('imports require real coordinates, calendar dates, attribution and safe source URLs',()=>{
 assert.equal(normalizeRecord(row,'local-test').source_id,'local-contribution');
 for(const bad of [{latitude:''},{latitude:null},{longitude:Infinity},{latitude:91},{date:'2023-02-29'},{source_url:'javascript:alert(1)'},{license:''},{source_name:''}])assert.throws(()=>normalizeRecord({...row,...bad},'bad'));
 assert.equal(validDate('2024-02-29'),true);assert.equal(safeUrl('data:text/html,test'),null);
});
test('CSV handles quotes, embedded newlines, BOM, negative coordinates and spreadsheet formula strings',()=>{
 const r=[{title:'A, "quoted"\nrecord',latitude:-18.3,source_url:'https://example.org'}];const out=parseCSV(toCSV(r,['title','latitude','source_url']));assert.equal(out[0].title,r[0].title);assert.equal(Number(out[0].latitude),-18.3);
 assert.equal(csvCell('=1+1'),'"\'=1+1"');assert.equal(csvCell(' \t@cmd'),'"\' \t@cmd"');
 assert.equal(parseCSV('\uFEFFtitle,latitude\r\nx,18')[0].title,'x');assert.throws(()=>parseCSV('a,a\n1,2'));assert.throws(()=>parseCSV('a,b\n"bad,1'));
});
const polygon={type:'Polygon',coordinates:[[[0,0],[10,0],[10,10],[0,10],[0,0]],[[4,4],[6,4],[6,6],[4,6],[4,4]]]};
test('polygon membership respects holes and marks ambiguous shared boundaries',()=>{
 assert.equal(pointInGeometry([2,2],polygon),true);assert.equal(pointInGeometry([5,5],polygon),false);assert.equal(pointInGeometry([12,5],polygon),false);
 const f={geometry:polygon,properties:{state:'A',name:'District A',id:'a'}};
 assert.equal(assignRegion({latitude:2,longitude:2},[f],[f]).district_id,'a');
 assert.equal(assignRegion({latitude:2,longitude:2},[f],[f,f]).boundary_assignment,'ambiguous border');
});
test('count grids conserve observations including negative longitudes',()=>{
 const records=[{longitude:73.01,latitude:18.01},{longitude:73.02,latitude:18.02},{longitude:-.01,latitude:18.03}];const bins=gridCounts(records);assert.equal(bins.reduce((s,x)=>s+x.count,0),3);assert.equal(bins.find(x=>x.x<0).x,-.25);
});
test('published snapshot is internally consistent and contains no GSI mirror records',async()=>{
 const load=async n=>JSON.parse(await readFile(new URL('../docs/data/'+n,import.meta.url),'utf8'));
 const [records,regions,states,districts,manifest]=await Promise.all(['observations.json','regions.json','states.geojson','districts.geojson','manifest.json'].map(load));
 assert.equal(records.length,manifest.counts.observations);assert.equal(new Set(records.map(r=>r.id)).size,records.length);
 assert.equal(states.features.length,36);assert.equal(districts.features.length,regions.districts.length);
 assert(records.every(r=>r.source_id==='nasa-coolr-reports'));assert(records.every(r=>r.latitude>=-90&&r.latitude<=90&&r.longitude>=-180&&r.longitude<=180));
 assert(records.every(r=>!r.date||validDate(r.date)));assert.equal(counts(records,'state').reduce((s,x)=>s+x[1],0),records.length);
 const state=regions.states.find(x=>x.normalize('NFD').replace(/\p{Diacritic}/gu,'')==='Maharashtra');assert(state,'Maharashtra default must resolve despite source diacritics');assert(records.some(r=>r.state===state));
 assert.deepEqual(geometryBounds([{geometry:polygon}]),[0,0,10,10]);
 const districtIds=new Set(regions.districts.map(d=>d.id));assert(records.every(r=>!r.district_id||districtIds.has(r.district_id)));
 // Recompute sampled spatial assignments against the exact public geometry.
 for(const r of records.filter((_,i)=>i%43===0)){const assigned=assignRegion(r,states.features,districts.features);assert.equal(assigned.district_id,r.district_id,'Published point/boundary join mismatch: '+r.id);}
});
