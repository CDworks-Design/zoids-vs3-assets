'use strict';
const node=(tag,text,cls)=>{const el=document.createElement(tag);if(text!==undefined)el.textContent=text;if(cls)el.className=cls;return el;};
async function start(){
 const res=await fetch('progress.json',{cache:'no-store'});if(!res.ok)throw Error('Snapshot unavailable');const data=await res.json();
 document.querySelector('#updated').textContent=`Verified snapshot: ${data.snapshot_date} · ${data.scope_note}`;
 for(const m of data.metrics){const el=node('div',undefined,'metric');el.append(node('span',String(m.value),'number'),node('strong',m.label),node('p',m.note,'muted'));document.querySelector('#metrics').append(el);}
 for(const item of data.exports){const el=node('article',undefined,'card');el.append(node('span',item.status,'badge'),node('h3',item.name),node('p',item.detail),node('p',item.limits,'muted'));document.querySelector('#exports').append(el);}
 for(const item of data.systems){const el=node('article',undefined,'card');el.append(node('span',item.status,'badge'),node('h3',item.name),node('p',item.detail),node('p',item.limits,'muted'));document.querySelector('#systems').append(el);}
 const cards=data.sections.map(s=>{const el=node('article',undefined,'card');el.append(node('span',s.status,'badge'),node('h3',s.name),node('p',s.purpose));const dl=node('dl');for(const [label,value]of [['Coverage',s.coverage],['Evidence',s.evidence],['Limits / next check',s.limits]])dl.append(node('dt',label),node('dd',value));el.append(dl);document.querySelector('#sections').append(el);return{el,text:JSON.stringify(s).toLowerCase()};});
 for(const p of data.priorities)document.querySelector('#priorities').append(node('li',p));
 function filter(){const q=document.querySelector('#filter').value.trim().toLowerCase();let n=0;for(const c of cards){c.el.hidden=!c.text.includes(q);if(!c.el.hidden)n++;}document.querySelector('#result-count').textContent=`${n} of ${cards.length} sections shown`;document.querySelector('#empty').hidden=n!==0;}
 document.querySelector('#filter').addEventListener('input',filter);filter();
}
start().catch(()=>{document.querySelector('#updated').textContent='The progress snapshot could not be loaded. Please refresh or try again later.';});
