import { createLocalActions } from './local-actions.js';
import { createOperations } from './operations.js';
import { reconcile } from './workspace-sync.js';
import { createInsights } from './insights.js';
import { mountChatGPTSettings } from './chatgpt-settings.js';
import { createInteractions, withButtonFeedback } from './interactions.js';
import { updateLivePanel } from './live-panel.js';
const interactions = createInteractions();
const $ = id => document.getElementById(id);
const esc = value => String(value ?? '').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let iconSource='/design/icons/nucleo-pixel/sprite.svg';
const icon = name => `<svg class="icon" aria-hidden="true"><use href="${iconSource}#nucleo-${name}"></use></svg>`;
const logo = '<img src="/design/logo/pixel-ghost.svg" width="24" height="24" alt="">';
let data={projects:[],chats:[],workflows:[]}, state={runs:[],registry:[],versions:[],busy:false}, browser={connected:false};
let route={type:'chat',id:null,projectId:null}, context=null, files=[], connected=false, submitting=false, saving=Promise.resolve(), pollTimer, toastTimer;
let workspaceBase={projects:[],chats:[],workflows:[]}, workspaceSaves=0;
const drafts=new Map(), events=new Map(), runCache=new Map();
const expandedProjects=new Set();
let recentExpanded=false;
const projectById=id=>data.projects.find(p=>p.id===id);
const chatById=id=>data.chats.find(c=>c.id===id);
const runById=id=>state.runs.find(r=>r.id===id)||runCache.get(id);
const skillById=id=>state.registry.find(s=>s.manifest.id===id)||state.versions.filter(s=>s.manifest.id===id).at(-1);
const busyRun=()=>state.runs.find(r=>['running','queued'].includes(r.status));
const textJSON=value=>typeof value==='string'?value:JSON.stringify(value,null,2);
async function api(path,body) {
  const res=await fetch(path,body===undefined?{cache:'no-store'}:{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  const json=await res.json(); if(!res.ok){const error=Error(json.error||'The request failed.');error.conflict=json.conflict;throw error;}return json;
}
function toast(text){$('toast').textContent=text;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,6500);}
async function persist(){
  workspaceSaves++;
  saving=saving.catch(()=>{}).then(async()=>{
    const snapshot=structuredClone(data),base=structuredClone(workspaceBase);
    try{localStorage.setItem('learning-workspace.live.backup',JSON.stringify(snapshot));}catch{}
    const remote=await api('/api/workspace',{base,value:snapshot});
    data=reconcile(snapshot,data,remote);workspaceBase=structuredClone(remote);renderSidebar();
  });
  try{await saving;return true;}catch(error){
    toast('Could not save: '+error.message);
    if(error.conflict){inspector('Save conflict',`<h2>This item changed in another tab.</h2><p class="description">Your edits are still in this tab. Export them before loading the latest saved workspace.</p><div class="detail-actions"><button class="secondary-button" id="export-unsaved">Export my edits</button><button class="primary-button" id="load-latest">Load latest</button></div>`);$('export-unsaved').onclick=()=>download(data,'unsaved-workspace.json');$('load-latest').onclick=async()=>{data=await api('/api/workspace');workspaceBase=structuredClone(data);closeInspector();renderSidebar();renderLibrary();};}
    return false;
  }finally{workspaceSaves--;}
}
function draftKey(){return route.id||`new:${route.projectId||'personal'}`;}
function rememberDraft(){if(route.type==='chat')drafts.set(draftKey(),{text:$('message').value,context,files:[...files],browser:$('use-browser').checked,desktop:$('use-desktop').checked});}
function restoreDraft(){const d=drafts.get(draftKey());$('message').value=d?.text||'';context=d?.context||null;files=d?.files||[];$('use-browser').checked=Boolean(d?.browser&&browser.connected);$('use-desktop').checked=Boolean(d?.desktop&&operations.desktopState().connected);updateComposer();}
function leave(){rememberDraft();closeInspector();}
function navChat(chat,nested){return `<button class="chat-link ${nested?'':'recent-chat'} ${route.type==='chat'&&route.id===chat.id?'active':''}" data-action="chat" data-id="${esc(chat.id)}" title="${esc(chat.title)}"><span>${esc(chat.title)}</span>${(chat.runIds||[]).some(id=>['running','queued'].includes(runById(id)?.status))?'<i class="connection-dot"></i>':''}</button>`;}
function renderSidebar(){
  $('project-list').innerHTML=data.projects.map(p=>{
    const chats=data.chats.filter(c=>c.projectId===p.id).slice().reverse(),expanded=expandedProjects.has(p.id);
    return `<div class="project-nav"><div class="project-nav-heading"><button class="nav-row project-row ${route.type==='project'&&route.id===p.id?'active':''}" data-action="project" data-id="${esc(p.id)}">${icon('folder-open')}<span>${esc(p.name)}</span></button><button class="project-expand" data-action="toggle-project" data-id="${esc(p.id)}" aria-label="${expanded?'Collapse':'Expand'} ${esc(p.name)} chats" aria-expanded="${expanded}" aria-controls="project-chats-${esc(p.id)}"><span aria-hidden="true">${expanded?'−':'+'}</span></button></div><div id="project-chats-${esc(p.id)}" ${expanded?'':'hidden'}>${chats.slice(0,4).map(c=>navChat(c,true)).join('')}${chats.length>4?`<button class="sidebar-more" data-action="project" data-id="${esc(p.id)}">View all ${chats.length} chats</button>`:''}</div></div>`;
  }).join('')||'<p class="sidebar-empty">Group related tasks here.</p>';
  const recent=data.chats.filter(c=>!c.projectId).slice().reverse();
  $('recent-list').innerHTML=recent.slice(0,recentExpanded?recent.length:5).map(c=>navChat(c,false)).join('')+(recent.length>5?`<button class="sidebar-more" data-action="toggle-recent">${recentExpanded?'Show less':'Show all chats'}</button>`:'')||'<p class="sidebar-empty">Your chats will appear here.</p>';
  const library=['actions','skills','workflows','schedules'].includes(route.type);
  $('library-navigation').hidden=!library;$('nav-library').classList.toggle('active',library);
  for(const name of ['actions','skills','workflows','computer','overview','guide','schedules']){
    const button=$(`nav-${name}`),active=route.type===name;button.classList.toggle('active',active);
    if(active)button.setAttribute('aria-current','page');else button.removeAttribute('aria-current');
  }
  $('new-chat').classList.toggle('active',route.type==='chat'&&!route.id&&!route.projectId);
  interactions.syncNavigation();
}
function header(title,projectId){const p=projectById(projectId);$('breadcrumb-page').textContent=title;$('breadcrumb-project').textContent=p?.name||'';$('breadcrumb-project').hidden=!p;$('context-button').hidden=!p;$('context-button').dataset.projectId=projectId||'';document.title=title+' · Wisp';}
function showView(name){if(matchMedia('(max-width:760px)').matches)setSidebar(false);for(const v of ['chat','library','project'])$(`${v}-view`).hidden=v!==name;interactions.enterView($(`${name}-view`));}
async function openChat(id=null,projectId=null){
  leave();const chat=chatById(id);route={type:'chat',id:chat?.id||null,projectId:chat?.projectId||projectId};if(route.projectId)expandedProjects.add(route.projectId);showView('chat');header(chat?.title||'New chat',route.projectId);renderSidebar();restoreDraft();renderChat();
  for(const runId of chat?.runIds||[]){if(!runById(runId)){try{runCache.set(runId,await api('/api/runs/'+encodeURIComponent(runId)));}catch{}}if(!events.has(runId))try{events.set(runId,await api('/api/events/'+encodeURIComponent(runId)));}catch{}}
  if(route.id===id)renderChat();
}
function newChat(projectId=null){openChat(null,projectId);$('message').focus();}
function userMessage(text,attachments=[]){return `<div class="message user">${esc(text)}${attachments.length?`<div class="attachments">${attachments.map(f=>`<span class="attachment">${icon('file')}${esc(f.name)}</span>`).join('')}</div>`:''}</div>`;}
function assistant(content){return `<div class="message assistant"><div class="message-label">${logo}Wisp</div>${content}</div>`;}
function activity(run){
  const logs=events.get(run.id)||[];
  if(!logs.length)return run.status==='running'?'<p class="progress-caption">Starting the task…</p>':'';
  const last=logs.at(-1);const active=['running','queued'].includes(run.status);
  return `<details class="activity" data-log="${esc(run.id)}"><summary>${icon(active?'loader':run.status==='completed'?'check':'triangle-warning')}<span>${esc(active?last.message:`${logs.length} steps · ${run.status}`)}</span></summary><ol>${logs.map(log=>`<li>${icon(log.kind==='error'||log.kind==='tests_failed'?'triangle-warning':log.kind==='browser_step'?'layers':'check')}<span>${esc(log.message)}${log.tests?`<small>${log.tests.filter(t=>t.passed).length}/${log.tests.length} checks passed</small>`:''}</span></li>`).join('')}</ol><button class="text-button" data-action="evidence" data-id="${esc(run.id)}">${icon('clipboard-check')}View evidence</button></details>`;
}
function resultCard(run){
  const count=run.artifacts?.length||0;
  return `<button class="result-card" data-action="result" data-id="${esc(run.id)}"><span class="result-icon">${icon('file')}</span><span><strong>${run.kind==='correction'?'Review skill update':'View result'}</strong><small>${count?`${count} file${count===1?'':'s'} ready · `:''}${Math.round((run.duration_ms||0)/1000)}s</small></span><span class="result-open">Open</span></button>`;
}
function taskMore(run,used){return `<details class="task-more" data-disclosure="more-${esc(run.id)}"><summary>More options</summary><div class="task-more-actions">${run.status==='completed'?`<button class="text-button" data-action="save-workflow" data-id="${esc(run.id)}">${icon('reuse')}Save as workflow</button>${used.length?`<button class="text-button" data-action="improve-run" data-id="${esc(run.id)}">${icon('book-magic-skill')}Improve a skill</button>`:''}`:''}<button class="text-button" data-action="usage" data-id="${esc(run.id)}">${icon('clipboard-check')}Usage &amp; cost</button><button class="text-button" data-action="evidence" data-id="${esc(run.id)}">${icon('file')}Execution details</button>${run.mode==='desktop'?`<button class="text-button" data-op="show-desktop">${icon('layers')}View application</button>`:''}${run.mode==='browser'?`<button class="text-button" data-action="browser-preview">${icon('layers')}View browser</button>`:''}</div></details>`;}
function renderChat(){
  if(route.type!=='chat')return;
  const chat=chatById(route.id), runs=(chat?.runIds||[]).map(runById).filter(Boolean);
  const empty=!chat||(!runs.length&&!chat.draftText);
  $('chat-view').classList.toggle('is-empty',empty);$('welcome').hidden=!empty;$('starter-actions').hidden=!empty;
  $('composer-project').hidden=!route.projectId;$('composer-project').textContent=projectById(route.projectId)?.name||'';
  const scroll=$('chat-scroll'),atBottom=scroll.scrollHeight-scroll.scrollTop-scroll.clientHeight<90;
  const opened=new Set([...$('conversation').querySelectorAll('details[open]')].map(d=>d.dataset.log||d.dataset.disclosure));
  let html=chat?.draftText?`<p class="example-note">Imported design draft. This message has not been executed.</p>${userMessage(chat.draftText)}`:'';
  html+=runs.map(run=>{
    const running=['running','queued'].includes(run.status),logs=events.get(run.id)||[];
    const used=[...new Set(logs.filter(e=>['installed','used'].includes(e.kind)).map(e=>e.capability).filter(Boolean))];
    let body;
    if(['needs_input','needs_review'].includes(run.status))body=`<p class="response-text">${esc(run.message)}</p>${run.status==='needs_review'?`<div class="message-actions"><button class="secondary-button" data-action="confirm-result" data-id="${esc(run.id)}">I checked the result</button></div>`:''}`;
    else if(running)body=`<p class="progress-caption">You can review the steps above or stop the task.</p><div class="message-actions">${run.mode==='browser'?`<button class="text-button" data-action="browser-preview">${icon('layers')}Watch browser</button>`:run.mode==='desktop'?`<button class="text-button" data-op="show-desktop">${icon('layers')}View application</button>`:''}</div>`;
    else if(run.status==='completed')body=`<p class="response-text">${esc(run.message||'Done.')}</p>${resultCard(run)}<div class="message-actions"><button class="text-button" data-action="follow-up" data-id="${esc(run.id)}">${icon('reuse')}Continue this task</button>${taskMore(run,used)}</div>`;
    else body=`<p class="run-error">${esc(run.error||'The task stopped before completion.')}</p><div class="message-actions"><button class="text-button" data-action="retry" data-id="${esc(run.id)}">${icon('reuse')}Try again</button>${taskMore(run,used)}</div>`;
    return userMessage(run.task,run.input?.files||[])+assistant(`${activity(run)}${body}${run.status==='needs_review'||run.status==='needs_input'?taskMore(run,used):''}`);
  }).join('');
  if(browser.pending&&runs.some(r=>r.id===busyRun()?.id))html+=approvalHTML();
  if(operations.desktopState().pending&&runs.some(r=>r.id===busyRun()?.id))html+=operations.approval();
  $('conversation').innerHTML=html;
  $('conversation').querySelectorAll('details').forEach(d=>d.open=opened.has(d.dataset.log||d.dataset.disclosure));
  if(atBottom)requestAnimationFrame(()=>scroll.scrollTop=scroll.scrollHeight);
}
function updateComposer(){
  $('send-message').disabled=!$('message').value.trim()||state.busy||submitting||!connected||state.ai_paused;
  if($('send-message').getAttribute('aria-busy')!==String(submitting)){
    $('send-message').setAttribute('aria-busy',String(submitting));
    $('send-message').setAttribute('aria-label',submitting?'Sending message':'Send message');
    $('send-message').innerHTML=icon(submitting?'loader':'paper-plane');
    $('send-message').querySelector('.icon').classList.toggle('button-loader',submitting);
  }
  $('message').rows=Math.min(6,Math.max(2,$('message').value.split('\n').length));
  $('message').placeholder=state.ai_paused?'AI is paused. Open Actions to run saved operations.':context?.type==='correction'?'Describe the behavior that should change':'Describe a task or ask a question';
  $('composer-context').hidden=!context;$('composer-context-text').textContent=context?.label||'';let testButton=$('add-correction-case');if(!testButton){testButton=document.createElement('button');testButton.id='add-correction-case';testButton.type='button';testButton.className='quiet-button';testButton.textContent='Test case';testButton.onclick=showCorrectionCase;$('composer-context').insertBefore(testButton,$('clear-composer-context'));}testButton.hidden=context?.type!=='correction';
  $('attachments').hidden=!files.length;$('attachments').innerHTML=files.map((f,i)=>`<span class="attachment">${icon('file')}<span>${esc(f.name)}</span><button type="button" data-action="remove-file" data-id="${i}" aria-label="Remove ${esc(f.name)}">${icon('xmark')}</button></span>`).join('');
  $('browser-toggle').hidden=!browser.connected;
  $('desktop-toggle').hidden=!operations.desktopState().connected;
  $('computer-dot').hidden=!browser.connected&&!operations.desktopState().connected;
  $('stop-run').hidden=!state.busy;
}
async function submit(event){
  event.preventDefault();const text=$('message').value.trim();if(!text||state.busy||submitting||!connected)return;
  submitting=true;updateComposer();
  try{
    let chat=chatById(route.id);
    if(!chat){chat={id:crypto.randomUUID(),title:text.slice(0,48),projectId:route.projectId,runIds:[]};data.chats.push(chat);drafts.delete(draftKey());route.id=chat.id;}
    if(!await persist())return;
    const input=context?.type==='correction'?{capability:context.id,...(context.case?{case:context.case}:{})}:{files:[...files],...(context?.type==='followup'?{previous_result:runById(context.id)?.result}:{}),...(context?.type==='skill'?{preferred_skill:context.id}:{}),...(context?.type==='workflow'?{workflow:context.id}: {})};
    const payload={task:text,input,project_id:context?.type==='correction'?(skillById(context.id)?.provenance?.project_id||null):route.projectId,chat_id:chat.id,use_desktop:operations.desktopState().connected&&$('use-desktop').checked,use_browser:browser.connected&&(context?.type==='correction'?skillById(context.id)?.manifest.kind==='browser_plan':$('use-browser').checked)};
    const run=await api(context?.type==='correction'?'/api/correct':'/api/run',payload);
    chat=chatById(chat.id);chat.runIds=[...new Set([...(chat.runIds||[]),run.id])];chat.draftText=null;state.runs.unshift(run);state.busy=true;await persist();
    context=null;files=[];drafts.delete(draftKey());$('message').value='';header(chat.title,chat.projectId);renderSidebar();renderChat();refresh();
  }catch(error){toast(error.message);}finally{submitting=false;updateComposer();}
}
function inspector(kind,html,wide=false){$('inspector-kind').textContent=kind;$('inspector-content').innerHTML=html;$('inspector').classList.toggle('browser-inspector',wide);$('inspector').hidden=false;$('inspector').dataset.kind=kind;}
function closeInspector(){$('inspector').hidden=true;$('inspector-content').innerHTML='';$('inspector').dataset.kind='';}
function valueHTML(value){
  if(Array.isArray(value)&&value.length&&value.every(v=>v&&typeof v==='object'&&!Array.isArray(v))){const columns=[...new Set(value.flatMap(v=>Object.keys(v)))].slice(0,8);return `<div class="result-table-wrap"><table class="result-table"><thead><tr>${columns.map(c=>`<th>${esc(c)}</th>`).join('')}</tr></thead><tbody>${value.map(row=>`<tr>${columns.map(c=>`<td>${esc(typeof row[c]==='object'?JSON.stringify(row[c]):row[c]??'')}</td>`).join('')}</tr>`).join('')}</tbody></table></div>`;}
  return `<pre class="result-json">${esc(textJSON(value))}</pre>`;
}
function resultContent(run){const r=run.result;if(r?.verified_constraints&&(run.permissions||[]).includes('browser:https://event.workspace.demo'))return `<div class="outcome-metrics"><div><strong>${r.participants}</strong><span>Attendees</span></div><div><strong>${r.assigned}</strong><span>Seats assigned</span></div><div><strong>${r.waitlist}</strong><span>Waiting list</span></div></div><details class="detail-section"><summary>Verification checks</summary><ul class="outcome-checks">${(r.checks||[]).map(check=>`<li>${icon('check')}<span>${esc(check)}</span></li>`).join('')}${r.unaffected_reservations_preserved?`<li>${icon('check')}<span>Reservations in unaffected workshops preserved</span></li>`:''}</ul><p class="field-note">These checks cover the listed constraints. They do not prove an optimal allocation.</p></details>`;return valueHTML(r);}
function showResult(id){
  const run=runById(id);if(!run)return;
  const used=[...new Set((events.get(id)||[]).filter(e=>['installed','used'].includes(e.kind)).map(e=>e.capability).filter(Boolean))];
  inspector('Result',`<span class="sample-tag">${esc(run.status)}</span><h2>${run.kind==='correction'?'Skill updated':'Task result'}</h2><p class="description">${esc(run.message||'')}</p>${resultContent(run)}${run.artifacts?.length?'<h3 class="result-files-heading">Files</h3>':''}${operations.artifactHTML(run)}<div class="detail-actions"><button class="primary-button" data-action="follow-up" data-id="${esc(id)}">Continue this task</button><button class="secondary-button" data-action="save-workflow" data-id="${esc(id)}">Save workflow</button></div>${used.length?`<details class="detail-section"><summary>${used.length} skill${used.length===1?'':'s'} used</summary>${used.map(skill=>`<p><button class="inline-link" data-action="skill" data-id="${esc(skill)}">${esc(skillById(skill)?.manifest.title||skill)}</button></p>`).join('')}</details>`:''}<details class="detail-section"><summary>Usage, checks &amp; export</summary><div class="task-more-actions"><button class="text-button" data-action="usage" data-id="${esc(id)}">Usage &amp; cost</button><button class="text-button" data-action="evidence" data-id="${esc(id)}">Execution details</button><button class="text-button" data-action="download-result" data-id="${esc(id)}">Download result data</button></div></details>`);
}
function showEvidence(id){const run=runById(id);if(!run)return;inspector('Evidence',`<button class="text-button" data-action="result" data-id="${esc(id)}">Back to result</button><h2>What actually ran</h2><dl class="detail-meta"><div><dt>State</dt><dd>${esc(run.status)}</dd></div><div><dt>Model calls</dt><dd>${run.model_calls||0}</dd></div><div><dt>Tokens</dt><dd>${run.tokens||0}</dd></div><div><dt>Duration</dt><dd>${Math.round((run.duration_ms||0)/1000)}s</dd></div><div><dt>Permissions</dt><dd>${esc((run.permissions||['compute']).join(', '))}</dd></div></dl><p class="field-note">Logs report real execution. Model-authored tests can still miss errors.</p>${(events.get(id)||[]).map(log=>`<section class="detail-section"><h3>${esc(log.kind)}</h3><p>${esc(log.message)}</p>${log.tests?log.tests.map(t=>`<details class="test-detail"><summary>${esc(t.name)} · ${t.passed?'Passed':'Failed'}</summary>${valueHTML(t)}</details>`).join(''):''}</section>`).join('')}<button class="secondary-button" data-action="download-evidence" data-id="${esc(id)}">Export evidence</button>`);}
function showSkill(id,version){
  const record=version?state.versions.find(s=>s.manifest.id===id&&s.version===Number(version)):skillById(id);if(!record)return;
  const m=record.manifest,active=state.registry.some(s=>s.manifest.id===id&&s.version===record.version),versions=state.versions.filter(s=>s.manifest.id===id);
  inspector('Skill',`<span class="sample-tag">${active?'Active':'Inactive'} · v${record.version}</span><h2>${esc(m.title)}</h2><p class="description">${esc(m.description)}</p><details class="detail-section"><summary>Origin &amp; permissions</summary><dl class="detail-meta"><div><dt>Scope</dt><dd>${esc(projectById(record.provenance?.project_id)?.name||'Shared')}</dd></div><div><dt>Permissions</dt><dd>${esc(m.permissions.join(', '))}</dd></div><div><dt>Created by</dt><dd>${esc(record.provenance?.source||'Unknown')}</dd></div><div><dt>Source</dt><dd><button class="inline-link" data-action="source-run" data-id="${esc(record.provenance?.run_id)}">Open task</button></dd></div></dl></details><details class="detail-section"><summary>Versions &amp; tests</summary><label for="skill-version">Version</label><select id="skill-version" data-skill="${esc(id)}">${versions.map(v=>`<option value="${v.version}" ${v.version===record.version?'selected':''}>Version ${v.version}</option>`).join('')}</select><section class="detail-section"><h3>${record.tests.filter(t=>t.passed).length}/${record.tests.length} tests passed</h3>${record.tests.map(t=>`<details class="test-detail"><summary>${esc(t.name)} · ${t.passed?'Passed':'Failed'}</summary>${valueHTML(t)}</details>`).join('')}<p class="field-note">Passing these cases is evidence, not a guarantee for every input.</p></section></details><details class="detail-section"><summary>Interface and source</summary>${valueHTML(m)}<pre class="result-json">${esc(record.code)}</pre></details><div class="detail-actions">${active?`${localActions.eligible(record)?`<button class="primary-button" data-local="open" data-id="${esc(id)}">Run locally</button>`:''}<button class="secondary-button" data-action="use-skill" data-id="${esc(id)}">Use in a chat</button><button class="secondary-button" data-action="correct-skill" data-id="${esc(id)}">Improve</button>`:`<button class="primary-button" data-action="activate-skill" data-id="${esc(id)}" data-version="${record.version}">Activate v${record.version}</button>`}</div>${active?`<button class="text-button danger-button" data-action="deactivate-skill" data-id="${esc(id)}">${icon('xmark')}Deactivate</button>`:''}<button class="text-button" data-action="export-skill" data-id="${esc(id)}" data-version="${record.version}">${icon('file')}Export this version</button>`);
}
function showCorrectionCase(){
  if(context?.type!=='correction')return;
  inspector('Regression case',`<h2>Define the expected result</h2><p class="description">Optional: provide one concrete case. It must expose the old behavior, then pass alongside every previous test.</p><label for="case-input">Input as JSON</label><textarea id="case-input">${esc(JSON.stringify(context.case?.input||{},null,2))}</textarea><label for="case-expected">Expected output as JSON</label><textarea id="case-expected">${esc(JSON.stringify(context.case?.expected||{},null,2))}</textarea><p class="field-note">New input fields are documented as optional parameters. Existing required inputs and permissions remain unchanged.</p><button class="primary-button" id="apply-correction-case">Use this case</button>`);
  $('apply-correction-case').onclick=()=>{try{context.case={name:'User-provided regression case',input:JSON.parse($('case-input').value),expected:JSON.parse($('case-expected').value)};closeInspector();toast('Regression case attached to your correction.');}catch{toast('Both fields must contain valid JSON.');}};
}
function correctSkill(id){const record=skillById(id);if(!record)return;if(record.manifest.kind==='browser_plan'&&(!browser.connected||browser.origin!==record.manifest.output_schema.properties.origin.const)){toast('Connect this skill’s target application before improving it.');openComputer();return;}newChat(record.provenance?.project_id||null);context={type:'correction',id,label:'Improve: '+record.manifest.title};updateComposer();$('message').focus();}
function improveRun(id){const ids=[...new Set((events.get(id)||[]).filter(e=>['used','installed'].includes(e.kind)).map(e=>e.capability).filter(Boolean))];if(ids.length===1){correctSkill(ids[0]);return;}inspector('Choose a skill',`<h2>What should improve?</h2><p class="description">Choose the skill that produced the behavior you want to change.</p>${ids.map(id=>`<button class="library-row" data-action="correct-skill" data-id="${esc(id)}">${icon('book-magic-skill')}<strong>${esc(skillById(id)?.manifest.title||id)}</strong></button>`).join('')}`);}
function openLibrary(type){leave();route={type,id:null,projectId:null};showView('library');header('Library');renderSidebar();renderLibrary();}
function renderLibrary(){
  if(route.type==='actions'){localActions.render();return;}
  if(!['skills','workflows'].includes(route.type))return;
  if(route.type==='skills'){
    const rows=new Map();state.versions.forEach(r=>rows.set(r.manifest.id,r));state.registry.forEach(r=>rows.set(r.manifest.id,r));
    $('library-view').innerHTML=`<div class="view-heading"><h1>Skills</h1><span class="sample-tag">${state.registry.length} active</span></div><p class="view-description">Operations the agent learned from your tasks. It finds and reuses them automatically.</p><label class="sr-only" for="library-filter">Find a skill</label><input class="filter-input" id="library-filter" placeholder="Find a skill" type="search"><div id="library-rows">${[...rows.values()].map(r=>`<button class="library-row" data-filter="${esc((r.manifest.title+' '+r.manifest.description).toLowerCase())}" data-action="skill" data-id="${esc(r.manifest.id)}">${icon('book-magic-skill')}<div><strong>${esc(r.manifest.title)}</strong><p>${esc(r.manifest.description)}</p></div><span class="row-end">v${r.version} · ${state.registry.some(s=>s.manifest.id===r.manifest.id)?'Active':'Inactive'}</span></button>`).join('')||`<div class="empty-state">${icon('book-magic-skill')}<h2>Skills start with real work.</h2><p>When a task needs a reusable operation, the agent can create it, test it and add it here.</p><button class="secondary-button" data-action="sample">Try a task</button></div>`}</div><p class="field-note" id="filter-empty" hidden>No skills match your search.</p>`;
  }else $('library-view').innerHTML=`<div class="view-heading"><h1>Saved workflows</h1></div><p class="view-description">Start again from successful work, with new inputs.</p>${data.workflows.map(w=>`<button class="library-row" data-action="workflow" data-id="${esc(w.id)}">${icon('reuse')}<div><strong>${esc(w.title)}</strong><p>${esc(projectById(w.projectId)?.name||'Personal workspace')}</p></div><span class="row-end">Open</span></button>`).join('')||`<div class="empty-state">${icon('reuse')}<h2>Keep what works.</h2><p>Save a workflow from a completed task. Reuse its instructions and attach fresh inputs next time.</p></div>`}`;
}
async function saveWorkflow(id){const run=runById(id);if(!run||run.status!=='completed')return;const existing=data.workflows.find(w=>w.sourceRun===id);if(existing){showWorkflow(existing.id);return;}data.workflows.push({id:crypto.randomUUID(),title:run.task.slice(0,60),prompt:run.task,sourceRun:id,projectId:run.project_id,mode:run.mode,skillIds:[...new Set((events.get(id)||[]).filter(e=>e.kind==='used').map(e=>e.capability))]});if(await persist()){toast('Saved in Library → Saved workflows.');showWorkflow(data.workflows.find(w=>w.sourceRun===id).id);}}
function showWorkflow(id){const w=data.workflows.find(w=>w.id===id);if(!w)return;inspector('Saved workflow',`<h2>${esc(w.title)}</h2><p class="description">${esc(w.prompt)}</p><section class="detail-section"><h3>Skills used in the original task</h3>${w.skillIds?.length?w.skillIds.map(id=>`<p><button class="inline-link" data-action="skill" data-id="${esc(id)}">${esc(skillById(id)?.manifest.title||id)}</button></p>`).join(''):'<p>No generated skill was used.</p>'}</section><p class="field-note">Run with fresh inputs, or schedule this workflow with the original attachments.</p><div class="detail-actions"><button class="primary-button" data-action="use-workflow" data-id="${esc(id)}">Use workflow</button><button class="secondary-button" data-action="schedule-workflow" data-id="${esc(id)}">Schedule</button><button class="quiet-button danger-button" data-action="delete-workflow" data-id="${esc(id)}">Remove</button></div><button class="text-button" data-action="source-run" data-id="${esc(w.sourceRun)}">Open original task</button>`);}
function openProject(id){const p=projectById(id);if(!p)return;leave();route={type:'project',id,projectId:id};showView('project');header(p.name);$('context-button').hidden=false;$('context-button').dataset.projectId=id;renderSidebar();const chats=data.chats.filter(c=>c.projectId===id);$('project-view').innerHTML=`<div class="view-heading"><h1>${esc(p.name)}</h1><button class="primary-button" data-action="new-project-chat" data-id="${esc(id)}">${icon('plus')}New chat</button></div><p class="view-description">Shared instructions, related tasks and scoped skills.</p><div class="project-context-row">${icon('sliders')}<div><h3>Project context</h3><p>${p.instructions?'Instructions apply to new tasks in this project.':'Add preferences and constraints for this work.'}</p></div><button class="quiet-button" data-action="project-context" data-id="${esc(id)}">Edit</button></div><div class="list-caption"><span>Chats</span><span>${chats.length}</span></div>${chats.map(c=>`<button class="library-row" data-action="chat" data-id="${esc(c.id)}">${icon('file')}<strong>${esc(c.title)}</strong></button>`).join('')||'<p class="field-note">Start a chat to begin.</p>'}`;}
function financialPolicyText(){const p=state.spend_policy;if(!p)return 'Financial policy unavailable.';if(!p.allowed)return p.error||'Model requests are blocked by the financial policy.';return p.policy==='strict'?`Strict model budget: $${p.max_usd} per task. Unpriced routes are blocked. Gemini billing must remain disabled in AI Studio.`:'ChatGPT plan mode: no local USD guarantee. Plan and credit limits are managed by the provider.';}
function showProjectContext(id){const p=projectById(id);if(!p)return;inspector('Project context',`<h2>${esc(p.name)}</h2><p class="description">These instructions apply to new tasks in this project.</p><label for="project-instructions">Instructions</label><textarea id="project-instructions" maxlength="4000" placeholder="Tone, constraints and preferences">${esc(p.instructions||'')}</textarea><p class="field-note">Saved locally on the server. They are included with this project’s tasks sent to the selected model provider.</p><button class="primary-button" data-action="save-context" data-id="${esc(id)}">Save instructions</button>`);}
function approvalHTML(){const pending=browser.pending;if(!pending)return '';return `<div class="approval-card"><h3>Review the browser action</h3><p>${esc(pending.reason)}</p><p class="field-note">${esc(pending.operation.action)} · ${esc(pending.operation.ref||'')}${pending.operation.value!==undefined?' · '+esc(String(pending.operation.value)):''}</p><button class="primary-button" data-action="approve">Allow this step</button><button class="quiet-button" data-action="decline">Decline</button></div>`;}
function browserImage(){return browser.screenshot?`<img class="browser-screenshot" src="data:image/jpeg;base64,${browser.screenshot}" alt="Current page in the connected browser">`:'';}
function browserDescription(){return `<div class="browser-address">${icon('shield-check')}<span>${esc(browser.url||'')}</span></div>${browserImage()}${approvalHTML()}<details class="detail-section" data-disclosure="page-map"><summary>Page map · ${browser.elements?.length||0} controls</summary><p class="field-note">Only this site is allowed. ${['https://workspace.demo','https://event.workspace.demo'].includes(browser.origin)?'Local showcase application.':'Interactions wait for your review.'}</p>${(browser.elements||[]).map(el=>`<div class="mapped-element"><code>${esc(el.ref)}</code><span>${esc(el.role||el.tag)} · ${esc(el.name||'(unnamed)')}</span></div>`).join('')}</details>`;}
function openComputer(){leave();route={type:'computer',id:null,projectId:null};showView('library');header('Computer');renderSidebar();renderComputer();}
function renderComputer(){
  if(route.type!=='computer')return;
  const demo=browser.origin==='https://event.workspace.demo';
  $('library-view').innerHTML=`<div class="view-heading"><h1>Computer</h1></div><p class="view-description">Choose the app your next task will use.</p><div class="connection-tabs"><button class="selected" aria-current="page" data-op="browser-tab">Web browser</button><button data-op="desktop-tab">Desktop application</button></div>
    ${browser.connected?`<div id="connection-approval">${approvalHTML()}</div><section class="connected-app"><div class="connected-app-heading">${icon('layers')}<div><span class="connection-caption">Connected</span><h2>${esc(browser.title||'Web browser')}</h2><p>${esc(browser.origin)}</p></div></div><div class="detail-actions"><button class="primary-button" data-action="browser-task">${icon('plus')}Start a task</button><button class="secondary-button" data-action="browser-preview">View browser</button></div><details class="connection-options"><summary>Connection options</summary><p class="field-note">Only this site is allowed. ${demo?'Local showcase using synthetic data.':'External interactions wait for your approval.'}</p><div class="detail-actions"><button class="quiet-button" data-action="refresh-browser">Refresh page map</button><button class="quiet-button" data-action="disconnect-browser">Disconnect browser</button></div></details></section>${demo?`<section class="next-task"><div><span class="connection-caption">Next in the showcase</span><h2>What if a room closes?</h2><p>After the first allocation, move a workshop and keep the other reservations intact.</p></div><button class="secondary-button" data-op="showcase-followup">Prepare room change</button></section>`:''}`:`<form id="connect-browser-form" class="connect-form"><label for="browser-url">Website</label><div><input id="browser-url" type="url" placeholder="https://example.com" required><button class="primary-button" type="submit">Connect browser</button></div><p class="field-note">Opens a separate Chrome window. You review changes before they happen.</p></form>`}
    ${!demo?`<section class="showcase-compact"><span class="connection-caption">Try it with sample data</span><h2>Run an event. Handle the unexpected.</h2><p>Import registrations, allocate workshops and replan when a room closes.</p><button class="secondary-button" data-action="practice">${icon('layers')}Open event operations</button><p class="field-note">A local demo app. The agent performs the work.</p></section>`:''}
    <section class="next-task"><h2>Your learned actions</h2><p>Run saved operations with new inputs and preview the result. No AI calls needed.</p><button class="secondary-button" data-local="list">Open actions</button></section><details class="detail-section remembered-apps"><summary>Previously connected apps (${(state.applications||[]).length})</summary><p class="field-note">Remembered page maps, not active connections.</p>${(state.applications||[]).map(a=>`<div class="application-row"><strong>${esc(a.title||a.origin)}</strong><p>${esc(a.origin)}</p></div>`).join('')||'<p class="field-note">No previous apps.</p>'}</details>`;
}
function showBrowser(){inspector('Browser',browser.connected?`<h2>${esc(browser.title||'Connected browser')}</h2><div id="browser-live-inspector">${browserDescription()}</div>`:'<h2>No browser connected</h2><p class="description">Connect an application to see its page here.</p><button class="primary-button" data-action="computer">Connect an app</button>',true);}
async function connectBrowser(url,button){if(button){button.disabled=true;button.textContent='Connecting…';}try{browser=await api('/api/browser/connect',{url});$('use-browser').checked=true;await refresh();renderComputer();updateComposer();toast('Browser connected. Start a task when you are ready.');}catch(e){toast(e.message);if(button){button.disabled=false;button.textContent='Connect browser';}}}
function renderSearch(query){query=query.toLowerCase().trim();const items=[...data.chats.map(c=>({id:c.id,title:c.title,action:'chat',type:'Chat',icon:'file'})),...state.registry.map(s=>({id:s.manifest.id,title:s.manifest.title,action:'skill',type:'Skill',icon:'book-magic-skill'})),...data.workflows.map(w=>({id:w.id,title:w.title,action:'workflow',type:'Workflow',icon:'reuse'}))].filter(x=>x.title.toLowerCase().includes(query));$('search-results').innerHTML=items.map(x=>`<button class="search-result" data-action="search-open" data-target="${x.action}" data-id="${esc(x.id)}">${icon(x.icon)}<span>${esc(x.title)}</span><small>${x.type}</small></button>`).join('')||'<p class="sidebar-empty">No matches yet.</p>';}
function search(){$('search-input').value='';renderSearch('');$('search-dialog').showModal();$('search-input').focus();}
function download(value,name){const url=URL.createObjectURL(new Blob([typeof value==='string'?value:JSON.stringify(value,null,2)],{type:typeof value==='string'?'text/plain':'application/json'}));const link=document.createElement('a');link.href=url;link.download=name;link.click();setTimeout(()=>URL.revokeObjectURL(url),1000);}
async function sourceRun(id){let run=runById(id);if(!run){run=await api('/api/runs/'+encodeURIComponent(id));runCache.set(id,run);}let chat=data.chats.find(c=>(c.runIds||[]).includes(id));if(!chat){chat={id:run.chat_id||`run-${run.id}`,title:run.task.slice(0,48),projectId:run.project_id,runIds:[id]};data.chats.push(chat);await persist();}await openChat(chat.id);}
function sampleTask(){newChat();$('message').value='Clean these workshop registrations: trim names, normalize emails, keep the first registration for each email, and list the duplicate entries separately.';files=[{name:'registrations.json',content:JSON.stringify([{name:' Alex ',email:'ALEX@example.test',workshop:'Design'},{name:'Sam',email:'sam@example.test',workshop:'Agents'},{name:'Alex second entry',email:'alex@example.test',workshop:'Design'}],null,2)}];updateComposer();}
const actions={
 'new-task':()=>newChat(),chat:id=>openChat(id),project:openProject,skill:id=>showSkill(id),workflow:showWorkflow,result:showResult,evidence:showEvidence,computer:openComputer,'browser-preview':showBrowser,sample:sampleTask,
 'new-project-chat':newChat,'project-context':showProjectContext,'source-run':sourceRun,
 'toggle-project':id=>{if(expandedProjects.has(id))expandedProjects.delete(id);else expandedProjects.add(id);renderSidebar();},
 'toggle-recent':()=>{recentExpanded=!recentExpanded;renderSidebar();},
 'confirm-result':async id=>{await api('/api/run/review',{id});await refresh();toast('Recorded your confirmation.');},
 'save-context':async id=>{projectById(id).instructions=$('project-instructions').value;if(await persist())toast('Project instructions saved.');},
 'remove-file':id=>{files.splice(Number(id),1);updateComposer();},
 'follow-up':id=>{closeInspector();context={type:'followup',id,label:'Continue from this result'};$('use-browser').checked=runById(id)?.mode==='browser'&&browser.connected;$('use-desktop').checked=runById(id)?.mode==='desktop'&&operations.desktopState().connected;updateComposer();$('message').focus();},
 retry:id=>{const r=runById(id);if(!r)return;$('message').value=r.task;files=r.input?.files||[];context=r.kind==='correction'?{type:'correction',id:r.input.capability,label:'Retry correction'}:null;$('use-browser').checked=r.mode==='browser'&&browser.connected;updateComposer();},
 'use-skill':id=>{const s=skillById(id);newChat(s?.provenance?.project_id||null);context={type:'skill',id,label:'Use: '+s.manifest.title};updateComposer();},
 'correct-skill':correctSkill,'improve-run':improveRun,'save-workflow':saveWorkflow,
 'deactivate-skill':async id=>{await api('/api/deactivate',{id});await refresh();showSkill(id);},
 'activate-skill':async(id,button)=>{await api('/api/activate',{id,version:Number(button.dataset.version)});await refresh();showSkill(id);},
 'export-skill':(id,button)=>{const r=state.versions.find(s=>s.manifest.id===id&&s.version===Number(button.dataset.version));download(r,`${id}-v${r.version}.json`);},
 'download-result':id=>download(runById(id).result,`result-${id.slice(0,8)}.${typeof runById(id).result==='string'?'txt':'json'}`),
 'download-evidence':id=>download({run:runById(id),events:events.get(id)||[]},`evidence-${id.slice(0,8)}.json`),
 'use-workflow':id=>{const w=data.workflows.find(w=>w.id===id);newChat(w.projectId);context={type:'workflow',id,label:'Workflow: '+w.title};$('message').value=w.prompt;$('use-browser').checked=w.mode==='browser'&&browser.connected;$('use-desktop').checked=w.mode==='desktop'&&operations.desktopState().connected;updateComposer();},
 'schedule-workflow':id=>operations.scheduleForm(data.workflows.find(w=>w.id===id)),
 'delete-workflow':async id=>{data.workflows=data.workflows.filter(w=>w.id!==id);await persist();openLibrary('workflows');},
 practice:async(_,button)=>{await connectBrowser('https://event.workspace.demo',button);if(browser.origin==='https://event.workspace.demo')await operations.showcase();},
 'disconnect-browser':async()=>{browser=await api('/api/browser/disconnect',{});updateComposer();renderComputer();},
 'refresh-browser':async()=>{browser=await api('/api/browser/refresh',{});renderComputer();},
 'browser-task':()=>{if(browser.origin==='https://event.workspace.demo')return operations.showcase();newChat();$('use-browser').checked=true;if(browser.origin==='https://workspace.demo')$('message').value='Add Alex Morgan to the Building agents workshop. Use alex@example.test and mark them as checked in. Confirm that the participant appears in the list.';updateComposer();$('message').focus();},
 approve:async()=>{await api('/api/browser/approve',{approved:true});toast('Allowed this browser step.');},
 decline:async()=>{await api('/api/browser/approve',{approved:false});await api('/api/stop',{});},
};
document.addEventListener('click',async event=>{const b=event.target.closest('[data-action]');if(!b)return;try{if(b.dataset.action==='search-open'){$('search-dialog').close();if(b.dataset.target==='skill')openLibrary('skills');if(b.dataset.target==='workflow')openLibrary('workflows');await actions[b.dataset.target]?.(b.dataset.id,b);}else await actions[b.dataset.action]?.(b.dataset.id,b);}catch(e){toast(e.message);}});
document.addEventListener('submit',event=>{if(event.target.id==='connect-browser-form'){event.preventDefault();connectBrowser($('browser-url').value,event.target.querySelector('button'));}});
document.addEventListener('input',event=>{if(event.target.id!=='library-filter')return;let count=0;const q=event.target.value.toLowerCase();document.querySelectorAll('[data-filter]').forEach(row=>{row.hidden=!row.dataset.filter.includes(q);if(!row.hidden)count++;});$('filter-empty').hidden=count>0;});
document.addEventListener('change',event=>{if(event.target.id==='skill-version')showSkill(event.target.dataset.skill,event.target.value);});
$('workspace-home').onclick=()=>newChat();$('new-chat').onclick=()=>newChat();$('search-chats').onclick=search;
$('nav-library').onclick=()=>localActions.open();
$('nav-skills').onclick=()=>openLibrary('skills');$('nav-workflows').onclick=()=>openLibrary('workflows');$('nav-computer').onclick=openComputer;
$('explore-example').onclick=openComputer;$('browse-skills').onclick=()=>openLibrary('skills');$('sample-task').onclick=sampleTask;
$('composer-form').onsubmit=submit;$('message').addEventListener('input',updateComposer);
$('message').addEventListener('keydown',event=>{if(event.key==='Enter'&&!event.shiftKey&&!event.isComposing){event.preventDefault();$('composer-form').requestSubmit();}});
$('clear-composer-context').onclick=()=>{context=null;updateComposer();};$('close-inspector').onclick=closeInspector;
$('context-button').onclick=()=>showProjectContext($('context-button').dataset.projectId);
$('close-search').onclick=()=>$('search-dialog').close();$('search-input').oninput=event=>renderSearch(event.target.value);
$('new-project').onclick=()=>{$('project-name').value='';$('project-dialog').showModal();$('project-name').focus();};$('cancel-project').onclick=()=>$('project-dialog').close();
$('project-form').onsubmit=async event=>{event.preventDefault();const name=$('project-name').value.trim();if(!name)return;await withButtonFeedback($('project-form').querySelector('[type="submit"]'),'Creating…',async()=>{const p={id:crypto.randomUUID(),name,instructions:''};data.projects.push(p);if(await persist()){$('project-dialog').close();openProject(p.id);}});};
$('settings').onclick=()=>{
  $('settings-runtime').innerHTML=`
    <section id="chatgpt-settings" aria-label="Model connection"><p>Loading your connection…</p></section>
    <details class="settings-disclosure"><summary>API keys &amp; other providers</summary>
      <div class="settings-disclosure-content"><p>ChatGPT uses your subscription. Gemini uses a separate API key from your local configuration.</p><p>API key entry and additional providers are not available in this panel yet.</p></div>
    </details>
    <details class="settings-disclosure"><summary>Runtime &amp; limits</summary>
      <div class="settings-disclosure-content"><p><span id="settings-model-name">${esc(state.model||'Not connected')}</span><br><span id="settings-model-status">${state.model_ready?'Model configured':esc(state.model_status||'Server unavailable')}</span></p>
      <p>Up to ${state.limits?.calls||0} model calls and ${state.limits?.seconds||0} seconds per task. Skills run in a local sandbox.</p>
      <p id="settings-financial-policy" class="field-note">${esc(financialPolicyText())}</p>
      <button class="text-button" id="check-runtime">Check runtime</button><p id="runtime-health" role="status"></p></div>
    </details>`;
  mountChatGPTSettings($('chatgpt-settings'),{api,esc,toast,refresh,state});
  $('settings-dialog').showModal();
  $('check-runtime').onclick=async event=>{await withButtonFeedback(event.currentTarget,'Checking…',async()=>{try{const health=await api('/api/health');$('runtime-health').textContent=`Sandbox: ${health.sandbox?'ready':'unavailable'}. Model: ${health.model_ready?'configured':'unavailable'}.`;}catch(e){toast(e.message);}});};
};
$('close-settings').onclick=()=>$('settings-dialog').close();
$('stop-run').onclick=async()=>{try{const result=await api('/api/stop',{});toast(result.message);await refresh();}catch(e){toast(e.message);}};
function setSidebar(open){$('sidebar').hidden=!open;$('app-shell').classList.toggle('sidebar-hidden',!open);$('show-sidebar').hidden=open;$('sidebar-shade').hidden=!(open&&matchMedia('(max-width:760px)').matches);interactions.syncNavigation();}
$('hide-sidebar').onclick=()=>setSidebar(false);$('show-sidebar').onclick=()=>setSidebar(true);$('sidebar-shade').onclick=()=>setSidebar(false);
const smallScreen=matchMedia('(max-width:760px)');smallScreen.addEventListener('change',event=>setSidebar(!event.matches));if(smallScreen.matches)setSidebar(false);
$('attach-file').onclick=()=>$('file-input').click();$('file-input').onchange=async event=>{const input=event.target,f=input.files[0];if(!f)return;const target=draftKey();await withButtonFeedback($('attach-file'),'Uploading file…',async()=>{try{const file=await operations.attach(f);if(target!==draftKey()){toast('The chat changed. Attach the file again.');return;}files.push(file);updateComposer();}catch(error){toast(error.message);}finally{input.value='';}});};
$('use-browser').onchange=()=>{if($('use-browser').checked)$('use-desktop').checked=false;};$('use-desktop').onchange=()=>{if($('use-desktop').checked)$('use-browser').checked=false;};
document.addEventListener('keydown',event=>{if((event.metaKey||event.ctrlKey)&&event.key.toLowerCase()==='k'){event.preventDefault();if(!$('search-dialog').open)search();}if(event.key==='Escape')closeInspector();});
for(const dialog of document.querySelectorAll('dialog'))dialog.addEventListener('click',event=>{if(event.target===dialog){const r=dialog.getBoundingClientRect();if(event.clientX<r.left||event.clientX>r.right||event.clientY<r.top||event.clientY>r.bottom)dialog.close();}});
let refreshing=false,lastRender='',lastRegistry='';
const localActions=createLocalActions({$,api,esc,icon,toast,getState:()=>state,getBrowser:()=>browser,getData:()=>data,getRoute:()=>route,setRoute:value=>route=value,leave,showView,header,renderSidebar,refresh,sourceRun});
const operations=createOperations({$,api,esc,icon,toast,inspector,leave,setRoute:value=>route=value,showView,header,renderSidebar,getState:()=>state,getRoute:()=>route,newChat,updateComposer,getFiles:()=>files,setFiles:value=>files=value,getData:()=>data,persist,sourceRun});
operations.setBrowser(renderComputer);$('nav-schedules').onclick=operations.openSchedules;
const insights=createInsights({ $,api,esc,icon,leave,setRoute:value=>route=value,getRoute:()=>route,showView,header,renderSidebar,inspector,projectById,download });
$('nav-overview').onclick=insights.open;$('nav-guide').onclick=insights.guide;
Object.assign(actions,{overview:insights.open,guide:insights.guide,usage:insights.showUsage,'export-usage':insights.exportAll,'export-task-usage':insights.exportTask,'open-skills':()=>openLibrary('skills'),'open-workflows':()=>openLibrary('workflows')});
async function refresh(){
  if(refreshing)return;refreshing=true;
  try{
    const [next,br]=await Promise.all([api('/api/state'),api('/api/browser/state')]);state=next;browser=br;await operations.poll();connected=true;
    if($('settings-financial-policy'))$('settings-financial-policy').textContent=financialPolicyText();if($('settings-model-name'))$('settings-model-name').textContent=state.model||'Not connected';if($('settings-model-status'))$('settings-model-status').textContent=state.model_ready?'Model configured':state.model_status||'Server unavailable';
    $('provider-notice').textContent=state.ai_paused?'Blackout is on. Saved actions run locally; resume AI for chat tasks.':state.provider==='chatgpt'?'Using ChatGPT plan · Tasks and attachments are sent directly to OpenAI. Skills run in a local sandbox.':'Tasks and attached content are sent to Gemini. Skills run in a local sandbox.';$('connection-label').textContent=state.ai_paused?'AI paused · Actions ready':state.model_ready?`${state.provider_label||'Gemini'} configured`:'Setup needed';$('runtime-status').textContent=state.busy?'Working':state.ai_paused?'Local only':state.model_ready?'Ready':'Setup needed';
    if(!workspaceSaves&&JSON.stringify(data)===JSON.stringify(workspaceBase)){const remote=await api('/api/workspace');if(!workspaceSaves&&JSON.stringify(data)===JSON.stringify(workspaceBase)){data=reconcile(workspaceBase,data,remote);workspaceBase=structuredClone(remote);renderSidebar();}}
    let imported=false;for(const r of state.runs){runCache.set(r.id,r);if(!data.chats.some(c=>(c.runIds||[]).includes(r.id))){let chat=data.chats.find(c=>c.id===r.chat_id);if(!chat){chat={id:r.chat_id||`run-${r.id}`,title:r.task.slice(0,48),projectId:r.project_id||null,runIds:[]};data.chats.push(chat);}chat.runIds.push(r.id);imported=true;}}
    if(imported)await persist();
    const activeChat=chatById(route.id);for(const id of activeChat?.runIds||[])if(['running','queued'].includes(runById(id)?.status)||!events.has(id)||state.runs.some(r=>r.id===id)){events.set(id,await api('/api/events/'+encodeURIComponent(id)));}
    const signature=JSON.stringify([route,state.runs.map(r=>[r.id,r.status,r.error,r.model_calls]),(activeChat?.runIds||[]).map(id=>events.get(id)?.length),browser.pending,operations.desktopState().pending]);
    if(signature!==lastRender){renderSidebar();renderChat();lastRender=signature;}
    const registrySignature=JSON.stringify(state.versions.map(s=>[s.manifest.id,s.version]))+JSON.stringify(state.registry.map(s=>[s.manifest.id,s.version]));
    if(registrySignature!==lastRegistry){renderLibrary();lastRegistry=registrySignature;}
    if($('connection-approval'))$('connection-approval').innerHTML=approvalHTML();
    if(route.type==='computer'&&$('browser-live'))updateLivePanel($('browser-live'),browserDescription());
    if($('inspector').dataset.kind==='Browser'&&$('browser-live-inspector'))updateLivePanel($('browser-live-inspector'),browserDescription());
    await insights.refresh();
    localActions.sync();
    updateComposer();
  }catch(error){connected=false;$('provider-notice').textContent=state.provider==='chatgpt'?'Using ChatGPT plan · Tasks and attachments are sent directly to OpenAI. Skills run in a local sandbox.':'Tasks and attached content are sent to Gemini. Skills run in a local sandbox.';$('connection-label').textContent='Server unavailable';$('runtime-status').textContent='Offline';updateComposer();}
  finally{refreshing=false;clearTimeout(pollTimer);pollTimer=setTimeout(refresh,state.busy?1000:5000);}
}
async function init(){
  openChat();
  try{
    data=await api('/api/workspace');workspaceBase=structuredClone(data);
    if(!data.projects.length&&!data.chats.length){try{const old=JSON.parse(localStorage.getItem('learning-workspace.design.v1')||'null');if(old){data.projects=(old.projects||[]).filter(p=>p.id!=='example-project');data.chats=(old.chats||[]).map(c=>({id:c.id,title:c.title,projectId:data.projects.some(p=>p.id===c.projectId)?c.projectId:null,runIds:[],draftText:c.messages?.filter(m=>m.role==='user').map(m=>m.text).join('\n\n')}));await persist();}}catch{}}
    await refresh();renderSidebar();
  }catch(error){toast('Could not connect to the local runtime: '+error.message);await refresh();}
}
// Keep approved symbols in this document so repeated view updates cannot invalidate
// external SVG references in Chromium. No replacement icon set is introduced.
async function loadIconSymbols(){
  const response=await fetch(iconSource);if(!response.ok)return;
  const svg=new DOMParser().parseFromString(await response.text(),'image/svg+xml').documentElement;
  if(svg.localName!=='svg')return;
  const symbols=document.importNode(svg,true);symbols.classList.add('icon-symbols');symbols.setAttribute('width','0');symbols.setAttribute('height','0');symbols.setAttribute('aria-hidden','true');document.body.prepend(symbols);
  for(const use of document.querySelectorAll('.icon use')){const href=use.getAttribute('href');if(href?.startsWith(iconSource+'#'))use.setAttribute('href',href.slice(iconSource.length));}
  iconSource='';
}
loadIconSymbols().catch(()=>{}).finally(init);
