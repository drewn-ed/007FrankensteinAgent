// PATCH forms are rendered from tested interfaces; execution never asks a model.
export function createLocalActions({$,api,esc,icon,toast,getState,getData,getBrowser,getRoute,setRoute,leave,showView,header,renderSidebar,refresh,sourceRun}) {
  let current=null, pending=null, generation=0;
  const title=s=>String(s).replaceAll('_',' ').replace(/^./,c=>c.toUpperCase());
  const eligible=r=>(r.manifest.kind||'task')==='task' && r.tests?.length && r.tests.every(t=>t.passed);
  const records=()=>getState().registry.filter(eligible);
  const empty=s=>s.default??s.enum?.[0]??(s.type==='array'?[]:s.type==='object'?Object.fromEntries(Object.entries(s.properties||{}).filter(([k])=>(s.required||[]).includes(k)).map(([k,v])=>[k,empty(v)])):s.type==='boolean'?false:['number','integer'].includes(s.type)?(s.minimum??0):'');
  function shell(label){leave();setRoute({type:'actions',id:null,projectId:null});showView('library');header(label||'Actions');renderSidebar();}
  function render(){
    if(getRoute().type!=='actions'||getRoute().id)return;
    const rows=records(),projects=getData().projects;
    $('library-view').innerHTML=`<div class="view-heading"><h1>Actions</h1><span class="sample-tag">${rows.length} ready</span></div><p class="view-description">Your work, turned into tools. Run a learned operation with new inputs, even when AI is off.</p><section class="blackout-card"><div><h2>Blackout</h2><p>Pause AI. Your saved actions keep working locally.</p></div><button class="secondary-button" data-local="blackout" aria-pressed="${!!getState().ai_paused}" ${getState().busy?'disabled':''}>${getState().ai_paused?'Resume AI':'Pause AI'}</button></section><div class="patch-list">${rows.map(r=>`<button class="library-row patch-row" data-local="open" data-id="${esc(r.manifest.id)}">${icon('reuse')}<div><strong>${esc(r.manifest.title)}</strong><p>${esc(r.manifest.description)}</p><small>${esc(projects.find(p=>p.id===r.provenance?.project_id)?.name||'Shared')} · v${r.version} · ${r.tests.length} tests</small></div><span class="row-end">Run locally →</span></button>`).join('')||`<div class="empty-state">${icon('reuse')}<h2>Give your software a new ability.</h2><p>Start a task in a chat. When the agent creates and tests a compute skill, its action appears here automatically.</p></div>`}</div><p class="field-note">Actions run saved code on the inputs you provide. Supported app changes require a separate confirmation. New instructions still need AI.</p>`;
  }
  function open(){generation++;current=null;pending=null;shell();render();}
  // Each node returns a DOM element and a typed reader, keeping user values out of HTML attributes.
  function field(schema,value,label,depth=0){
    const wrap=document.createElement('div');wrap.className='patch-field';
    const id='patch-'+crypto.randomUUID();
    const caption=document.createElement('label');caption.htmlFor=id;caption.textContent=label;wrap.append(caption);
    if(schema.description){const note=document.createElement('p');note.className='field-note';note.textContent=schema.description;wrap.append(note);}
    if(schema.type==='object'&&schema.properties&&depth<5){
      const children=[];caption.className='patch-group-label';
      for(const [key,sub] of Object.entries(schema.properties)){
        const required=(schema.required||[]).includes(key),present=value&&Object.hasOwn(value,key);
        const row=field(sub,present?value[key]:empty(sub),title(key),depth+1);
        let enabled=null;
        if(!required){enabled=document.createElement('input');enabled.type='checkbox';enabled.checked=!!present;enabled.setAttribute('aria-label','Include '+title(key));const toggle=document.createElement('label');toggle.className='patch-optional';toggle.append(enabled,document.createTextNode(' Include '+title(key)));wrap.append(toggle);row.el.hidden=!enabled.checked;enabled.onchange=()=>row.el.hidden=!enabled.checked;}
        wrap.append(row.el);children.push({key,row,enabled});
      }
      return {el:wrap,read:()=>Object.fromEntries(children.filter(c=>!c.enabled||c.enabled.checked).map(c=>[c.key,c.row.read()]))};
    }
    if(schema.type==='array'&&schema.items&&depth<5){
      const details=document.createElement('details');details.className='patch-array';details.open=false;
      const summary=document.createElement('summary');details.append(summary);wrap.append(details);caption.hidden=true;
      const list=document.createElement('div');details.append(list);const rows=[];
      const count=()=>summary.textContent=`${label} · ${rows.length} ${rows.length===1?'item':'items'}`;
      const add=value=>{const row=field(schema.items,value,'Item '+(rows.length+1),depth+1),container=document.createElement('div');container.className='patch-array-item';const remove=document.createElement('button');remove.type='button';remove.className='quiet-button';remove.textContent='Remove';remove.onclick=()=>{rows.splice(rows.indexOf(row),1);container.remove();count();};container.append(row.el,remove);list.append(container);rows.push(row);count();};
      for(const v of (Array.isArray(value)?value:[]))add(v);count();
      const button=document.createElement('button');button.type='button';button.className='secondary-button';button.textContent='Add item';button.onclick=()=>add(empty(schema.items));details.append(button);
      return {el:wrap,read:()=>rows.map(r=>r.read())};
    }
    let input;
    if(schema.enum){input=document.createElement('select');schema.enum.forEach(v=>{const o=document.createElement('option');o.value=JSON.stringify(v);o.textContent=String(v);input.append(o);});input.value=JSON.stringify(value);}
    else if(schema.type==='boolean'){input=document.createElement('input');input.type='checkbox';input.checked=Boolean(value);}
    else if(['integer','number'].includes(schema.type)){input=document.createElement('input');input.type='number';input.step=schema.type==='integer'?'1':'any';if(schema.minimum!==undefined)input.min=schema.minimum;if(schema.maximum!==undefined)input.max=schema.maximum;input.value=value??'';}
    else{const complex=typeof value==='object'&&value!==null;input=document.createElement(complex||String(value??'').includes('\n')||String(value??'').length>180?'textarea':'input');input.value=complex?JSON.stringify(value,null,2):value??'';if(input.tagName==='TEXTAREA'){input.rows=String(input.value).includes('\n')?7:2;input.spellcheck=false;}}
    input.id=id;wrap.append(input);
    return {el:wrap,read:()=>{if(schema.enum)return JSON.parse(input.value);if(schema.type==='boolean')return input.checked;if(['integer','number'].includes(schema.type)){if(!input.value.trim())throw Error(label+' is required.');return Number(input.value);}if(['object','array'].includes(schema.type))return JSON.parse(input.value);return input.value;}};
  }
  async function show(id){
    const token=++generation;shell('Action');setRoute({type:'actions',id,projectId:null});$('library-view').innerHTML='<p class="field-note">Opening action…</p>';
    try{const detail=await api('/api/actions/'+encodeURIComponent(id));if(token!==generation||getRoute().id!==id)return;current=detail;pending=null;draw(detail);}catch(e){toast(e.message);if(token===generation)open();}
  }
  function draw(detail){
    const m=detail.manifest,source=detail.input_source||{};
    $('library-view').innerHTML=`<button class="text-button" data-local="list">← All actions</button><div class="view-heading"><h1>${esc(m.title)}</h1></div><p class="view-description">${esc(m.description.split(/(?<=\.)\s/)[0])}</p><div class="patch-meta"><span>v${detail.version}</span><span>${detail.tests_passed} tests passed</span><span>No AI needed</span></div><p class="field-note">${source.kind==='previous_run'?'Inputs from a previous successful run. Review them before running again.':'Example inputs from a saved test case. Replace them with your data.'}</p>${getBrowser().origin==='https://event.workspace.demo'&&['participants','rooms','workshops'].every(k=>m.input_schema.properties?.[k])?'<button class="secondary-button" id="patch-app-input">Use current Fieldwork data</button>':''}<form id="patch-form"><div id="patch-fields"></div><div class="patch-footer"><button class="primary-button" id="patch-run" type="submit">${icon('reuse')}Preview result</button><label class="secondary-button patch-import">Import inputs<input id="patch-import" type="file" accept=".json,.csv,text/csv,application/json" hidden></label><span class="field-note">Runs locally. No application changes.</span></div></form><section id="patch-result" class="patch-result" hidden aria-live="polite"></section><details class="detail-section"><summary>About this action</summary><p class="description">${esc(m.description)}</p><p class="field-note">This form comes from the skill’s declared interface. Its code runs in the existing isolated sandbox with compute permission only. Tests cover saved cases, not every possible input.</p><div class="detail-actions"><button class="quiet-button" data-action="skill" data-id="${esc(m.id)}">Skill, source &amp; tests</button>${detail.provenance?.run_id?`<button class="quiet-button" data-action="source-run" data-id="${esc(detail.provenance.run_id)}">Original task</button>`:''}</div></details>`;
    if($('patch-app-input'))$('patch-app-input').onclick=async()=>{try{const context=await api('/api/actions/'+encodeURIComponent(m.id)+'/context');draw({...detail,input:context.input,app_context:context.app_context,input_source:{kind:'application'}});$('library-view').querySelector('.patch-meta + .field-note').textContent='Current Fieldwork data, revision '+context.revision+'. Preview before applying changes.';}catch(e){toast(e.message);}};
    const editor=field(m.input_schema,detail.input??empty(m.input_schema),'Inputs');$('patch-fields').append(editor.el);
    $('patch-import').onchange=async e=>{const f=e.target.files[0];if(!f)return;try{if(f.size>120000)throw Error('Keep inputs under 120 KB.');const text=await f.text();let input;if(f.name.toLowerCase().endsWith('.csv')){const keys=Object.entries(m.input_schema.properties||{}).filter(([k,s])=>s.type==='string'&&k.includes('csv'));if(keys.length!==1)throw Error('This action has no single CSV input. Import JSON instead.');input=editor.read();input[keys[0][0]]=text;}else input=JSON.parse(text);draw({...detail,input,app_context:null,input_source:{kind:'import'}});$('library-view').querySelector('.patch-meta + .field-note').textContent='Inputs imported from '+f.name+'. Review them before running.';}catch(e){toast(e.message);}};
    $('patch-form').onsubmit=async e=>{e.preventDefault();const button=$('patch-run');button.disabled=true;button.textContent='Running locally…';try{const run=await api('/api/actions/run',{id:m.id,version:detail.version,code_hash:detail.code_hash,project_id:detail.project_id,input:editor.read(),...(detail.app_context?{app_context:detail.app_context}:{})});pending=run.id;result(run);await refresh();}catch(e){toast(e.message);button.disabled=false;button.textContent='Preview result';}};
  }
  function preview(value,inputs={}){
    if(Array.isArray(value)&&value.length&&value.every(r=>r&&typeof r==='object'&&Object.hasOwn(r,'participant_id')&&Object.hasOwn(r,'workshop_id'))){const people=new Map((inputs.participants||[]).map(p=>[p.id,p.name])),workshops=new Map((inputs.workshops||[]).map(w=>[w.id,w.name]));return `<div class="patch-table"><table><thead><tr><th>Participant</th><th>Workshop</th></tr></thead><tbody>${value.slice(0,100).map(r=>`<tr><td>${esc(people.get(r.participant_id)||r.participant_id)}</td><td>${esc(workshops.get(r.workshop_id)||r.workshop_id)}</td></tr>`).join('')}</tbody></table></div>${value.length>100?'<p class="field-note">First 100 rows shown. Download the full result below.</p>':''}`;}
    if(Array.isArray(value)){if(value.length&&typeof value[0]==='object'&&value[0]!==null){const keys=[...new Set(value.flatMap(r=>Object.keys(r||{})))];return `<div class="patch-table"><table><thead><tr>${keys.map(k=>`<th>${esc(title(k))}</th>`).join('')}</tr></thead><tbody>${value.slice(0,100).map(r=>`<tr>${keys.map(k=>`<td>${esc(typeof r[k]==='object'?JSON.stringify(r[k]):r[k])}</td>`).join('')}</tr>`).join('')}</tbody></table></div>${value.length>100?'<p class="field-note">First 100 rows shown. Download the full result below.</p>':''}`;}return `<p class="patch-values">${value.length?value.map(v=>esc(typeof v==='object'?JSON.stringify(v):v)).join(', '):'None'}</p>`;}
    if(value&&typeof value==='object')return Object.entries(value).map(([k,v])=>`<section class="patch-output-section"><h3>${esc(title(k))}${Array.isArray(v)?` <span>${v.length}</span>`:''}</h3>${preview(v,inputs)}</section>`).join('');
    return `<pre class="patch-value">${esc(value)}</pre>`;
  }
  function result(run){
    const host=$('patch-result');if(!host)return;host.hidden=false;
    if(['queued','running'].includes(run.status)){host.innerHTML='<p>Running saved code in the local sandbox…</p>';return;}
    $('patch-run').disabled=false;$('patch-run').innerHTML=icon('reuse')+'Preview result';
    if(run.status!=='completed'){const error=String(run.error||run.status),brief=error.trim().match(/(?:ValueError|TypeError|KeyError|RuntimeError):\s*([^\n]+)$/)?.[1]||error;host.innerHTML=`<h2>Action stopped</h2><p>${esc(brief)}</p>${brief!==error?`<details class="detail-section"><summary>Technical details</summary><pre class="patch-value">${esc(error)}</pre></details>`:''}`;return;}
    host.innerHTML=`<div class="patch-result-heading"><h2>Your result</h2><span class="sample-tag">${run.model_calls} AI calls · ${run.duration_seconds}s</span></div>${run.ai_paused?'<p class="blackout-proof">Completed while Blackout was on.</p>':''}<p class="field-note">${run.application_apply?.status==='completed'?'Applied and verified in Fieldwork.':run.application_apply?'Apply needs review. Inspect Fieldwork before continuing.':'Preview only. No external application was changed.'}</p>${preview(run.result,run.input)}${run.result?.cleaned_csv?'<p class="field-note">Replacing the Fieldwork roster clears its current seat assignments. Your preview stays available here.</p>':''}<div class="detail-actions">${!run.application_apply&&getBrowser().origin==='https://event.workspace.demo'&&((run.result?.assignments&&run.result?.waitlist&&run.input?.participants?.length>0&&['participants','rooms','workshops'].every(k=>run.input?.[k]))||(run.result?.cleaned_csv&&run.result?.participants))?`<button class="primary-button" data-local="apply" data-id="${esc(run.id)}">${run.result?.cleaned_csv?'Replace Fieldwork roster':'Apply to Fieldwork'}</button>`:''}${(run.artifacts||[]).map(f=>`<a class="primary-button" href="/api/files/${esc(f.id)}" download>Download ${esc(f.name||'result')}</a>`).join('')}<button class="secondary-button" data-local="run-details" data-id="${esc(run.id)}">View run &amp; evidence</button></div>`;
  }
  function sync(){
    const paused=!!getState().ai_paused;const toggle=$('blackout-toggle');toggle.setAttribute('aria-pressed',String(paused));toggle.textContent=paused?'Blackout on':'Blackout';toggle.disabled=!!getState().busy;
    $('blackout-notice').hidden=!paused;
    document.querySelectorAll('[data-local="blackout"]').forEach(b=>{b.textContent=paused?'Resume AI':'Pause AI';b.setAttribute('aria-pressed',String(paused));b.disabled=!!getState().busy;});
    if(pending&&getRoute().type==='actions'&&getRoute().id===current?.manifest.id){const run=getState().runs.find(r=>r.id===pending);if(run){result(run);if(!['queued','running'].includes(run.status))pending=null;}}
  }
  async function blackout(){try{await api('/api/blackout',{paused:!getState().ai_paused});await refresh();toast(getState().ai_paused?'Blackout on. Saved actions still run.':'AI resumed.');}catch(e){toast(e.message);}}
  async function apply(id){const b=document.querySelector('[data-local=apply]');if(b){b.disabled=true;b.textContent='Applying…';}try{const run=await api('/api/actions/apply',{run_id:id});result(run);await refresh();toast('Applied and verified in Fieldwork. No AI calls.');}catch(e){toast(e.message);try{result(await api('/api/runs/'+encodeURIComponent(id)));}catch{if(b){b.disabled=false;b.textContent='Apply to Fieldwork';}}}}
  document.addEventListener('click',e=>{const b=e.target.closest('[data-local]');if(!b)return;({list:open,open:()=>show(b.dataset.id),blackout,apply:()=>apply(b.dataset.id),'run-details':()=>sourceRun(b.dataset.id)})[b.dataset.local]?.();});
  $('blackout-toggle').onclick=blackout;
  $('nav-actions').onclick=open;
  return {open,show,render,sync,eligible};
}
