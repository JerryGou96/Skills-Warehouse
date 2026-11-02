import fs from 'node:fs';
import path from 'node:path';
import { createHash } from 'node:crypto';

export function loadConfig() {
  if (!process.env.C_MINUS_CONFIG) throw Error('Set C_MINUS_CONFIG to your local JSON config');
  const file=path.resolve(process.env.C_MINUS_CONFIG), cfg=JSON.parse(fs.readFileSync(file,'utf8'));
  for (const key of ['output_dir','runtime_dir','timezone','source_guild_id','source_channel_id','author_id','destination_account','destination_channel_id','cdp_endpoint']) {
    if (typeof cfg[key]!=='string' || !cfg[key].trim() || cfg[key].startsWith('SET_')) throw Error(`Configure ${key}`);
  }
  for (const key of ['source_guild_id','source_channel_id','author_id','destination_channel_id']) {
    if (!/^\d+$/.test(cfg[key])) throw Error(`${key} must be a numeric string`);
  }
  if (cfg.source_channel_id===cfg.destination_channel_id) throw Error('Source and destination channels must differ');
  new Intl.DateTimeFormat('en-US',{timeZone:cfg.timezone});
  const endpoint=new URL(cfg.cdp_endpoint);
  if (endpoint.protocol!=='http:' || !['127.0.0.1','localhost','[::1]'].includes(endpoint.hostname) || !endpoint.port || endpoint.pathname!=='/' || endpoint.search || endpoint.hash || endpoint.username || endpoint.password) throw Error('CDP endpoint must be local HTTP with explicit port and no path or credentials');
  cfg.cdp_endpoint=endpoint.origin;
  for (const key of ['output_dir','runtime_dir']) cfg[key]=path.resolve(path.dirname(file),cfg[key]);
  return cfg;
}
export function acquireLock(out) {
  const lock=path.join(out,'.capture-lock');
  try { fs.mkdirSync(lock); } catch (e) { if (e.code==='EEXIST') throw Error('Capture already running; do not overwrite lock'); throw e; }
  let released=false;
  return () => { if (!released) { fs.rmSync(lock,{recursive:true}); released=true; } };
}
export function saveCapture(out,rows,meta) {
  if (!rows.length) throw Error('No messages read; not proof of no report');
  const hash=createHash('sha256').update(JSON.stringify(rows)).digest('hex');
  const raw_file=`raw-${hash.slice(0,16)}.json`;
  fs.writeFileSync(path.join(out,raw_file),JSON.stringify(rows,null,2));
  fs.writeFileSync(path.join(out,'capture-latest.json'),JSON.stringify({...meta,raw_file,count:rows.length,earliest:rows[0].time,latest:rows.at(-1).time},null,2));
  return raw_file;
}
