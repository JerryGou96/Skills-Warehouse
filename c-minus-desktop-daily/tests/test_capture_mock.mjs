// Execute capture with only external process/CDP/time waits replaced by synthetic adapters.
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import assert from 'node:assert/strict';
import { EventEmitter } from 'node:events';
const root=fs.mkdtempSync(path.join(os.tmpdir(),'capture-mock-'));
const commands=[];
try {
  const cfg={output_dir:'data',runtime_dir:'runtime',timezone:'America/Los_Angeles',source_guild_id:'1',source_channel_id:'2',author_id:'3',destination_account:'fixture',destination_channel_id:'4',cdp_endpoint:'http://127.0.0.1:9232'};
  const config=path.join(root,'config.json');fs.writeFileSync(config,JSON.stringify(cfg));process.env.C_MINUS_CONFIG=config;
  globalThis.fixtureExec=(...args)=>{commands.push(args);return '{}';};
  globalThis.fixtureFetch=async()=>({json:async()=>[{url:'https://discord.com/channels/1/2',webSocketDebuggerUrl:'ws://fixture.invalid'}]});
  globalThis.FixtureSocket=class extends EventEmitter {
    constructor(){super();queueMicrotask(()=>this.emit('open'));}
    send(value){
      const request=JSON.parse(value),expression=request.params.expression;
      // Compile every DOM expression as JavaScript; no real DOM/browser is read.
      new Function('return '+expression);
      const rows=expression.startsWith('Array.from') ? [{id:'5',author:{id:'3'},time:'2001-01-01T00:00:00Z',content:'synthetic',channel_id:'2',attachments:[]}] : true;
      if(Array.isArray(rows))assert.ok(expression.includes('channel_id:"2"'));
      queueMicrotask(()=>this.emit('message',JSON.stringify({id:request.id,result:{result:{value:rows}}})));
    }
    close(){}
  };
  let source=fs.readFileSync(new URL('../scripts/capture.mjs',import.meta.url),'utf8');
  source=source.replace("import { createRequire } from 'node:module';",'')
    .replace("import { execFileSync } from 'node:child_process';",'const execFileSync=globalThis.fixtureExec; const fetch=globalThis.fixtureFetch;')
    .replace("'./capture-utils.mjs'",JSON.stringify(new URL('../scripts/capture-utils.mjs',import.meta.url).href))
    .replace("const require=createRequire(path.join(cfg.runtime_dir,'package.json'));",'')
    .replace("const WebSocket=require('ws');",'const WebSocket=globalThis.FixtureSocket;')
    .replace(/await new Promise\(r=>setTimeout\(r,\d+\)\);/g,'');
  const listeners=process.listeners('exit');
  await import('data:text/javascript;base64,'+Buffer.from(source).toString('base64'));
  const out=path.join(root,'data',fs.readdirSync(path.join(root,'data'))[0]);
  const meta=JSON.parse(fs.readFileSync(path.join(out,'capture-latest.json')));
  assert.equal(meta.author_id,'3');assert.equal(meta.source_url,'https://discord.com/channels/1/2');assert.equal(meta.count,1);
  assert.equal(commands[0][0],path.join(root,'runtime/node_modules/.bin/opencli'));
  assert.deepEqual(commands[1],['open',['discord://discord.com/channels/1/2']]);
  // Simulate normal process exit and unregister the fixture-only cleanup hook.
  for(const listener of process.listeners('exit').filter(fn=>!listeners.includes(fn))){listener();process.removeListener('exit',listener);}
  assert.ok(!fs.existsSync(path.join(out,'.capture-lock')));
  console.log('PASS: mocked capture source navigation, CDP expressions, configured author/channel, evidence, exit lock cleanup');
} finally {fs.rmSync(root,{recursive:true,force:true});}
