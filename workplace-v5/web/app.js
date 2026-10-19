'use strict';
const $=id=>document.getElementById(id), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let ws=null,sceneId='progress',cat='report',session=null,busy=false,currentTab='practice',apiEditId='',objectEditId='',quoteObjectId='',meetingDraft=null,freePreviousId='',preferencesReady=false,toastTimer;
let reviewBusyId=null,reviewPolling=false;const reviewIntent=new Set(),reviewLocalErrors=new Map();
const categories=[['report','项目汇报','Project briefing'],['technical','技术评审','Technical review'],['customer','客户沟通','Customer dialogue'],['english','国际协作','Global collaboration']];
const objectLabels={name:'称呼',role:'角色 / 工作关系',goals:'工作目标',standards:'关注点 / 判断标准',style:'表达风格',personality:'性格与沟通习惯（可选）',technicalBackground:'变流技术背景（可选）',responseGuide:'追问与推进方式（可选）',quotes:'语录（每行一句，可选）',difficulty:'沟通难点（可选）',facts:'已知事实 / 来源',inferences:'推断 / 虚拟补充',boundaries:'模拟边界'};
function toast(message){$('toast').textContent=message;$('toast').hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>$('toast').hidden=true,3500);}
function showError(id,message){$(id).textContent=message||'';$(id).hidden=!message;}
async function request(url,options={}){let r;try{r=await fetch(url,{cache:'no-store',...options});}catch{throw Error('本机服务器连接中断，请确认启动窗口仍在运行；已保存原话可恢复。');}const j=await r.json();if(!r.ok)throw Error(j.error||'请求失败 '+r.status);return j;}
async function action(operation,data={}){return request('/api/workplace/action',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({operation,requestId:crypto.randomUUID(),...data})});}
function brief(value,max=64){
 const full=String(value??'').replace(/\s+/g,' ').trim();if(full.length<=max)return full;
 let cut=full.slice(0,max-1),stop=Math.max(cut.lastIndexOf('。'),cut.lastIndexOf('；'),cut.lastIndexOf('，'),cut.lastIndexOf('、'),cut.lastIndexOf(' '));
 if(stop>=Math.floor(max*.55))cut=cut.slice(0,stop+1);
 return cut.replace(/[，、；,:; ]+$/,'')+'…';
}
function shortVerdict(r){
 if(typeof r.summary==='string'&&r.summary.trim())return brief(r.summary,64);
 const full=String(r.overall||'').trim(),sentence=full.match(/^[\s\S]*?[。！？!?](?=\s|[^”’]|$)/)?.[0];
 return brief(sentence||full,64);
}
function stamp(value){return new Date(value).toLocaleString('zh-CN');}
const visualButton=b=>b.matches('[data-expand-answer],[data-theme-choice],#themeOpen,[data-close="themeDialog"]');
function lock(value,note='模型生成中，请稍候…'){busy=value;document.querySelectorAll('button').forEach(b=>b.disabled=value&&!visualButton(b));$('reply').disabled=value;$('freeInput').disabled=value;$('experienceFile').disabled=value;$('intensity').disabled=value;$('meetingText').disabled=value;$('meetingTitle').disabled=value;$('meetingFile').disabled=value;$('projectSelect').disabled=value;$('meetingPreview').querySelectorAll('input,select').forEach(el=>el.disabled=value||el.dataset.applied==='1');$('modelStatus').textContent=value?note:'';if(!value)syncSessionButtons();}
function isReviewFlow(s){return !!s&&(!!s.review||!!s.reviewStatus||['review_pending','review_failed','ended'].includes(s.status)||reviewIntent.has(s.id)||localStorage.getItem('workplace_review_intent:'+s.id)==='1');}
function markReviewIntent(id){reviewIntent.add(id);localStorage.setItem('workplace_review_intent:'+id,'1');}
function reviewIsPending(s){return reviewBusyId===s.id||(s.status==='review_pending'&&!reviewLocalErrors.has(s.id));}
function syncSessionButtons(){
 if($('meetingApply'))$('meetingApply').disabled=busy||meetingDraft.items.every(i=>meetingDraft.appliedItems.includes(i.id));
 $('start').disabled=busy||!ws?.objects?.length;$('objectSelect').disabled=busy||!ws?.objects?.length;
 if(!session)return;
 const active=session.status==='active'&&!isReviewFlow(session),pending=!session.messages.length||session.messages.at(-1)?.role==='user';
 $('send').disabled=busy||!active||pending||!$('reply').value.trim();$('end').disabled=busy||!active;
 $('retry').hidden=!active||!pending;$('retry').disabled=busy;$('cancel').hidden=!active;
 for(const b of $('review').querySelectorAll('button'))b.disabled=b.hasAttribute('data-expand-answer')?false:busy||reviewIsPending(session);
}

async function refresh(){ws=await request('/api/workplace/workspace');renderWorkspace();return ws;}
function renderWorkspace(){renderSelection();renderObjects();renderMeetings();renderExperiences();renderFreeHistory();renderPortrait();renderRecords();if(!preferencesReady){$('intensity').value=ws.preferences?.intensity||'标准';preferencesReady=true;}const c=ws.config.apis?.find(a=>a.id===ws.config.active);$('apiBadge').textContent=c?c.name:'未配置';}
function selectedScene(){return ws.scenes.find(s=>s.id===sceneId)||ws.scenes[0];}
function defaultObject(s){const preferred={report:'builtin-project',technical:'builtin-technical',customer:'builtin-customer',english:'builtin-global'}[s.cat];return ws.objects.some(o=>o.id===preferred)?preferred:ws.objects[0]?.id||'';}
function objectLabel(o){return o.name.replace(/：/g,':').endsWith(':'+o.role)||o.name===o.role?o.name:`${o.name} · ${o.role}`;}
function renderSelection(){if(!ws)return;const s=selectedScene();$('categories').innerHTML=categories.map(([id,name,en],i)=>`<button class="category ${id===cat?'active':''}" data-category="${id}" aria-pressed="${id===cat}"><span class="category-index">0${i+1}</span><span><strong>${name}</strong><small>${en}</small></span></button>`).join('');$('scenes').innerHTML=ws.scenes.filter(s=>s.cat===cat).map(s=>`<button class="scene ${s.id===sceneId?'active':''}" data-scene="${s.id}" aria-pressed="${s.id===sceneId}"><strong>${esc(s.title)}</strong><small>${esc(s.short)}</small></button>`).join('');$('sceneTitle').textContent=s.title;$('sceneDescription').textContent=s.description;$('previewOpening').textContent=s.opening;$('previewRole').textContent=s.role;const old=$('objectSelect').value;$('objectSelect').innerHTML=ws.objects.map(o=>`<option value="${esc(o.id)}">${esc(objectLabel(o))}</option>`).join('')||'<option value="">暂无可选对象</option>';$('objectSelect').value=ws.objects.some(o=>o.id===old)?old:defaultObject(s);if(!$('goal').value)$('goal').value=s.goal;$('noObjects').hidden=!!ws.objects.length;$('objectFocus').hidden=!ws.objects.length;renderFocus();syncSessionButtons();}
function chooseScene(id){sceneId=id;cat=selectedScene().cat;$('goal').value=selectedScene().goal;$('objectSelect').value=defaultObject(selectedScene());renderSelection();}
function objectFacts(o){return Object.entries(objectLabels).filter(([k])=>!['name','role'].includes(k)).map(([k,label])=>`<p class="object-fact"><b>${label}</b><br>${esc(o[k]||'尚未补充')}</p>`).join('');}
function renderFocus(){const o=ws.objects.find(p=>p.id===$('objectSelect').value);$('focusContent').innerHTML=o?objectFacts(o):'';const name=o?.name||selectedScene().role;$('previewAvatar').textContent=[...name][0]||'';$('previewRole').textContent=name;}
function showTab(id){currentTab=id;document.querySelectorAll('.view').forEach(v=>v.hidden=v.id!==id);document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b.dataset.tab===id));}
function renderObjects(){$('objectCards').innerHTML=ws.objects.map(o=>`<article class="object-card"><div class="object-card-top"><span class="profile-avatar">${esc(o.name.slice(0,1))}</span><span class="object-kind">沟通对象</span></div><h3>${esc(o.name)}</h3><p class="muted">${esc(o.role)}</p><p>${esc(brief(o.goals,90))}</p><details><summary>画像详情 · 事实与推断</summary>${objectFacts(o)}</details><div class="actions object-actions"><button class="outline" data-edit-object="${esc(o.id)}">编辑画像</button><button class="outline" data-object-quotes="${esc(o.id)}">语录与分析</button><button class="delete-object" data-delete-object="${esc(o.id)}">删除对象</button></div></article>`).join('')||'<div class="empty"><h3>给下一次沟通，选一个新对象。</h3><p>已删除对象的训练记录仍可在「训练记录」查看。</p></div>';}
function renderQuoteAnalysis(o){
 const a=o.quoteAnalysis;
 if(!a)return `<p class="muted">${o.quoteAnalysisStale?'语录已更新，原分析已失效，请重新分析。':'记录语录后，可让 AI 分析沟通特征并生成可能的表达。'}</p>`;
 return `<div class="quote-analysis-head"><h3>基于语录的特征推测</h3><small>${a.sampleCount} 条语录 · ${esc(stamp(a.at))}</small></div><p class="muted">${esc(a.summary)}</p>${a.traits.map(t=>`<article class="quote-trait"><h4>${esc(t.title)} <small>AI 推测</small></h4><p>${esc(t.description)}</p><details><summary>查看原话依据</summary>${t.evidence.map(q=>`<blockquote class="quote-evidence">${esc(q)}</blockquote>`).join('')}</details></article>`).join('')}<h3>可能的表达 · AI 模拟</h3><p class="muted">以下不是对象说过的原话，不会自动加入语录。</p>${a.likelyLines.map(t=>`<article class="quote-prediction"><p>${esc(t.text)}</p><details><summary>参考了哪些语录</summary>${t.basis.map(q=>`<blockquote class="quote-evidence">${esc(q)}</blockquote>`).join('')}</details></article>`).join('')}`;
}
function openQuotes(id){
 const o=ws.objects.find(p=>p.id===id);if(!o)return;
 quoteObjectId=id;$('quotesDialogTitle').textContent=o.name+' · 语录';$('objectQuotes').value=o.quotes||'';
 $('quoteAnalysis').innerHTML=renderQuoteAnalysis(o);$('quotesStatus').textContent='';$('quotesDialog').showModal();
}
async function saveQuotes(analyze=false){
 if(busy||!quoteObjectId)return;
 const raw=$('objectQuotes').value;let saved=false;
 if(analyze&&!raw.trim()){$('quotesStatus').textContent='请先记录至少一句语录。';return;}
 lock(true,analyze?'正在分析对象语录…':'正在保存语录…');$('objectQuotes').disabled=true;
 $('quotesStatus').textContent=analyze?'正在保存并分析，语录会先保留…':'正在保存…';
 try{
  await action('object-quotes',{objectId:quoteObjectId,quotes:raw});saved=true;await refresh();
  const obj=ws.objects.find(p=>p.id===quoteObjectId);if(obj)$('quoteAnalysis').innerHTML=renderQuoteAnalysis(obj);
  if(analyze){await action('analyze-object',{objectId:quoteObjectId});await refresh();$('quoteAnalysis').innerHTML=renderQuoteAnalysis(ws.objects.find(p=>p.id===quoteObjectId));}
  $('quotesStatus').textContent=analyze?'语录与 AI 分析已保存，供新训练参考。':'语录已保存，供新训练参考。';
 }catch(e){$('quotesStatus').textContent=e.message+(saved?'；语录已保存，可重试分析。':'；输入仍保留在此页，可重试保存。');}
 finally{lock(false);$('objectQuotes').disabled=false;}
}
async function deleteObject(id){
 const o=ws.objects.find(p=>p.id===id);if(!o||busy)return;
 if(!confirm(`删除「${o.name}」？该对象将从可选名单移除，已有对话、复盘和画像证据保留。`))return;
 lock(true,'正在删除对象…');
 try{await action('delete-object',{objectId:id});await refresh();toast('对象已删除，已有训练记录保留。');}
 catch(e){toast(e.message);}
 finally{lock(false);}
}
function openObject(id){const o=ws.objects.find(p=>p.id===id)||{};objectEditId=o.id||'';$('objectDialogTitle').textContent=o.id?'编辑对象画像':'新建对象画像';$('objectFields').innerHTML=Object.entries(objectLabels).map(([k,label])=>`<label>${label}${['name','role'].includes(k)?`<input name="${k}" value="${esc(o[k]||'')}" required maxlength="200">`:`<textarea name="${k}" rows="${['quotes','personality','technicalBackground','responseGuide'].includes(k)?6:2}" ${['quotes','difficulty','personality','technicalBackground','responseGuide'].includes(k)?'':'required'}>${esc(o[k]||(k==='facts'?'虚拟训练对象，不对应现实人物':k==='inferences'?'仅用于本场景模拟的推断':k==='boundaries'?'尊重对方，不羞辱、不作人格攻击':''))}</textarea>`}</label>`).join('');$('objectStatus').textContent='';$('objectDialog').showModal();}
function applySession(s){document.body.classList.add('session-active');session=s;localStorage.setItem('workplace_active_session',s.id);$('selection').hidden=true;$('sessionPanel').hidden=false;showTab('practice');renderSession();}
function renderSession(){
 if(!session)return;const s=session,reviewMode=isReviewFlow(s);$('sessionPanel').classList.toggle('is-review',reviewMode);
 $('sessionPhase').textContent=reviewMode?'03 / 结束与复盘':'02 / 连续对话';
 $('sessionTitle').textContent=reviewMode?'本次训练复盘':s.object.name;
 const state=reviewMode?(s.review?(s.review.timeline.some(t=>!t.improved||!t.feedback)?'评分已生成 · 说明可补全':'已完成复盘'):reviewIsPending(s)?'训练已结束 · 正在生成复盘':'训练已结束 · 对话已保留'):s.status==='archived'?'已中断，记录保留':'训练进行中';
 $('sessionMeta').textContent=`${s.scene.title} · ${s.scene.lang==='en'?'英文对话 / 中文复盘':'中文对话'} · ${state} · ${s.intensity}追问`;
 $('snapshot').innerHTML=`<p><b>本轮目标</b><br>${esc(s.goal)}</p><p><b>背景</b><br>${esc(s.background||'未提供')}</p>${s.project?`<p><b>参考项目</b><br>${esc(s.project.name)}</p>`:''}${objectFacts(s.object)}${s.experiences?.length?`<p><b>本轮参考经验（训练开始时保存）</b></p>${s.experiences.map(e=>`<p><b>${esc(e.title)}</b><br>${esc(e.content)}</p>`).join('')}`:''}${s.intensityChanges?.length?`<p><b>强度调整记录</b><br>${s.intensityChanges.map(e=>esc(e.from+' → '+e.to+' · '+stamp(e.at))).join('<br>')}</p>`:''}`;
 $('chat').hidden=reviewMode;
 $('chat').innerHTML=s.messages.map(m=>`<article class="bubble ${m.role==='user'?'user':''}" id="message-${esc(m.id)}"><small>${m.role==='user'?'你':esc(s.object.name)}</small><p>${esc(m.text)}</p>${m.interpretation?`<details><summary>展开原话三层解读 · 模拟推断</summary><div class="interpretation"><p><b>表面问题</b><br>${esc(m.interpretation.surface)}</p><p><b>核心关切</b><br>${esc(m.interpretation.real)}</p><p><b>判断依据</b><br>${esc(m.interpretation.hidden)}</p><p class="muted">这是模型的模拟解读，不代表现实人物的心理事实。</p></div></details>`:''}</article>`).join('')||'<p class="muted">等待模型生成开场；失败可重试。</p>';
 $('chat').scrollTop=$('chat').scrollHeight;
 const bound=ws.config.apis?.find(a=>a.id===s.apiId);
 showError('sessionError',reviewMode?'':s.status==='active'&&!bound?'本轮绑定的旧 API 配置已不存在。点击「使用当前 API 配置」，再重试模型回应；已提交原话会保留。':s.error);
 $('useCurrentAPI').hidden=reviewMode||s.status!=='active'||s.apiId===ws.config.active;$('composer').hidden=reviewMode||s.status!=='active';$('end').hidden=reviewMode||s.status!=='active';
 $('review').hidden=!reviewMode;$('review').setAttribute('aria-busy',String(reviewMode&&!s.review&&reviewIsPending(s)));
 $('exportHTML').hidden=!s.review;$('print').hidden=!s.review;$('sessionActions').hidden=!reviewMode&&s.status==='active';
 $('exampleText').textContent=ws.examples[s.scene.lang==='en'?'en':'zh'];
 const openPanels=[...$('review').querySelectorAll('details[open][data-detail]')].map(d=>d.dataset.detail);
 const expanded=[...$('review').querySelectorAll('.answers-expanded[data-answer]')].map(d=>d.dataset.answer);
 $('review').innerHTML=reviewMode?(s.review?renderReview(s):renderReviewState(s)):'';
 for(const d of $('review').querySelectorAll('details[data-detail]'))if(openPanels.includes(d.dataset.detail))d.open=true;
 for(const d of $('review').querySelectorAll('[data-answer]'))if(expanded.includes(d.dataset.answer)){d.classList.add('answers-expanded');const b=d.querySelector('[data-expand-answer]');if(b){b.textContent='收起完整回答';b.setAttribute('aria-expanded','true');}}

 requestAnimationFrame(updateAnswerControls);
 syncSessionButtons();
}
function updateAnswerControls(){
 for(const box of document.querySelectorAll('.answer-comparison[data-answer]')){
  const button=box.querySelector('[data-expand-answer]');if(!button)continue;
  button.hidden=!box.classList.contains('answers-expanded')&&[...box.querySelectorAll('.answer-copy')].every(p=>p.scrollHeight<=p.clientHeight+1);
 }
}
window.addEventListener('resize',()=>requestAnimationFrame(updateAnswerControls));
document.addEventListener('toggle',e=>{if(e.target.matches('.round'))requestAnimationFrame(updateAnswerControls);},true);
function reviewMessage(error){
 if(/402|余额/.test(error))return '模型账户余额不足。充值后可在这里重新生成复盘，本轮对话已保留。';
 if(/429|额度/.test(error))return '模型调用频率或额度暂时受限。稍后可重新生成，本轮对话已保留。';
 if(/401|认证/.test(error))return '模型配置需要核对。请在 API 设置中检查后重试，本轮对话已保留。';
 if(/旧|不存在|绑定/.test(error))return '本轮使用的模型配置需要更新。可以切换到当前配置后重新生成。';
 if(/连接|网络|超时/.test(error))return '模型服务暂未完成回应。你可以稍后重试，本轮对话已保留。';
 return '模型这次未提供完整的复盘。你可以重新生成，也可以先查看和导出完整对话。';
}
function renderReviewState(s){
 const count=s.messages.filter(m=>m.role==='user').length,pending=reviewIsPending(s),empty=!count;
 const error=reviewLocalErrors.get(s.id)||s.reviewError||s.error||'';
 const title=pending?'正在生成本轮复盘':empty?'本轮训练已结束':'本轮复盘尚未生成';
 const note=pending?'正在分析完整对话、核对评分依据。完成后会直接在这里展示。':empty?'本轮还没有你的回应，暂时没有可评分的内容。开场记录已经保留，可以开始下一次训练。':reviewMessage(error);
 const missingBinding=!ws.config.apis?.some(a=>a.id===s.apiId);
 return `<header class="review-head review-stage-card"><div><p class="eyebrow">03 / 结束与复盘</p><h2>${title}</h2><p>${esc(note)}</p></div></header>
 <div class="review-summary"><div><strong>${count}</strong><span>条真实回应</span></div><div><strong>${s.messages.filter(m=>m.role==='assistant').length}</strong><span>条对方发言</span></div><div><strong>已保留</strong><span>完整训练记录</span></div></div>
 ${pending?'<div class="review-notice" role="status"><span class="review-spinner" aria-hidden="true"></span> 正在准备六维评分与逐轮复盘，请稍候…</div>':!empty?`<div class="review-notice" role="status">原话和目标快照已保留，重新生成不会重复提交回应。<div class="actions">${missingBinding?'<button class="outline" data-review-bind="1">使用当前 API 配置</button>':''}<button class="primary" data-review-retry="1">重新生成复盘</button></div></div>`:''}
 ${!pending&&error?`<details class="review-diagnostic"><summary>查看本次生成详情</summary><p class="muted">${esc(error)}</p></details>`:''}
 <section class="review-section"><h3>本轮完整对话</h3><p class="muted">${esc(s.scene.title)} · ${esc(s.object.name)}。评分生成前不显示虚构分数。</p>${s.messages.map(m=>`<div class="review-transcript"><small>${m.role==='user'?'你':esc(s.object.name)}</small><p>${esc(m.text)}</p></div>`).join('')||'<p class="muted">本轮没有已生成的消息。</p>'}</section>`;
}

function radar(dims){const cx=220,cy=205,r=135,pt=(i,f=1)=>{const a=-Math.PI/2+i*Math.PI/3;return [cx+Math.cos(a)*r*f,cy+Math.sin(a)*r*f];},poly=f=>dims.map((d,i)=>pt(i,f).join(',')).join(' ');return `<svg class="radar" viewBox="0 0 440 425" role="img" aria-label="六维雷达图，范围零至一百分"><title>六维 AI 评分，0–100</title>${[.2,.4,.6,.8,1].map(f=>`<polygon class="grid" points="${poly(f)}"/><text x="225" y="${cy-r*f-3}" style="font-size:10px">${f*100}</text>`).join('')}${dims.map((d,i)=>{const [x,y]=pt(i),[lx,ly]=pt(i,1.3);return `<line class="grid" x1="${cx}" y1="${cy}" x2="${x}" y2="${y}"/><text text-anchor="middle" dominant-baseline="middle" x="${lx}" y="${ly}">${esc(d.name)}</text>`;}).join('')}<polygon class="reference" points="${poly(.6)}"/><polygon class="shape" points="${dims.map((d,i)=>pt(i,d.score/100).join(',')).join(' ')}"/>${dims.map((d,i)=>{const [x,y]=pt(i,d.score/100);return `<circle class="dot" cx="${x}" cy="${y}" r="4"/>`;}).join('')}</svg>`;}
function quoteFor(s,id){return s.messages.find(m=>m.id===id)?.text||'';}
function scoreLines(dims){return dims.map(d=>`<div class="score-metric ${d.score<40?'needs-work':d.score<65?'developing':'solid'}"><div class="score-line"><span>${esc(d.name)}</span><b>${d.score}<small> / 100</small></b></div><div class="score-track" role="meter" aria-label="${esc(d.name)}" aria-valuemin="0" aria-valuemax="100" aria-valuenow="${d.score}"><span style="width:${Math.max(0,Math.min(100,Number(d.score)||0))}%"></span></div></div>`).join('');}

function dimension(d){return `<article class="dimension"><h3>${esc(d.name)} <span>${d.score} / 100</span></h3><p>${esc(d.basis)}</p>${d.evidence.map(e=>`<blockquote>${esc(e.quote)}<br><small class="muted">来源消息 ${esc(e.messageId.slice(0,8))}</small></blockquote>`).join('')}</article>`;}
function reportHeading(number,title,note=''){return `<div class="report-heading"><div><span class="section-number">${number}</span><h3>${title}</h3></div>${note?`<small>${note}</small>`:''}</div>`;}
function issueCard(item,index){return `<article class="issue-card ${index===0?'priority':'support'}"><span class="issue-order">重点 ${String(index+1).padStart(2,'0')}</span><h4>${esc(brief(item.title,32))}</h4><p>${esc(brief(item.action||item.desc,76))}</p><details><summary>查看分析与调整建议</summary><p><b>${esc(item.title)}</b></p>${item.desc?`<p>${esc(item.desc)}</p>`:''}${item.action?`<p><b>建议：</b>${esc(item.action)}</p>`:''}</details></article>`;}
function renderReview(s,expanded=false){
 const r=s.review,rank=[...r.dims].sort((a,b)=>a.score-b.score),weak=rank[0],strong=rank.at(-1);
 const moreIssues=[...r.loss.slice(2),...(r.additionalLoss||[])];
 return `<header class="review-head review-verdict">
 <div class="verdict-top"><span class="report-tag">AI 复盘 · 本轮反馈</span><small>${esc(stamp(r.at))}</small></div>
 <div class="verdict-body"><div class="score-block"><div class="bigscore">${r.score}<small> / 100</small></div><span>六维平均分</span></div>
 <div class="verdict-copy"><h2>${esc(s.scene.title)}</h2><p class="review-lead">${esc(shortVerdict(r))}</p><div class="verdict-meta"><span>${esc(s.object.name)}</span><span>${s.messages.filter(m=>m.role==='user').length} 次回应</span><span>${s.scene.lang==='en'?'英文训练':'中文训练'}</span></div></div></div></header>
 <div class="review-focus"><div class="focus-strength"><span class="focus-caption">本轮较高得分</span><strong>${esc(strong.name)}</strong><b>${strong.score}<small> / 100</small></b></div><div class="focus-priority"><span class="focus-caption">下一轮优先练习</span><strong>${esc(weak.name)}</strong><b>${weak.score}<small> / 100</small></b></div></div>
 <details class="overall-details" data-detail="overall"><summary>查看完整总评与评分说明</summary><div class="overall-full"><p>${esc(r.overall)}</p><p class="muted">${esc(r.sampleLimit)} 总分为六维平均取整数。AI 评分用于训练反馈，不是经验证的心理或能力测量。</p></div></details>
 ${r.timeline.some(t=>!t.improved||!t.feedback)?`<div class="review-notice" role="status">六维评分与原话依据已保存，部分点评或改进示范尚待补全。${r.detailError&&!expanded?`<details class="review-diagnostic"><summary>查看补全说明</summary><p>${esc(r.detailError)}</p></details>`:''}${!expanded?'<div class="actions"><button class="outline" data-review-details="1">补全点评与示范</button></div>':''}</div>`:''}
 <section class="review-section radar-section">${reportHeading('01','六维表现','先看图，再看具体依据')}
 <div class="radar-layout"><div>${radar(r.dims)}<div class="radar-legend"><span><i class="legend-actual"></i>本轮 AI 评分</span><span><i class="legend-reference"></i>60 分参考线</span></div></div><div class="dimension-meters">${scoreLines(r.dims)}<p class="muted">每维 0–100 分，数值来自本轮 AI 复盘。</p></div></div>
 <details class="dimension-details" data-detail="dimensions"><summary>展开六维依据与原话证据</summary>${r.dims.map(dimension).join('')}</details></section>
 <section class="review-section issues-section">${reportHeading('02','先改这几个关键点','把建议落到下一次表达')}
 <div class="issue-grid">${r.loss.slice(0,2).map(issueCard).join('')||'<p class="muted">模型未列出单独的问题清单，可查看下方逐轮反馈。</p>'}</div>
 ${moreIssues.length?`<details class="more-issues" data-detail="more-issues"><summary>其余模型观察（${moreIssues.length}）</summary><div class="issue-grid">${moreIssues.map((l,i)=>issueCard(l,i+2)).join('')}</div></details>`:''}</section>
 <section class="review-section rounds-section">${reportHeading('03','逐轮回看，换一种表达','原话、反馈与示范放在一起')}
 ${r.timeline.map((t,i)=>`<details class="round" data-detail="round-${i}" ${i===0?'open':''}><summary><span class="round-index">${String(i+1).padStart(2,'0')}</span><span>回应 ${i+1}</span><span class="round-score">${t.score}<small> / 100</small></span></summary><div class="round-body">
 <p class="round-feedback">${esc(brief(t.feedback||'本轮点评尚待补全，评分依据可展开查看。',100))}</p>
 <div class="answer-comparison ${expanded?'answers-expanded':''}" data-answer="${i}"><div class="answer-box answer-original"><span class="answer-label">原回答</span><p class="answer-copy original">${esc(quoteFor(s,t.messageId))}</p></div><div class="answer-box answer-improved demo"><span class="answer-label">改进示范${s.scene.lang==='en'?' · English':''}</span><p class="answer-copy">${esc(t.improved||'本轮改进示范尚待模型生成，可单独补全。')}</p></div>${!expanded?'<button class="text-button" data-expand-answer="1" aria-expanded="false">展开完整回答</button>':''}</div>
 <details class="round-evidence" data-detail="round-evidence-${i}"><summary>查看完整点评与本轮六维依据</summary><p>${esc(t.feedback||'本轮点评尚待模型生成。')}</p>${scoreLines(t.dims)}${t.dims.map(dimension).join('')}</details></div></details>`).join('')}</section>
 <section class="review-section translation-section">${reportHeading('04','读懂对方的问题','原话三层解读')}
 <p class="section-note">以下为本轮模拟解读，不代表现实人物的心理事实。</p>
 ${r.translations.map((t,i)=>`<details class="translation" data-detail="translation-${i}"><summary><span class="translation-number">${String(i+1).padStart(2,'0')}</span><span>${esc(brief(t.quote,92))}</span></summary><div class="translation-body"><blockquote>${esc(t.quote)}</blockquote>${t.source==='conversation'?'<p class="muted">训练时的 AI 解读</p>':''}<dl class="interpretation"><dt>表面问题</dt><dd>${esc(t.surface)}</dd><dt>核心关切</dt><dd>${esc(t.real)}</dd><dt>判断依据</dt><dd>${esc(t.hidden)}</dd></dl></div></details>`).join('')||'<p class="muted">模型没有提供单独的原话解读，完整对话仍可查看。</p>'}</section>
 <section class="review-section next-section">${reportHeading('05','下一轮，只练几件事','从具体行动开始')}
 <ol class="next-list">${r.next.map((n,i)=>`<li><span>${String(i+1).padStart(2,'0')}</span><p>${esc(n)}</p></li>`).join('')}</ol>
 ${!r.next.length?'<p class="muted">模型未单独列出下轮计划，可结合逐轮反馈继续练习。</p>':''}
 ${r.additionalNext?.length?`<details data-detail="more-next"><summary>更多模型建议（${r.additionalNext.length}）</summary><ol>${r.additionalNext.map(n=>`<li>${esc(n)}</li>`).join('')}</ol></details>`:''}${r.language?`<details class="language-note" data-detail="language"><summary>语言表达建议</summary><p>${esc(r.language)}</p></details>`:''}</section>
 <details class="full-transcript review-section" data-detail="transcript"><summary>完整对话记录（含开场）</summary>${s.messages.map(m=>`<div class="review-transcript"><small>${m.role==='user'?'你':esc(s.object.name)}</small><p>${esc(m.text)}</p></div>`).join('')}</details>
 ${s.portraitStatus==='failed'?'<p class="review-notice">本次复盘已保存，长期画像生成失败。可到「我的沟通画像」单独重试。</p>':''}`;
}

function renderPortrait(){const p=ws.portrait;let html=ws.portraitError?`<p class="error">画像更新失败：${esc(ws.portraitError)}。成功复盘已保留，可重试。</p>`:'';if(!p){$('portraitContent').innerHTML=html+'<div class="empty"><h3>尚在积累，先开始一场沟通。</h3><p>成功复盘后，AI 会从原话证据中总结表达特征、优势与练习方向。</p></div>';return;}html+=`<div class="portrait-summary"><small>${p.sessionCount<3?'初步画像 · 请谨慎理解':'持续积累'}</small><p>${esc(p.summary)}</p><small>${p.sessionCount} 场训练 · ${p.sampleCount} 条回应 · 更新于 ${esc(stamp(p.updated))}</small></div>`;for(const [key,label] of [['traits','沟通特征'],['strengths','已有优势'],['directions','提升方向']])html+=`<section class="portrait-section"><h3>${label}</h3>${p[key].map(o=>`<article class="observation"><h3>${esc(o.title)} <small class="muted">${esc(o.confidence)}</small></h3><p>${esc(o.description)}</p>${o.action?`<p><b>练习措施：</b>${esc(o.action)}</p>`:''}<details><summary>原话证据与来源</summary>${o.evidence.map(e=>`<blockquote class="evidence">${esc(e.quote)}</blockquote><button class="outline" data-open-session="${esc(e.sessionId)}">查看来源训练 · ${esc(e.messageId.slice(0,8))}</button>`).join('')}</details></article>`).join('')}</section>`;if(p.history?.length)html+=`<details><summary>画像更新历史</summary>${p.history.map(h=>`<p>${esc(stamp(h.updated))} · ${h.sessionCount} 场<br>${esc(h.summary)}</p>`).join('')}</details>`;$('portraitContent').innerHTML=html;}
function renderRecords(){$('records').innerHTML=ws.sessions.length?ws.sessions.map(s=>`<article class="record"><div><h3>${esc(s.scene)}</h3><p class="muted">${esc(s.objectName)} · ${esc(stamp(s.at))}<br>${s.turns} 条回应 · ${s.status==='reviewed'?`AI 六维总分 ${s.score}`:s.status==='archived'?'中断，原话保留':s.status==='review_pending'?'训练已结束 · 正在生成复盘':s.status==='review_failed'?'训练已结束 · 复盘可重试':s.status==='ended'?'训练已结束 · 暂无评分':'进行中 / 可恢复'}</p></div><div class="actions"><button class="outline" data-open-session="${esc(s.id)}">${s.status==='active'?'继续训练':'查看记录'}</button></div></article>`).join(''):'<div class="empty">还没有训练记录。无需个人画像即可开始。</div>';$('legacyRecords').innerHTML=ws.legacyRecords.length?'<h3>旧版记录 · 原样保留</h3>'+ws.legacyRecords.map(r=>`<details><summary>${esc(r.label)} · 旧评估</summary><p class="muted">原有评分与数据保留，未补造六维 AI 分数。只有含完整 role/text 对话的记录可重新分析。</p><button class="outline" data-reanalyze="${esc(r.id)}">重新 AI 分析完整对话</button><pre style="white-space:pre-wrap;overflow-wrap:anywhere">${esc(JSON.stringify(r.raw,null,2))}</pre></details>`).join(''):'';}
async function reanalyzeLegacy(id){if(!confirm('将按训练页当前选择的场景、对象与目标分析旧对话；原记录与旧评分保持原样。是否继续？'))return;lock(true,'正在重新分析旧记录…');const rid=crypto.randomUUID();try{applySession(await action('reanalyze-legacy',{requestId:rid,legacyId:id,sceneId,objectId:$('objectSelect').value,goal:$('goal').value}));await refresh();}catch(e){try{applySession(await request('/api/workplace/session?id='+rid));}catch{}showError('globalError',e.message);}finally{lock(false);}}
async function openSession(id){applySession(await request('/api/workplace/session?id='+encodeURIComponent(id)));$('sessionPanel').scrollIntoView({behavior:'smooth'});}
async function sessionOperation(op,data={}){
 if(busy||!session)return;
 const id=session.id,revision=session.revision;
 if(op==='review'){
  markReviewIntent(id);reviewLocalErrors.delete(id);reviewBusyId=id;
  showError('globalError','');renderSession();$('review').scrollIntoView({behavior:'instant',block:'start'});
 }
 lock(true,op==='review'?'正在生成复盘…':'模型生成中，请稍候…');showError('sessionError','');
 try{
  const updated=await action(op,{sessionId:id,revision,...data});
  if(session?.id===id){reviewLocalErrors.delete(id);applySession(updated);}
  await refresh();
 }catch(e){
  const reviewMode=op==='review'||isReviewFlow(session);
  if(reviewMode)reviewLocalErrors.set(id,e.message);
  try{const updated=await request('/api/workplace/session?id='+encodeURIComponent(id));if(session?.id===id)session=updated;}catch{}
  try{await refresh();}catch{}
  if(!reviewMode)showError('sessionError',e.message);
 }finally{
  if(reviewBusyId===id)reviewBusyId=null;
  if(session?.id===id)renderSession();
  lock(false);
 }
}
const reviewPoll=setInterval(async()=>{
 if(reviewPolling||!session||!isReviewFlow(session)||!(reviewBusyId===session.id||session.status==='review_pending'))return;
 const id=session.id;reviewPolling=true;
 try{const updated=await request('/api/workplace/session?id='+encodeURIComponent(id));if(session?.id===id){session=updated;renderSession();}}catch{}
 finally{reviewPolling=false;}
},1500);
window.addEventListener('pagehide',()=>clearInterval(reviewPoll));

function selectAPI(id){$('apiKey').required=false;$('clearKey').disabled=false;for(const k of ['apiName','apiURL','apiModel','apiReviewModel'])$(k).readOnly=false;apiEditId=id||'';const a=ws.config.apis?.find(a=>a.id===id)||{};$('apiSelect').value=id||'';$('apiName').value=a.name||(id?'':'DeepSeek527');$('apiURL').value=a.baseURL||(id?'':'https://api.deepseek.com');$('apiKey').value='';$('apiKey').placeholder=a.hasKey?'已有密钥 · 留空保留':'可在本机填写；免密本机服务可留空';$('clearKey').checked=false;$('apiModel').value=a.model||(id?'':'deepseek-flash');$('apiReviewModel').value=a.reviewModel||'';$('apiEnabled').checked=a.useLLM!==false;$('apiStatus').textContent=a.id===ws.config.active?'当前启用配置':'';}
function renderAPI(){const apis=ws.config.apis||[];$('apiSelect').innerHTML='<option value="">＋ 新配置</option>'+apis.map(a=>`<option value="${esc(a.id)}">${esc(a.name)}${a.id===ws.config.active?' · 当前':''}</option>`).join('');selectAPI(apiEditId||ws.config.active);}
function download(content,type,name){const u=URL.createObjectURL(new Blob([content],{type})),a=document.createElement('a');a.href=u;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(u),1000);}
async function exportHTML(){if(!session.review)return;const css=await (await fetch('/web/style.css')).text();const content=renderReview(session,true).replace(/<details(?![^>]*\bopen\b)(?=[\s>])/g,'<details open');download(`<!doctype html><html lang="zh-CN" data-theme="${window.CoachTheme.current.id}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>AI职场沟通训练师 · 复盘</title><style>${css}</style></head><body><main class="shell"><article class="panel">${content}<footer>AI职场沟通训练师 · 离线复盘报告</footer></article></main></body></html>`,'text/html;charset=utf-8',`沟通复盘_${session.id.slice(0,8)}.html`);}
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b||(busy&&!visualButton(b)))return;try{if(b.hasAttribute('data-expand-answer')){const box=b.closest('[data-answer]'),open=box.classList.toggle('answers-expanded');b.setAttribute('aria-expanded',String(open));b.textContent=open?'收起完整回答':'展开完整回答';updateAnswerControls();}if(b.dataset.reviewDetails)await sessionOperation('review-details');if(b.dataset.reviewRetry)await sessionOperation('review');if(b.dataset.reviewBind)await sessionOperation('use-current-api');if(b.dataset.freeExample){$('freeInput').value=b.dataset.freeExample;$('freeInput').focus();}if(b.dataset.openMeeting)await openMeeting(b.dataset.openMeeting);if(b.dataset.tab)showTab(b.dataset.tab);if(b.dataset.category){cat=b.dataset.category;chooseScene(ws.scenes.find(s=>s.cat===cat).id);}if(b.dataset.scene)chooseScene(b.dataset.scene);if(b.dataset.objectQuotes)openQuotes(b.dataset.objectQuotes);if(b.dataset.editObject)openObject(b.dataset.editObject);if(b.dataset.deleteObject)await deleteObject(b.dataset.deleteObject);if(b.dataset.createObject)openObject();if(b.dataset.themeChoice){window.CoachTheme.set(b.dataset.themeChoice);renderThemes();$('themeChoices').querySelector('[aria-pressed="true"]').focus();}if(b.dataset.openSession)await openSession(b.dataset.openSession);if(b.dataset.reanalyze)await reanalyzeLegacy(b.dataset.reanalyze);if(b.dataset.close)$(b.dataset.close).close();}catch(e){toast(e.message);}});
function renderThemes(){
 const active=window.CoachTheme.current;
 $('themeName').textContent=active.name;
 $('themeChoices').innerHTML=window.CoachTheme.themes.map(t=>`<button class="theme-choice" data-theme-choice="${t.id}" aria-pressed="${active.id===t.id}"><span class="theme-swatch" style="--swatch-bg:${t.colors[0]};--swatch-brand:${t.colors[1]};--swatch-accent:${t.colors[2]}"><i></i><i></i><i></i></span><span class="theme-title">${esc(t.name)}<span class="theme-check" aria-hidden="true">${active.id===t.id?'✓':''}</span></span><small>${esc(t.note)}</small></button>`).join('');
 $('themeStatus').textContent='当前主题：'+active.name+' · 导出报告沿用此主题。';
}
renderThemes();
window.addEventListener('coach-theme-change',renderThemes);
$('themeOpen').onclick=()=>{renderThemes();$('themeDialog').showModal();};
$('quotesSave').onclick=()=>saveQuotes(false);$('quotesAnalyze').onclick=()=>saveQuotes(true);
$('objectSelect').onchange=renderFocus;$('newObject').onclick=()=>openObject();$('editSelected').onclick=()=>openObject($('objectSelect').value);
$('objectForm').onsubmit=async e=>{e.preventDefault();if(busy)return;lock(true,'正在保存画像…');try{const o=Object.fromEntries(new FormData(e.target));if(objectEditId)o.id=objectEditId;await action('object',{object:o});await refresh();$('objectDialog').close();toast('画像已保存；已有训练快照保持不变。');}catch(e){$('objectStatus').textContent=e.message;}finally{lock(false);}};
$('start').onclick=async()=>{if(busy)return;lock(true);showError('globalError','');const rid=crypto.randomUUID();try{applySession(await action('start',{requestId:rid,sceneId,objectId:$('objectSelect').value,goal:$('goal').value,background:$('background').value,projectId:$('projectSelect').value,intensity:$('intensity').value}));await refresh();$('sessionPanel').scrollIntoView({behavior:'smooth'});}catch(e){try{applySession(await request('/api/workplace/session?id='+encodeURIComponent(rid)));}catch{}try{await refresh();}catch{}showError(session?.id===rid?'sessionError':'globalError',e.message);}finally{lock(false);}};
$('reply').oninput=syncSessionButtons;$('send').onclick=async()=>{const t=$('reply').value.trim();if(!t||busy)return;await sessionOperation('send',{text:t});if(session?.messages.some(m=>m.role==='user'&&m.text===t))$('reply').value='';syncSessionButtons();};$('reply').onkeydown=e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();$('send').click();}};
$('useCurrentAPI').onclick=async()=>{await sessionOperation('use-current-api');if(!session?.error)toast('本轮已使用当前 API 配置。请重试模型回应或继续训练。');};
$('retry').onclick=()=>sessionOperation('retry');$('end').onclick=()=>sessionOperation('review');$('cancel').onclick=async()=>{if(confirm('中断本轮？已提交原话会保留，可在记录中查看。'))await sessionOperation('cancel');};
function backToSelection(){document.body.classList.remove('session-active');session=null;localStorage.removeItem('workplace_active_session');$('selection').hidden=false;$('sessionPanel').hidden=true;showTab('practice');renderSelection();$('workspace').scrollIntoView({behavior:'smooth'});}
$('back').onclick=backToSelection;$('again').onclick=()=>{const s=session;chooseScene(s.scene.id);$('objectSelect').value=s.object.id;$('goal').value=s.goal;$('background').value=s.background;$('projectSelect').value=s.project?.id||'';$('intensity').value=s.intensity;backToSelection();toast('本次再练将冻结最新对象画像，请点击进入连续对话。');};
$('copyExample').onclick=async()=>{try{await navigator.clipboard.writeText($('exampleText').textContent);toast('已复制虚构示例，尚未提交到训练。');}catch{toast('复制失败，可选择示例文字手动复制。');}};
$('exportHTML').onclick=()=>exportHTML().catch(e=>toast(e.message));$('exportJSON').onclick=()=>download(JSON.stringify(session,null,2),'application/json',`沟通记录_${session.id.slice(0,8)}.json`);$('print').onclick=()=>window.print();
let printState=null;window.addEventListener('beforeprint',()=>{const details=[...$('review').querySelectorAll('details')];printState=details.map(d=>[d,d.open]);details.forEach(d=>d.open=true);});window.addEventListener('afterprint',()=>{for(const [d,opened] of printState||[])d.open=opened;printState=null;});
$('portraitRetry').onclick=async()=>{if(busy)return;lock(true,'正在更新长期画像…');try{await action('portrait');toast('画像已更新');}catch(e){toast(e.message);}finally{await refresh();lock(false);}};
$('apiOpen').onclick=()=>{renderAPI();$('apiDialog').showModal();};$('apiSelect').onchange=e=>selectAPI(e.target.value);$('apiNew').onclick=()=>selectAPI('');
$('apiForm').onsubmit=async e=>{e.preventDefault();if(busy)return;lock(true,'正在保存本机配置…');try{const api={id:apiEditId,name:$('apiName').value,baseURL:$('apiURL').value,apiKey:$('apiKey').value,clearKey:$('clearKey').checked,model:$('apiModel').value,reviewModel:$('apiReviewModel').value,useLLM:$('apiEnabled').checked};const saved=await action('config',{api});apiEditId=saved.active;$('apiKey').value='';await refresh();renderAPI();$('apiStatus').textContent='已保存并启用。可测试连接。';}catch(e){$('apiStatus').textContent=e.message;}finally{lock(false);}};
for(const [id,operation] of [['apiActivate','activate'],['apiDelete','delete']])$(id).onclick=async()=>{if(!apiEditId){toast('请先选择配置');return;}if(operation==='delete'&&!confirm('删除此 API 配置？请确认已有备份。'))return;lock(true,'正在保存配置…');try{await action('config',{configOperation:operation,id:apiEditId});apiEditId='';await refresh();renderAPI();}catch(e){$('apiStatus').textContent=e.message;}finally{lock(false);}};
$('apiTest').onclick=async()=>{if(!apiEditId){$('apiStatus').textContent='请先保存配置再测试。';return;}lock(true,'正在测试模型连接…');$('apiStatus').textContent='正在请求已保存模型…';try{const r=await action('test',{apiId:apiEditId});$('apiStatus').textContent='连接测试通过 · '+r.model;showError('globalError','');if(session?.status==='active'){renderSession();if(session.apiId!==apiEditId)$('apiStatus').textContent+='。本轮仍绑定旧配置：关闭设置后点击「使用当前 API 配置」，再重试。';}}catch(e){$('apiStatus').textContent=e.message;}finally{lock(false);}};
$('importHistory').onclick=()=>$('legacyFile').click();$('legacyFile').onchange=async e=>{const f=e.target.files[0];if(!f)return;lock(true,'正在保留旧版记录…');try{const record=JSON.parse(await f.text());await action('import-legacy',{record,label:f.name});await refresh();toast('旧版原数据已保留，未补造新分数。');}catch(e){toast(e.message);}finally{lock(false);e.target.value='';}};

function renderExperiences(){
 const query=$('experienceSearch').value.trim().toLowerCase();
 const items=(ws.experiences||[]).filter(e=>(e.title+' '+e.content+' '+e.category).toLowerCase().includes(query));
 $('experienceCards').innerHTML=items.map(e=>`<article class="experience-card"><div class="experience-meta"><span>${esc(e.category)}</span><small>${esc(e.source||'用户导入')}</small></div><h3>${esc(e.title)}</h3><p>${esc(brief(e.content,140))}</p><details><summary>查看完整经验</summary><p class="experience-content">${esc(e.content)}</p>${e.meetingId?`<p class="muted">从会议纪要提炼，需结合适用场景验证。</p>${e.evidence.map(q=>`<blockquote class="quote-evidence">${esc(q)}</blockquote>`).join('')}<button class="outline" data-open-meeting="${esc(e.meetingId)}">查看来源纪要</button>`:''}</details></article>`).join('')||'<p class="empty">没有找到经验，可添加或在下方直接输入。</p>';
}
function renderFreeHistory(){
 $('freeHistory').innerHTML=(ws.commands||[]).map(c=>`<article class="free-log"><small>${esc(stamp(c.at))}</small><p>${esc(brief(c.text,100))}</p>${c.clarification?`<p class="muted">待补充：${esc(c.clarification)}</p>`:`<ul>${c.changes.map(t=>`<li>${esc(t)}</li>`).join('')}</ul>`}</article>`).join('')||'<p class="muted">办理结果会保存在这里。</p>';
}
$('experienceSearch').oninput=renderExperiences;
$('newExperience').onclick=()=>{$('experienceForm').reset();$('experienceStatus').textContent='';$('experienceDialog').showModal();};
$('experienceForm').onsubmit=async e=>{
 e.preventDefault();if(busy)return;lock(true,'正在保存经验…');
 try{const result=await action('import-experiences',{entries:[{title:$('experienceName').value,category:$('experienceCategory').value,content:$('experienceContent').value}]});await refresh();$('experienceDialog').close();toast(result.added?'经验已保存，将供新训练参考。':'相同经验已存在。');}catch(e){$('experienceStatus').textContent=e.message;}finally{lock(false);}
};
$('importExperience').onclick=()=>$('experienceFile').click();
$('experienceFile').onchange=async e=>{
 const file=e.target.files[0];if(!file||busy)return;
 if(file.size>1000000){toast('请选择 1 MB 以内的文本或 JSON 文件。');e.target.value='';return;}
 lock(true,'正在导入沟通经验…');
 try{const raw=await file.text();let entries;
  if(file.name.toLowerCase().endsWith('.json')){const data=JSON.parse(raw);entries=Array.isArray(data)?data:data.experiences;if(!Array.isArray(entries))throw Error('JSON 需为经验数组，或包含 experiences 数组。');}
  else entries=[{title:file.name.replace(/\.(txt|md)$/i,''),content:raw,category:'通用沟通'}];
  const result=await action('import-experiences',{entries});await refresh();toast(`已导入 ${result.added} 条，跳过重复 ${result.skipped} 条。`);
 }catch(e){toast(e.message);}finally{lock(false);e.target.value='';}
};
$('exportExperiences').onclick=()=>download(JSON.stringify(ws.experiences,null,2),'application/json','沟通经验库.json');
$('freeNew').onclick=()=>{freePreviousId='';$('freeNew').hidden=true;$('freeInput').value='';$('freeResult').replaceChildren();$('freeStatus').textContent='已另起需求，请输入。';$('freeInput').focus();};
$('freeForm').onsubmit=async e=>{
 e.preventDefault();const input=$('freeInput').value.trim();if(busy||!input)return;
 lock(true,'AI 正在整理你的需求…');$('freeResult').replaceChildren();$('freeStatus').textContent='正在识别对象与要修改的内容，请稍候…';
 try{const result=await action('free-command',{text:input,previousId:freePreviousId,sessionId:session?.id,revision:session?.revision});
  if(result.session&&session?.id===result.session.id){session=result.session;renderSession();}
  if(result.intensity)$('intensity').value=result.intensity;
  freePreviousId=result.clarification?result.id:'';$('freeNew').hidden=!freePreviousId;
  $('freeResult').innerHTML=result.clarification?`<div class="free-result clarification"><b>还需要确认一点</b><p>${esc(result.clarification)}</p><small>直接在上方补充回答即可，此前没有修改资料。</small></div>`:`<div class="free-result"><b>已办理</b><ul>${result.changes.map(t=>`<li>${esc(t)}</li>`).join('')}</ul><small>对象画像与经验用于新训练，已有对话和评分保留。</small></div>`;
  $('freeInput').value='';$('freeStatus').textContent=result.clarification?'请补充回答，或另起一个需求。':'已保存，可以继续输入新的需求。';
  await refresh();
 }catch(e){$('freeStatus').textContent='未保存修改：'+e.message;}
 finally{lock(false);}
};
$('freeInput').onkeydown=e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();$('freeForm').requestSubmit();}};
$('intensity').onchange=async()=>{if(busy)return;try{await action('training-preferences',{intensity:$('intensity').value});}catch(e){toast(e.message);}};

function renderMeetings(){
 const selected=$('projectSelect').value;
 $('projectSelect').innerHTML='<option value="">不引用已保存项目</option>'+(ws.projects||[]).map(p=>`<option value="${esc(p.id)}">${esc(p.name)}</option>`).join('');
 $('projectSelect').value=(ws.projects||[]).some(p=>p.id===selected)?selected:'';
 $('projectCards').innerHTML=(ws.projects||[]).map(p=>`<details><summary>${esc(p.name)}</summary><p class="experience-content">${esc(p.background)}</p><p class="muted">${p.sources.length} 条纪要依据 · 更新于 ${esc(stamp(p.updated))}</p>${[...new Set(p.sources.map(x=>x.meetingId))].map(id=>`<button class="outline" data-open-meeting="${esc(id)}">查看来源纪要</button>`).join('')}</details>`).join('')||'<p class="muted">保存提取结果中的项目背景后，会在这里显示。</p>';
 $('meetingRecords').innerHTML=(ws.meetings||[]).map(m=>`<article class="record"><div><h3>${esc(m.title)}</h3><p class="muted">${esc(stamp(m.at))} · ${m.appliedItems.length?`已保存 ${m.appliedItems.length} 项`:'等待核对'}<br>${esc(brief(m.summary,100))}</p></div><button class="outline" data-open-meeting="${esc(m.id)}">查看提取与原文</button></article>`).join('')||'<p class="empty">还没有导入会议纪要。</p>';
}
function meetingEvidence(item){return `<details class="meeting-evidence"><summary>查看原文依据</summary>${item.evidence.map(q=>`<blockquote class="quote-evidence">${esc(q)}</blockquote>`).join('')}</details>`;}
function renderMeetingPreview(){
 const m=meetingDraft;if(!m){$('meetingPreview').hidden=true;$('meetingPreview').replaceChildren();return;}
 $('meetingPreview').hidden=false;const saved=new Set(m.appliedItems),names=[...new Set(m.items.filter(i=>['observation','quote'].includes(i.kind)).map(i=>i.name))];
 let html=`<div class="section-heading"><p class="eyebrow">先核对，再收录</p><h2>${esc(m.title)}</h2><p>${esc(m.summary)}</p><p class="muted">勾选需要保存的条目。画像会追加并注明来源，已有训练不改写。纪要中的记载语句不等同于录音逐字稿。</p></div>`;
 for(const name of names){
  const items=m.items.filter(i=>i.name===name&&['observation','quote'].includes(i.kind));
  const target=m.targets[name]||items[0].objectId||(items[0].ambiguous?'':'new');
  html+=`<section class="meeting-group"><div class="meeting-person"><div><h3>${esc(name)}</h3><p class="muted">${esc(ws.objects.find(o=>o.id===target)?.role||items.find(i=>i.role!=='会议相关人员（角色待确认）')?.role||items[0].role)}</p></div><label>归入哪个对象<select data-meeting-target="${esc(name)}"><option value="">请选择归属</option>${ws.objects.map(o=>`<option value="${esc(o.id)}" ${o.id===target?'selected':''}>${esc(o.name)}</option>`).join('')}<option value="new" ${target==='new'?'selected':''}>新建对象：${esc(name)}</option></select></label></div>${items.map(item=>`<article class="meeting-item"><label class="check"><input type="checkbox" data-meeting-item="${item.id}" ${saved.has(item.id)?'disabled data-applied="1"':'checked'}><span><small class="meeting-kind">${saved.has(item.id)?'已保存 · ':''}${item.kind==='quote'?'纪要记载语句':item.certainty==='inferred'?'AI 特征推测 · '+esc(objectLabels[item.field]):'纪要观察 · '+esc(objectLabels[item.field])}</small><p>${esc(item.text)}</p></span></label>${meetingEvidence(item)}</article>`).join('')}</section>`;
 }
 for(const kind of ['project','experience']){
  const items=m.items.filter(i=>i.kind===kind);if(!items.length)continue;
  html+=`<section class="meeting-group"><h3>${kind==='project'?'项目背景与行动项':'可复用沟通经验'}</h3>${items.map(item=>`<article class="meeting-item"><label class="check"><input type="checkbox" data-meeting-item="${item.id}" ${saved.has(item.id)?'disabled data-applied="1"':'checked'}><span><small class="meeting-kind">${saved.has(item.id)?'已保存 · ':''}${kind==='project'?esc(item.name):esc(item.title)+' · '+esc(item.category)}</small><p>${esc(item.text||item.content)}</p></span></label>${kind==='project'?`<label class="meeting-project-target">归入项目<select data-meeting-project="${esc(item.name)}"><option value="new">新建项目：${esc(item.name)}</option>${(ws.projects||[]).map(p=>`<option value="${esc(p.id)}" ${(m.projectTargets[item.name]||item.projectId)===p.id?'selected':''}>${esc(p.name)}</option>`).join('')}</select></label>`:''}${meetingEvidence(item)}</article>`).join('')}</section>`;
 }
 html+=`<p id="meetingApplyStatus" role="status" class="muted"></p><div class="actions"><button id="meetingApply" class="primary" ${m.items.every(i=>saved.has(i.id))?'disabled':''}>保存勾选结果</button><span class="muted">已保存 ${saved.size} / ${m.items.length} 项；未勾选的条目可稍后继续保存。</span></div><details><summary>查看完整纪要原文</summary><p class="meeting-original">${esc(m.text)}</p></details>`;
 $('meetingPreview').innerHTML=html;
 $('meetingApply').onclick=applyMeeting;
}
async function openMeeting(id){
 meetingDraft=await request('/api/workplace/meeting?id='+encodeURIComponent(id));renderMeetingPreview();showTab('meetings');$('meetingPreview').scrollIntoView({behavior:'smooth'});
}
$('projectSelect').onchange=()=>{const project=(ws.projects||[]).find(p=>p.id===$('projectSelect').value);if(project)$('background').value=project.background;};
function clearMeetingPreview(){meetingDraft=null;renderMeetingPreview();}
$('meetingText').oninput=clearMeetingPreview;$('meetingTitle').oninput=clearMeetingPreview;
$('meetingFileOpen').onclick=()=>$('meetingFile').click();
$('meetingFile').onchange=async e=>{
 const file=e.target.files[0];if(!file||busy)return;if(file.size>5000000){$('meetingStatus').textContent='文件最大 5 MB，请精简后重试。';e.target.value='';return;}
 lock(true,'正在读取会议纪要…');$('meetingStatus').textContent='正在读取文件正文…';
 try{const bytes=new Uint8Array(await file.arrayBuffer());let binary='';for(let i=0;i<bytes.length;i+=16384)binary+=String.fromCharCode(...bytes.subarray(i,i+16384));
  const parsed=await action('meeting-file',{filename:file.name,data:btoa(binary)});$('meetingText').value=parsed.text;$('meetingTitle').value=parsed.title;clearMeetingPreview();$('meetingStatus').textContent='已读取正文。可先脱敏或修改，再点击 AI 提取并预览。';
 }catch(e){$('meetingStatus').textContent=e.message;}finally{lock(false);e.target.value='';}
};
$('meetingForm').onsubmit=async e=>{
 e.preventDefault();if(busy||!$('meetingText').value.trim())return;clearMeetingPreview();lock(true,'正在提取会议纪要…');$('meetingStatus').textContent='AI 正在整理人物、项目与沟通经验，尚未修改画像或背景…';
 try{meetingDraft=await action('meeting-analyze',{title:$('meetingTitle').value,text:$('meetingText').value});renderMeetingPreview();await refresh();$('meetingStatus').textContent=meetingDraft.items.length?'提取结果已保留，请核对人物归属和原文依据后保存。':'本次未提取到可保存条目。可补充人物、项目或决议后重试。';$('meetingPreview').scrollIntoView({behavior:'smooth'});}
 catch(e){$('meetingStatus').textContent='尚未更新资料：'+e.message;}finally{lock(false);}
};
async function applyMeeting(){
 if(busy||!meetingDraft)return;
 const selected=[...$('meetingPreview').querySelectorAll('[data-meeting-item]:checked')].map(el=>el.dataset.meetingItem);
 if(!selected.length){$('meetingApplyStatus').textContent='请至少勾选一项尚未保存的结果。';return;}
 const targets=Object.fromEntries([...$('meetingPreview').querySelectorAll('[data-meeting-target]')].map(el=>[el.dataset.meetingTarget,el.value]));
 const projectTargets=Object.fromEntries([...$('meetingPreview').querySelectorAll('[data-meeting-project]')].map(el=>[el.dataset.meetingProject,el.value]));
 lock(true,'正在保存纪要提取结果…');
 try{const result=await action('meeting-apply',{meetingId:meetingDraft.id,selected,targets,projectTargets});meetingDraft=result.meeting;await refresh();renderMeetingPreview();$('meetingApplyStatus').textContent=result.applied?`已保存 ${result.applied} 项：`+result.changes.join('；'):'这些条目此前已保存，没有重复追加。';}
 catch(e){$('meetingApplyStatus').textContent='未保存本次修改：'+e.message;}finally{lock(false);$('meetingApply').disabled=meetingDraft.items.every(i=>meetingDraft.appliedItems.includes(i.id));}
}
(async()=>{try{await refresh();let old=null;try{old=JSON.parse(localStorage.getItem('ahc_api_cfg_v1'));}catch{}if(old&&!ws.config.apis?.length){await action('import-config',{config:old});await refresh();}const id=localStorage.getItem('workplace_active_session');if(id){try{applySession(await request('/api/workplace/session?id='+encodeURIComponent(id)));}catch{localStorage.removeItem('workplace_active_session');}}}catch(e){showError('globalError',e.message);}})();
