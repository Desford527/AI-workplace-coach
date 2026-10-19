'use strict';
const $=id=>document.getElementById(id), esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
let ws=null,sceneId='progress',cat='report',session=null,busy=false,currentTab='practice',apiEditId='',objectEditId='',toastTimer;
let reviewBusyId=null,reviewPolling=false;const reviewIntent=new Set(),reviewLocalErrors=new Map();
const categories=[['report','项目汇报','Project briefing'],['technical','技术评审','Technical review'],['customer','客户沟通','Customer dialogue'],['english','国际协作','Global collaboration']];
const objectLabels={name:'称呼',role:'角色 / 工作关系',goals:'工作目标',standards:'关注点 / 判断标准',style:'表达风格',quotes:'典型原话（可选）',difficulty:'沟通难点（可选）',facts:'已知事实 / 来源',inferences:'推断 / 虚拟补充',boundaries:'模拟边界'};
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
function lock(value,note='模型生成中，请稍候…'){busy=value;document.querySelectorAll('button').forEach(b=>b.disabled=value&&!visualButton(b));$('reply').disabled=value;$('modelStatus').textContent=value?note:'';if(!value)syncSessionButtons();}
function isReviewFlow(s){return !!s&&(!!s.review||!!s.reviewStatus||['review_pending','review_failed','ended'].includes(s.status)||reviewIntent.has(s.id)||localStorage.getItem('workplace_review_intent:'+s.id)==='1');}
function markReviewIntent(id){reviewIntent.add(id);localStorage.setItem('workplace_review_intent:'+id,'1');}
function reviewIsPending(s){return reviewBusyId===s.id||(s.status==='review_pending'&&!reviewLocalErrors.has(s.id));}
function syncSessionButtons(){
 $('start').disabled=busy||!ws?.objects?.length;$('objectSelect').disabled=busy||!ws?.objects?.length;
 if(!session)return;
 const active=session.status==='active'&&!isReviewFlow(session),pending=!session.messages.length||session.messages.at(-1)?.role==='user';
 $('send').disabled=busy||!active||pending||!$('reply').value.trim();$('end').disabled=busy||!active;
 $('retry').hidden=!active||!pending;$('retry').disabled=busy;$('cancel').hidden=!active;
 for(const b of $('review').querySelectorAll('button'))b.disabled=b.hasAttribute('data-expand-answer')?false:busy||reviewIsPending(session);
}

async function refresh(){ws=await request('/api/workplace/workspace');renderWorkspace();return ws;}
function renderWorkspace(){renderSelection();renderObjects();renderPortrait();renderRecords();const c=ws.config.apis?.find(a=>a.id===ws.config.active);$('apiBadge').textContent=c?c.name:'未配置';}
function selectedScene(){return ws.scenes.find(s=>s.id===sceneId)||ws.scenes[0];}
function defaultObject(s){const preferred={report:'builtin-project',technical:'builtin-technical',customer:'builtin-customer',english:'builtin-global'}[s.cat];return ws.objects.some(o=>o.id===preferred)?preferred:ws.objects[0]?.id||'';}
function renderSelection(){if(!ws)return;const s=selectedScene();$('categories').innerHTML=categories.map(([id,name,en],i)=>`<button class="category ${id===cat?'active':''}" data-category="${id}" aria-pressed="${id===cat}"><span class="category-index">0${i+1}</span><span><strong>${name}</strong><small>${en}</small></span></button>`).join('');$('scenes').innerHTML=ws.scenes.filter(s=>s.cat===cat).map(s=>`<button class="scene ${s.id===sceneId?'active':''}" data-scene="${s.id}" aria-pressed="${s.id===sceneId}"><strong>${esc(s.title)}</strong><small>${esc(s.short)}</small></button>`).join('');$('sceneTitle').textContent=s.title;$('sceneDescription').textContent=s.description;$('previewOpening').textContent=s.opening;$('previewRole').textContent=s.role;const old=$('objectSelect').value;$('objectSelect').innerHTML=ws.objects.map(o=>`<option value="${esc(o.id)}">${esc(o.name)} · ${esc(o.role)}</option>`).join('')||'<option value="">暂无可选对象</option>';$('objectSelect').value=ws.objects.some(o=>o.id===old)?old:defaultObject(s);if(!$('goal').value)$('goal').value=s.goal;$('noObjects').hidden=!!ws.objects.length;$('objectFocus').hidden=!ws.objects.length;renderFocus();syncSessionButtons();}
function chooseScene(id){sceneId=id;cat=selectedScene().cat;$('goal').value=selectedScene().goal;$('objectSelect').value=defaultObject(selectedScene());renderSelection();}
function objectFacts(o){return Object.entries(objectLabels).filter(([k])=>!['name','role'].includes(k)).map(([k,label])=>`<p><b>${label}</b><br>${esc(o[k]||'尚未补充')}</p>`).join('');}
function renderFocus(){const o=ws.objects.find(p=>p.id===$('objectSelect').value);$('focusContent').innerHTML=o?objectFacts(o):'';}
function showTab(id){currentTab=id;document.querySelectorAll('.view').forEach(v=>v.hidden=v.id!==id);document.querySelectorAll('[data-tab]').forEach(b=>b.classList.toggle('active',b.dataset.tab===id));}
function renderObjects(){$('objectCards').innerHTML=ws.objects.map(o=>`<article class="object-card"><div class="object-card-top"><span class="profile-avatar">${esc(o.name.slice(0,1))}</span><span class="object-kind">沟通对象</span></div><h3>${esc(o.name)}</h3><p class="muted">${esc(o.role)}</p><p>${esc(brief(o.goals,90))}</p><details><summary>画像详情 · 事实与推断</summary>${objectFacts(o)}</details><div class="actions object-actions"><button class="outline" data-edit-object="${esc(o.id)}">编辑画像</button><button class="delete-object" data-delete-object="${esc(o.id)}">删除对象</button></div></article>`).join('')||'<div class="empty"><h3>给下一次沟通，选一个新对象。</h3><p>已删除对象的训练记录仍可在「训练记录」查看。</p></div>';}
async function deleteObject(id){
 const o=ws.objects.find(p=>p.id===id);if(!o||busy)return;
 if(!confirm(`删除「${o.name}」？该对象将从可选名单移除，已有对话、复盘和画像证据保留。`))return;
 lock(true,'正在删除对象…');
 try{await action('delete-object',{objectId:id});await refresh();toast('对象已删除，已有训练记录保留。');}
 catch(e){toast(e.message);}
 finally{lock(false);}
}
function openObject(id){const o=ws.objects.find(p=>p.id===id)||{};objectEditId=o.id||'';$('objectDialogTitle').textContent=o.id?'编辑对象画像':'新建对象画像';$('objectFields').innerHTML=Object.entries(objectLabels).map(([k,label])=>`<label>${label}${['name','role'].includes(k)?`<input name="${k}" value="${esc(o[k]||'')}" required maxlength="200">`:`<textarea name="${k}" rows="2" ${['quotes','difficulty'].includes(k)?'':'required'}>${esc(o[k]||(k==='facts'?'虚拟训练对象，不对应现实人物':k==='inferences'?'仅用于本场景模拟的推断':k==='boundaries'?'尊重对方，不羞辱、不作人格攻击':''))}</textarea>`}</label>`).join('');$('objectStatus').textContent='';$('objectDialog').showModal();}
function applySession(s){document.body.classList.add('session-active');session=s;localStorage.setItem('workplace_active_session',s.id);$('selection').hidden=true;$('sessionPanel').hidden=false;showTab('practice');renderSession();}
function renderSession(){
 if(!session)return;const s=session,reviewMode=isReviewFlow(s);$('sessionPanel').classList.toggle('is-review',reviewMode);
 $('sessionPhase').textContent=reviewMode?'03 / 结束与复盘':'02 / 连续对话';
 $('sessionTitle').textContent=reviewMode?'本次训练复盘':s.object.name;
 const state=reviewMode?(s.review?'已完成复盘':reviewIsPending(s)?'训练已结束 · 正在生成复盘':'训练已结束 · 对话已保留'):s.status==='archived'?'已中断，记录保留':'训练进行中';
 $('sessionMeta').textContent=`${s.scene.title} · ${s.scene.lang==='en'?'英文对话 / 中文复盘':'中文对话'} · ${state}`;
 $('snapshot').innerHTML=`<p><b>本轮目标</b><br>${esc(s.goal)}</p><p><b>背景</b><br>${esc(s.background||'未提供')}</p>${objectFacts(s.object)}`;
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
 return `<header class="review-head review-stage-card"><span class="stage-symbol" aria-hidden="true">↗</span><div><p class="eyebrow">03 / 结束与复盘</p><h2>${title}</h2><p>${esc(note)}</p></div></header>
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
 <section class="review-section radar-section">${reportHeading('01','六维表现','先看图，再看具体依据')}
 <div class="radar-layout"><div>${radar(r.dims)}<div class="radar-legend"><span><i class="legend-actual"></i>本轮 AI 评分</span><span><i class="legend-reference"></i>60 分参考线</span></div></div><div class="dimension-meters">${scoreLines(r.dims)}<p class="muted">每维 0–100 分，数值来自本轮 AI 复盘。</p></div></div>
 <details class="dimension-details" data-detail="dimensions"><summary>展开六维依据与原话证据</summary>${r.dims.map(dimension).join('')}</details></section>
 <section class="review-section issues-section">${reportHeading('02','先改这几个关键点','把建议落到下一次表达')}
 <div class="issue-grid">${r.loss.slice(0,2).map(issueCard).join('')||'<p class="muted">模型未列出单独的问题清单，可查看下方逐轮反馈。</p>'}</div>
 ${moreIssues.length?`<details class="more-issues" data-detail="more-issues"><summary>其余模型观察（${moreIssues.length}）</summary><div class="issue-grid">${moreIssues.map((l,i)=>issueCard(l,i+2)).join('')}</div></details>`:''}</section>
 <section class="review-section rounds-section">${reportHeading('03','逐轮回看，换一种表达','原话、反馈与示范放在一起')}
 ${r.timeline.map((t,i)=>`<details class="round" data-detail="round-${i}" ${i===0?'open':''}><summary><span class="round-index">${String(i+1).padStart(2,'0')}</span><span>回应 ${i+1}</span><span class="round-score">${t.score}<small> / 100</small></span></summary><div class="round-body">
 <p class="round-feedback">${esc(brief(t.feedback,100))}</p>
 <div class="answer-comparison ${expanded?'answers-expanded':''}" data-answer="${i}"><div class="answer-box answer-original"><span class="answer-label">原回答</span><p class="answer-copy original">${esc(quoteFor(s,t.messageId))}</p></div><div class="answer-box answer-improved demo"><span class="answer-label">改进示范${s.scene.lang==='en'?' · English':''}</span><p class="answer-copy">${esc(t.improved)}</p></div>${!expanded?'<button class="text-button" data-expand-answer="1" aria-expanded="false">展开完整回答</button>':''}</div>
 <details class="round-evidence" data-detail="round-evidence-${i}"><summary>查看完整点评与本轮六维依据</summary><p>${esc(t.feedback)}</p>${scoreLines(t.dims)}${t.dims.map(dimension).join('')}</details></div></details>`).join('')}</section>
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
document.addEventListener('click',async e=>{const b=e.target.closest('button');if(!b||(busy&&!visualButton(b)))return;try{if(b.hasAttribute('data-expand-answer')){const box=b.closest('[data-answer]'),open=box.classList.toggle('answers-expanded');b.setAttribute('aria-expanded',String(open));b.textContent=open?'收起完整回答':'展开完整回答';updateAnswerControls();}if(b.dataset.reviewRetry)await sessionOperation('review');if(b.dataset.reviewBind)await sessionOperation('use-current-api');if(b.dataset.tab)showTab(b.dataset.tab);if(b.dataset.category){cat=b.dataset.category;chooseScene(ws.scenes.find(s=>s.cat===cat).id);}if(b.dataset.scene)chooseScene(b.dataset.scene);if(b.dataset.editObject)openObject(b.dataset.editObject);if(b.dataset.deleteObject)await deleteObject(b.dataset.deleteObject);if(b.dataset.createObject)openObject();if(b.dataset.themeChoice){window.CoachTheme.set(b.dataset.themeChoice);renderThemes();$('themeChoices').querySelector('[aria-pressed="true"]').focus();}if(b.dataset.openSession)await openSession(b.dataset.openSession);if(b.dataset.reanalyze)await reanalyzeLegacy(b.dataset.reanalyze);if(b.dataset.close)$(b.dataset.close).close();}catch(e){toast(e.message);}});
function renderThemes(){
 const active=window.CoachTheme.current;
 $('themeName').textContent=active.name;
 $('themeChoices').innerHTML=window.CoachTheme.themes.map(t=>`<button class="theme-choice" data-theme-choice="${t.id}" aria-pressed="${active.id===t.id}"><span class="theme-swatch" style="--swatch-bg:${t.colors[0]};--swatch-brand:${t.colors[1]};--swatch-accent:${t.colors[2]}"><i></i><i></i><i></i></span><span class="theme-title">${esc(t.name)}<span class="theme-check" aria-hidden="true">${active.id===t.id?'✓':''}</span></span><small>${esc(t.note)}</small></button>`).join('');
 $('themeStatus').textContent='当前主题：'+active.name+' · 导出报告沿用此主题。';
}
renderThemes();
window.addEventListener('coach-theme-change',renderThemes);
$('themeOpen').onclick=()=>{renderThemes();$('themeDialog').showModal();};
$('objectSelect').onchange=renderFocus;$('newObject').onclick=()=>openObject();$('editSelected').onclick=()=>openObject($('objectSelect').value);
$('objectForm').onsubmit=async e=>{e.preventDefault();if(busy)return;lock(true,'正在保存画像…');try{const o=Object.fromEntries(new FormData(e.target));if(objectEditId)o.id=objectEditId;await action('object',{object:o});await refresh();$('objectDialog').close();toast('画像已保存；已有训练快照保持不变。');}catch(e){$('objectStatus').textContent=e.message;}finally{lock(false);}};
$('start').onclick=async()=>{if(busy)return;lock(true);showError('globalError','');const rid=crypto.randomUUID();try{applySession(await action('start',{requestId:rid,sceneId,objectId:$('objectSelect').value,goal:$('goal').value,background:$('background').value,intensity:$('intensity').value}));await refresh();$('sessionPanel').scrollIntoView({behavior:'smooth'});}catch(e){try{applySession(await request('/api/workplace/session?id='+encodeURIComponent(rid)));}catch{}try{await refresh();}catch{}showError(session?.id===rid?'sessionError':'globalError',e.message);}finally{lock(false);}};
$('reply').oninput=syncSessionButtons;$('send').onclick=async()=>{const t=$('reply').value.trim();if(!t||busy)return;await sessionOperation('send',{text:t});if(session?.messages.some(m=>m.role==='user'&&m.text===t))$('reply').value='';syncSessionButtons();};$('reply').onkeydown=e=>{if((e.ctrlKey||e.metaKey)&&e.key==='Enter'){e.preventDefault();$('send').click();}};
$('useCurrentAPI').onclick=async()=>{await sessionOperation('use-current-api');if(!session?.error)toast('本轮已使用当前 API 配置。请重试模型回应或继续训练。');};
$('retry').onclick=()=>sessionOperation('retry');$('end').onclick=()=>sessionOperation('review');$('cancel').onclick=async()=>{if(confirm('中断本轮？已提交原话会保留，可在记录中查看。'))await sessionOperation('cancel');};
function backToSelection(){document.body.classList.remove('session-active');session=null;localStorage.removeItem('workplace_active_session');$('selection').hidden=false;$('sessionPanel').hidden=true;showTab('practice');renderSelection();$('workspace').scrollIntoView({behavior:'smooth'});}
$('back').onclick=backToSelection;$('again').onclick=()=>{const s=session;chooseScene(s.scene.id);$('objectSelect').value=s.object.id;$('goal').value=s.goal;$('background').value=s.background;$('intensity').value=s.intensity;backToSelection();toast('本次再练将冻结最新对象画像，请点击进入连续对话。');};
$('copyExample').onclick=async()=>{try{await navigator.clipboard.writeText($('exampleText').textContent);toast('已复制虚构示例，尚未提交到训练。');}catch{toast('复制失败，可选择示例文字手动复制。');}};
$('exportHTML').onclick=()=>exportHTML().catch(e=>toast(e.message));$('exportJSON').onclick=()=>download(JSON.stringify(session,null,2),'application/json',`沟通记录_${session.id.slice(0,8)}.json`);$('print').onclick=()=>window.print();
let printState=null;window.addEventListener('beforeprint',()=>{const details=[...$('review').querySelectorAll('details')];printState=details.map(d=>[d,d.open]);details.forEach(d=>d.open=true);});window.addEventListener('afterprint',()=>{for(const [d,opened] of printState||[])d.open=opened;printState=null;});
$('portraitRetry').onclick=async()=>{if(busy)return;lock(true,'正在更新长期画像…');try{await action('portrait');toast('画像已更新');}catch(e){toast(e.message);}finally{await refresh();lock(false);}};
$('apiOpen').onclick=()=>{renderAPI();$('apiDialog').showModal();};$('apiSelect').onchange=e=>selectAPI(e.target.value);$('apiNew').onclick=()=>selectAPI('');
$('apiForm').onsubmit=async e=>{e.preventDefault();if(busy)return;lock(true,'正在保存本机配置…');try{const api={id:apiEditId,name:$('apiName').value,baseURL:$('apiURL').value,apiKey:$('apiKey').value,clearKey:$('clearKey').checked,model:$('apiModel').value,reviewModel:$('apiReviewModel').value,useLLM:$('apiEnabled').checked};const saved=await action('config',{api});apiEditId=saved.active;$('apiKey').value='';await refresh();renderAPI();$('apiStatus').textContent='已保存并启用。可测试连接。';}catch(e){$('apiStatus').textContent=e.message;}finally{lock(false);}};
for(const [id,operation] of [['apiActivate','activate'],['apiDelete','delete']])$(id).onclick=async()=>{if(!apiEditId){toast('请先选择配置');return;}if(operation==='delete'&&!confirm('删除此 API 配置？请确认已有备份。'))return;lock(true,'正在保存配置…');try{await action('config',{configOperation:operation,id:apiEditId});apiEditId='';await refresh();renderAPI();}catch(e){$('apiStatus').textContent=e.message;}finally{lock(false);}};
$('apiTest').onclick=async()=>{if(!apiEditId){$('apiStatus').textContent='请先保存配置再测试。';return;}lock(true,'正在测试模型连接…');$('apiStatus').textContent='正在请求已保存模型…';try{const r=await action('test',{apiId:apiEditId});$('apiStatus').textContent='连接测试通过 · '+r.model;showError('globalError','');if(session?.status==='active'){renderSession();if(session.apiId!==apiEditId)$('apiStatus').textContent+='。本轮仍绑定旧配置：关闭设置后点击「使用当前 API 配置」，再重试。';}}catch(e){$('apiStatus').textContent=e.message;}finally{lock(false);}};
$('importHistory').onclick=()=>$('legacyFile').click();$('legacyFile').onchange=async e=>{const f=e.target.files[0];if(!f)return;lock(true,'正在保留旧版记录…');try{const record=JSON.parse(await f.text());await action('import-legacy',{record,label:f.name});await refresh();toast('旧版原数据已保留，未补造新分数。');}catch(e){toast(e.message);}finally{lock(false);e.target.value='';}};
(async()=>{try{await refresh();let old=null;try{old=JSON.parse(localStorage.getItem('ahc_api_cfg_v1'));}catch{}if(old&&!ws.config.apis?.length){await action('import-config',{config:old});await refresh();}const id=localStorage.getItem('workplace_active_session');if(id){try{applySession(await request('/api/workplace/session?id='+encodeURIComponent(id)));}catch{localStorage.removeItem('workplace_active_session');}}}catch(e){showError('globalError',e.message);}})();
