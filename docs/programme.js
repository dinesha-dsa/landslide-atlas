const target=document.querySelector('#programme-content');
if(target) showProgramme();
async function showProgramme(){
  try{
    const response=await fetch('data/research-programme.json',{cache:'no-store'});
    if(!response.ok) throw Error('Unavailable');
    const data=await response.json();target.replaceChildren();
    const summary=document.createElement('p');
    summary.textContent=`Inventory audit: ${data.audit.maharashtra_reports} Maharashtra candidate reports; ${data.audit.pilot_rectangle_reports} in the fixed pilot rectangle. Independently verified forecast labels: ${data.audit.independently_verified_forecast_labels}. These counts describe reports, not deduplicated events.`;
    target.append(summary);
    const grid=document.createElement('div');grid.className='programme-grid';target.append(grid);
    for(const item of data.priorities){
      const article=document.createElement('article');grid.append(article);
      for(const [tag,text] of [['h3',`${item.id}. ${item.title}`],['strong',item.status],['p',item.started],['p',`Next evidence needed: ${item.next}`]]){
        const node=document.createElement(tag);node.textContent=text;article.append(node);
      }
      const a=document.createElement('a');a.textContent='Open workstream resources ↗';
      a.href='https://github.com/dinesha-dsa/landslide-atlas/tree/main/research/forecasting/'+item.resource;
      a.target='_blank';a.rel='noopener noreferrer';article.append(a);
    }
  }catch{target.textContent='Research status could not be loaded. Open the repository protocol and workplan for the current evidence requirements.';}
}
