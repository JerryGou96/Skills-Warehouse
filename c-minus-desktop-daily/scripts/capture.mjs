import { createRequire } from 'node:module';
import { execFileSync } from 'node:child_process';
import path from 'node:path';
import { loadConfig, acquireLock, saveCapture } from './capture-utils.mjs';
const cfg=loadConfig();
const require=createRequire(path.join(cfg.runtime_dir,'package.json'));
const WebSocket=require('ws');
import fs from 'node:fs';
const date=new Intl.DateTimeFormat('en-CA',{timeZone:cfg.timezone,year:'numeric',month:'2-digit',day:'2-digit'}).format(new Date());
const out=path.join(cfg.output_dir,date);fs.mkdirSync(out,{recursive:true});
const releaseLock=acquireLock(out);
const timeout=setTimeout(()=>{console.error('Capture timeout');process.exit(1)},90000);
process.on('exit',()=>{releaseLock();clearTimeout(timeout)});
const endpoint=cfg.cdp_endpoint;
const sourcePath=`discord.com/channels/${cfg.source_guild_id}/${cfg.source_channel_id}`;
try{await fetch(endpoint+'/json',{signal:AbortSignal.timeout(2000)})}catch{
 execFileSync('open',['-a','Discord','--args','--remote-debugging-port='+new URL(endpoint).port]);
 await new Promise(r=>setTimeout(r,5000));
}
execFileSync(path.join(cfg.runtime_dir,'node_modules/.bin/opencli'),['discord-app','status','-f','json'],{env:{...process.env,OPENCLI_CDP_ENDPOINT:endpoint},timeout:15000});
execFileSync('open',['discord://'+sourcePath]);
await new Promise(r=>setTimeout(r,2000));
const pages=await(await fetch(endpoint+'/json',{signal:AbortSignal.timeout(5000)})).json();
const target=pages.find(p=>p.url.includes(sourcePath));if(!target)throw Error('Wrong channel or login required');
const ws=new WebSocket(target.webSocketDebuggerUrl);await new Promise((r,reject)=>{ws.on('open',r);ws.on('error',reject)});let seq=0;const pending=new Map();ws.on('message',s=>{const r=JSON.parse(s);if(pending.has(r.id)){pending.get(r.id)(r);pending.delete(r.id)}});
const evaluate=expression=>new Promise((resolve,reject)=>{const id=++seq;pending.set(id,r=>{if(r.error||r.result?.exceptionDetails)reject(Error(JSON.stringify(r.error||r.result.exceptionDetails)));else resolve(r.result?.result?.value)});ws.send(JSON.stringify({id,method:'Runtime.evaluate',params:{expression,returnByValue:true}}))});
const scrollerCode=`const list=document.querySelector('[data-list-id="chat-messages"],ol[aria-label]');let n=list;while(n&&!(n.scrollHeight>n.clientHeight&&['scroll','auto'].includes(getComputedStyle(n).overflowY)))n=n.parentElement;if(!n)n=document.querySelector('[class*="scroller__36d07"]');if(!n)throw Error('Message scroller missing');`;
await evaluate(`(()=>{${scrollerCode}n.scrollTop=n.scrollHeight;return true})()`);
await new Promise(r=>setTimeout(r,1200));
const rows=new Map();
for(let i=0;i<30;i++){
 const batch=await evaluate(`Array.from(document.querySelectorAll('li[id^="chat-messages-"]')).map(n=>{const content=n.querySelector('[id^="message-content-"]');const article=n.querySelector('[role=article]');let f=article?.[Object.keys(article).find(k=>k.startsWith('__reactFiber'))];let author=null;let edited=null;for(let j=0;f&&j<20;j++,f=f.return){const m=f.memoizedProps?.message;if(m?.author){author={id:m.author.id,username:m.author.username,globalName:m.author.globalName};edited=m.editedTimestamp?.toISOString?.()||null;break;}}return {id:n.id.split('-').pop(),channel_id:${JSON.stringify(cfg.source_channel_id)},author,time:n.querySelector('time')?.getAttribute('datetime'),edited,content:content?.innerText,attachments:Array.from(n.querySelectorAll('a[href*="/attachments/"]')).map(a=>a.href)}})`);
 for(const row of batch||[])rows.set(row.id,row);
 console.log(i,rows.size,batch?.[0]?.time);

 if(batch?.[0]?.time && batch[0].time.slice(0,10)<new Date(Date.parse(date+'T12:00:00Z')-7*86400000).toISOString().slice(0,10))break;
 await evaluate(`(()=>{${scrollerCode}n.scrollTop=0;return true})()`);
 await new Promise(r=>setTimeout(r,900));
}
ws.close();
const all=[...rows.values()].sort((a,b)=>a.id.localeCompare(b.id));
if(!all.length)throw Error('No messages read; not proof of no report');
saveCapture(out,all,{date,captured_at:new Date().toISOString(),author_id:cfg.author_id,source_url:target.url,bounded_scroll_limit:30});
console.log(JSON.stringify({ok:true,date,count:all.length,output:out}));
clearTimeout(timeout);
