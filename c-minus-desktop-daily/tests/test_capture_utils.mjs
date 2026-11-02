import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { loadConfig, acquireLock, saveCapture } from '../scripts/capture-utils.mjs';
const root=fs.mkdtempSync(path.join(os.tmpdir(),'capture-fixture-'));
try {
  const cfg={output_dir:'data',runtime_dir:'runtime',timezone:'America/Los_Angeles',source_guild_id:'1',source_channel_id:'2',author_id:'3',destination_account:'fixture',destination_channel_id:'4',cdp_endpoint:'http://127.0.0.1:9232'};
  const file=path.join(root,'config.json');process.env.C_MINUS_CONFIG=file;
  fs.writeFileSync(file,JSON.stringify(cfg));assert.equal(loadConfig().output_dir,path.join(root,'data'));
  cfg.cdp_endpoint='https://example.invalid';fs.writeFileSync(file,JSON.stringify(cfg));assert.throws(loadConfig,/local HTTP/);
  cfg.cdp_endpoint='http://127.0.0.1:9232';cfg.destination_channel_id='2';fs.writeFileSync(file,JSON.stringify(cfg));assert.throws(loadConfig,/must differ/);
  const release=acquireLock(root);assert.throws(()=>acquireLock(root),/already running/);release();release();acquireLock(root)();
  const rows=[{id:'1',time:'2025-01-07T14:00:00Z',content:'synthetic'}];
  const one=saveCapture(root,rows,{date:'2025-01-07'});assert.equal(saveCapture(root,rows,{}),one);
  rows[0].content+=' edit';const two=saveCapture(root,rows,{});assert.notEqual(two,one);assert.ok(fs.existsSync(path.join(root,one)));
  assert.equal(JSON.parse(fs.readFileSync(path.join(root,'capture-latest.json'))).raw_file,two);
  assert.throws(()=>saveCapture(root,[],{}),/No messages/);
  console.log('PASS: config paths and rejection, capture lock exclusion/release, versioned evidence, empty capture rejection');
} finally {fs.rmSync(root,{recursive:true,force:true});}
