const $ = id => document.getElementById(id);
let state = null, selected = null, selectedResult = null, eventSignature = '', runSignature = '';
const labels = {queued:'VE FRONTĚ',running:'PRACUJE',completed:'DOKONČENO',failed:'ZASTAVENO',interrupted:'PŘERUŠENO'};
function node(tag, text, className) { const el=document.createElement(tag); if(text!==undefined)el.textContent=text; if(className)el.className=className; return el; }
function notice(message) { $('notice').textContent=message || ''; $('notice').hidden=!message; }
async function api(path, body) {
  const response=await fetch(path, body===undefined ? {} : {method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const result=await response.json(); if(!response.ok)throw new Error(result.error || 'Požadavek selhal.'); return result;
}
function dataValue(text) { if(!text.trim())return null; try{return JSON.parse(text);}catch{return {text};} }
function showTab(name) { for(const tab of ['work','skills']){$(`${tab}-view`).hidden=tab!==name;$(`${tab}-tab`).classList.toggle('active',tab===name);$(`${tab}-tab`).setAttribute('aria-pressed',String(tab===name));} }
$('work-tab').onclick=()=>showTab('work'); $('skills-tab').onclick=()=>showTab('skills');
$('fresh-session').onclick=()=>{selected=null;selectedResult=null;eventSignature='';runSignature='';$('task').value='';$('input-data').value='';notice('Nová session zachová naučené postupy, ale nepřevezme předchozí konverzaci.');renderRun();$('task').focus();};
$('example').onclick=()=>{
  $('task').value='Očisti seznam registrací: sjednoť emaily na malá písmena, odstraň okolní mezery a duplicitní registrace stejného emailu na stejný workshop (zachovej první záznam). Vrať čistý seznam a počet odstraněných duplicit.';
  $('input-data').value=JSON.stringify({source:'Syntetická ukázková data, žádní skuteční účastníci',registrations:[{name:'Anna',email:' ANNA@example.test ',workshop:'Design'},{name:'Boris',email:'boris@example.test',workshop:'AI'},{name:'Anna',email:'anna@example.test',workshop:'Design'}]},null,2);
  notice('Ukázková data. Úkol proběhne skutečně přes Gemini; žádné schopnosti nejsou předem vložené.');
};
$('file-input').onchange=async event=>{const file=event.target.files[0];if(!file)return;if(file.size>30000){notice('Pro první prototyp přidej textový soubor do 30 KB.');return;}$('input-data').value=await file.text();notice(`Přidáno: ${file.name}. Obsah se odešle Gemini při spuštění úkolu.`);};
$('task-form').onsubmit=async event=>{event.preventDefault();notice('');$('submit').disabled=true;try{const run=await api('/api/run',{task:$('task').value,input:dataValue($('input-data').value)});selected=run.id;eventSignature='';runSignature='';await refresh();}catch(error){notice(error.message);}finally{$('submit').disabled=!!state?.busy;}};
$('correction-form').onsubmit=async event=>{event.preventDefault();notice('');$('correct-submit').disabled=true;try{const input={capability:$('capability').value};if($('case-input').value.trim()||$('case-expected').value.trim()){input.case={name:'Příklad od uživatele',input:JSON.parse($('case-input').value),expected:JSON.parse($('case-expected').value)};}const run=await api('/api/correct',{task:$('correction').value,input});selected=run.id;eventSignature='';runSignature='';await refresh();}catch(error){notice(error instanceof SyntaxError?'Vlastní ověřovací příklad musí mít platný JSON vstup i výstup.':error.message);}finally{$('correct-submit').disabled=!!state?.busy;}};
const fieldNames={cleaned_registrations:'Očištěné registrace',removed_duplicates_count:'Odstraněné duplicity',workshop_summary:'Přehled workshopů',name:'Jméno',email:'Email',workshop:'Workshop',seats:'Místa',capacity:'Kapacita',ordered_seats:'Rezervovaná místa',overloaded:'Překročeno'};
function fieldName(key){return fieldNames[key]||key.replaceAll('_',' ');}
function renderValue(value, parent, depth=0) {
  if(Array.isArray(value)&&value.length&&value.every(x=>x&&typeof x==='object'&&!Array.isArray(x))){
    const table=node('table'),head=node('tr'),cols=[...new Set(value.flatMap(x=>Object.keys(x)))];
    cols.forEach(col=>head.append(node('th',fieldName(col))));const thead=node('thead');thead.append(head);table.append(thead);const body=node('tbody');
    for(const row of value){const tr=node('tr');cols.forEach(col=>tr.append(node('td',typeof row[col]==='object'?JSON.stringify(row[col]):String(row[col]??''))));body.append(tr);}table.append(body);parent.append(table);
  }else if(value&&typeof value==='object'&&!Array.isArray(value)&&depth<2){
    for(const [key,item] of Object.entries(value)){const section=node('section',undefined,'data-group');section.append(node('h3',fieldName(key)));renderValue(item,section,depth+1);parent.append(section);}
  }else if(value===null||typeof value!=='object')parent.append(node('p',typeof value==='boolean'?(value?'Ano':'Ne'):String(value??'—'),'data-value'));
  else parent.append(node('pre',JSON.stringify(value,null,2)));
}
function renderHistory(){const history=$('history');history.replaceChildren();if(!state.runs.length){history.append(node('p','Tady se objeví dokončená práce.','muted'));return;}for(const run of state.runs){const button=node('button',run.task);button.className=run.id===selected?'selected':'';button.append(node('small',`${labels[run.status]} · ${new Date(run.created_at*1000).toLocaleTimeString('cs',{hour:'2-digit',minute:'2-digit'})}`));button.onclick=()=>{selected=run.id;eventSignature='';runSignature='';showTab('work');renderRun();renderHistory();};history.append(button);}}
function renderRun(){const run=state?.runs.find(x=>x.id===selected);const signature=JSON.stringify(run);if(signature===runSignature)return;runSignature=signature;
  $('run-status').textContent=run?labels[run.status]:'ČEKÁ NA ZADÁNÍ';$('run-status').className=`badge ${run?.status||''}`;
  $('result-empty').hidden=!!run&&run.status==='completed';$('result-content').hidden=!run||run.status!=='completed';
  $('correction-form').hidden=!run||run.status!=='completed'||!state.registry.length;
  if(run?.status==='completed'){selectedResult=run.result;$('result-message').textContent=run.message||'Hotovo.';$('result-value').replaceChildren();renderValue(run.result,$('result-value'));}
  if(run?.status==='failed'||run?.status==='interrupted')notice(run.error);
  if(run){loadEvents(run.id);$('run-metrics').hidden=!run.duration_ms;$('run-metrics').textContent=`${(run.duration_ms/1000).toFixed(1)} s · ${run.model_calls} volání modelu · ${run.tokens} tokenů`;}else{$('activity').replaceChildren(node('li','Skutečné kroky, testy a použité postupy — jakmile spustíš úkol.','activity-empty'));$('activity-count').textContent='0 kroků';$('run-metrics').hidden=true;}
}
async function loadEvents(id){try{const events=await api(`/api/events/${id}`);if(selected!==id)return;const signature=JSON.stringify(events);if(signature===eventSignature)return;eventSignature=signature;$('activity').replaceChildren();$('activity-count').textContent=`${events.length} kroků`;
  for(const event of events){const li=node('li');li.className=['error','tests_failed'].includes(event.kind)?'bad':['installed','tests_passed','finished'].includes(event.kind)?'good':'';li.append(node('time',new Date(event.at*1000).toLocaleTimeString('cs')),node('div',event.message));
    if(event.tests){for(const test of event.tests)li.append(node('div',`${test.passed?'✓':'×'} ${test.name}`,`test ${test.passed?'pass':'fail'}`));}
    const details=node('details');details.append(node('summary','Zobrazit důkazy'),node('pre',JSON.stringify(event,null,2)));li.append(details);$('activity').append(li);
  }
}catch(error){notice(error.message);}}
let registrySignature='';
function renderSkills(){const signature=JSON.stringify(state.registry);if(signature===registrySignature)return;registrySignature=signature;$('skill-count').textContent=state.registry.length;
  const current=$('capability').value;$('capability').replaceChildren();$('skills-list').replaceChildren();
  if(!state.registry.length)$('skills-list').append(node('div','Zatím žádné naučené postupy. První vznikne teprve z potřeby skutečného úkolu.','empty'));
  for(const record of state.registry){const m=record.manifest;const option=node('option',`${m.title} · v${record.version}`);option.value=m.id;$('capability').append(option);
    const card=node('article',undefined,'skill-card');card.append(node('h2',m.title),node('p',m.description));card.append(node('div',`v${record.version} · ${record.tests.length} testů prošlo · pouze výpočet nad daty`,'skill-meta'));
    const details=node('details');details.append(node('summary','Původ, rozhraní a testy'),node('pre',JSON.stringify(record,null,2)));card.append(details);
    const button=node('button','Deaktivovat','quiet');button.disabled=state.busy;button.onclick=async()=>{try{await api('/api/deactivate',{id:m.id});await refresh();}catch(error){notice(error.message);showTab('work');}};card.append(button);$('skills-list').append(card);
  }
  if([...$('capability').options].some(x=>x.value===current))$('capability').value=current;
}
$('download-result').onclick=()=>{const url=URL.createObjectURL(new Blob([JSON.stringify(selectedResult,null,2)],{type:'application/json'}));const a=node('a');a.href=url;a.download='vysledek.json';a.click();setTimeout(()=>URL.revokeObjectURL(url),1000);};
async function refresh(){try{state=await api('/api/state');$('connection').textContent=state.model_ready?`${state.model} · Free projekt`:'Model není připraven';$('limits').textContent=`Limit ${state.limits.calls} volání / ${state.limits.seconds} s. Postupy zůstávají, konverzace začíná znovu.`;$('submit').disabled=state.busy||!state.model_ready;$('correct-submit').disabled=state.busy||!state.model_ready;if(!state.model_ready)notice(state.model_status);renderHistory();renderSkills();renderRun();if(selected&&state.busy)await loadEvents(selected);}catch(error){$('connection').textContent='Server není dostupný';notice(error.message);}}
refresh();setInterval(refresh,1500);
