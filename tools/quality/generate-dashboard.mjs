// CHAD Feature Assurance reference implementation; dependency-free Node.js.
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
function makeDashboards(reg,stats,total){
 const palette={light:{bg:"#ffffff",surface:"#ffffff",border:"#dedede",text:"#202123",muted:"#61646b",track:"#ededee",green:"#21865f",blue:"#497aa7",amber:"#956324",grey:"#777d86"},dark:{bg:"#171717",surface:"#212121",border:"#424242",text:"#f2f2f2",muted:"#b4b4b4",track:"#393939",green:"#48ba90",blue:"#87aed9",amber:"#e1b46b",grey:"#a2a4aa"}};
 const esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;");
 const result={};
 for(const [theme,p] of Object.entries(palette)){
  const width=880;
  const text=(x,y,s,size=15,weight=400,fill=p.text,anchor="start")=>`<text x="${x}" y="${y}" font-size="${size}" font-weight="${weight}" fill="${fill}" text-anchor="${anchor}">${esc(s)}</text>`;
  const rect=(x,y,w,h,r,fill,stroke="none")=>`<rect x="${x}" y="${y}" width="${w}" height="${h}" rx="${r}" fill="${fill}" stroke="${stroke}"/>`;
  const progress=(x,y,w,value,color)=>rect(x,y,w,8,4,p.track)+(value>0?rect(x,y,w*Math.min(100,Math.max(0,value))/100,8,4,color):"");
  const frame=(h,title,desc,body)=>`<svg xmlns="http://www.w3.org/2000/svg" width="${width}" height="${h}" viewBox="0 0 ${width} ${h}" role="img" aria-labelledby="title desc"><title id="title">${esc(title)}</title><desc id="desc">${esc(desc)}</desc>${rect(0,0,width,h,12,p.bg)}<g font-family="system-ui, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif">${body}</g></svg>\n`;
  let body=text(20,30,"Project development status",21,600)+text(20,52,`${reg.baseline_release} · Catalog-based metrics`,13,400,p.muted);
  const metrics=[["Implementation (incl. beta)",`${total.implemented}%`,p.green,total.implemented],["Documented verification",`${total.documented}%`,p.blue,total.documented],["Tracked requirements",`${total.total}`,p.text,null],["Subsystems audited",`${reg.groups.length}`,p.text,null]];
  metrics.forEach(([label,value,color,percent],i)=>{const x=20+(i%2)*426,y=68+Math.floor(i/2)*105;body+=rect(x,y,414,94,14,p.surface,p.border)+text(x+17,y+25,label,14,400,p.muted)+text(x+17,y+61,value,31,600,color);if(percent!==null)body+=progress(x+17,y+75,380,percent,color);});
  body+=text(20,304,"Distribution of features",18,600);
  const categories=[["Documented verified",0,p.green],["Implemented",1,p.blue],["Beta",2,p.amber],["Partial",3,p.amber],["Planned",4,p.grey],["Unverified",5,p.grey],["In progress",6,p.blue],["Blocked",7,p.amber],["Regression",8,p.amber]].filter(([,i])=>i<6||total.counts[i]>0);
  const panelH=categories.length*29+22;
  body+=rect(20,319,840,panelH,14,p.surface,p.border);
  categories.forEach(([label,i,color],row)=>{const n=total.counts[i],y=342+row*29;body+=text(36,y,label,14,400)+text(844,y,String(n),14,600,p.text,"end")+progress(257,y-10,530,100*n/total.total,color);});
  body+=text(20,319+panelH+22,"Historical documentation claims · Not a new runtime test or release-readiness score.",12,400,p.muted);
  result[theme==="light"?"project-status.svg":"project-status-dark.svg"]=frame(319+panelH+38,"Project development status",`${total.implemented}% implemented, ${total.documented}% documented verified, ${total.total} requirements.`,body);
  let grid=text(20,30,"Subsystem progress",21,600)+text(20,52,"Implementation including beta · documented verification shown separately",13,400,p.muted);
  reg.groups.forEach((g,i)=>{const x=20+(i%2)*426,y=68+Math.floor(i/2)*110,s=stats(g.features);grid+=rect(x,y,414,98,14,p.surface,p.border)+text(x+16,y+24,g.name,15,600)+text(x+398,y+26,`${s.implemented}%`,22,600,p.text,"end")+progress(x+16,y+38,382,s.implemented,p.green)+text(x+16,y+68,`${s.total} requirements · ${s.documented}% documented verified`,12,400,p.muted)+text(x+16,y+86,`${s.counts[4]} planned · ${s.counts[5]} unverified`,12,400,p.muted);});
  result[theme==="light"?"subsystems.svg":"subsystems-dark.svg"]=frame(68+Math.ceil(reg.groups.length/2)*110,"Subsystem progress","Implementation and documented verification for each catalogued subsystem.",grid);
 }
 return result;
}
function render(reg){
 const statuses=["documented_verified","implemented","beta","partial","planned","unverified","in_progress","blocked","regression"];
 const colors=["#41b883","#74a9d7","#d9ad62","#c88c5c","#8b8e9c","#666b80","#9876d5","#ce6571","#ed5267"];
 const labels=["Documented verified","Implemented","Beta","Partial","Planned","Unverified","In progress","Blocked","Regression"];
 const seen=new Set(), groupIds=new Set();
 if(reg.schema_version!==1||!Array.isArray(reg.groups)||!reg.groups.length||!/^[a-f0-9]{40}$/.test(reg.baseline_commit))throw Error("Invalid registry");
 const all=reg.groups.flatMap(g=>{if(!g.id||groupIds.has(g.id)||!g.name||!Array.isArray(g.features)||!g.features.length)throw Error("Invalid group");groupIds.add(g.id);return g.features.map(f=>{if(!f.id||seen.has(f.id)||!statuses.includes(f.status)||!f.name||!f.acceptance||!f.source||!Array.isArray(f.runtime_evidence)||!f.id.startsWith(g.id+"-")||!/^[-\w./]+$/.test(f.source)||f.source.includes("..")||f.source.startsWith("/"))throw Error("Invalid feature "+f.id);seen.add(f.id);return f;});});
 const stats=a=>{const counts=statuses.map(s=>a.filter(f=>f.status===s).length);const pct=n=>Math.round(100*n/a.length);return {total:a.length,counts,implemented:pct(counts[0]+counts[1]+counts[2]),documented:pct(counts[0]),evidenced:pct(a.filter(f=>f.runtime_evidence.length>0).length)};};
 const total=stats(all), esc=s=>String(s).replace(/&/g,"&amp;").replace(/</g,"&lt;").replace(/>/g,"&gt;").replace(/"/g,"&quot;"), md=s=>String(s).replace(/\|/g,"\\|").replace(/\r?\n/g," ");
 const dashboards=makeDashboards(reg,stats,total);
 let doc=`# Feature status & progress / Status e progresso\n\nGenerated from [quality/features.json](../quality/features.json). Do not edit this report directly.\n\nBaseline: \`${reg.baseline_release}\` / \`${reg.baseline_commit}\`. ${reg.method}\n\n<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/dashboard/project-status-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="../assets/dashboard/project-status.svg">
  <img alt="Project development status" src="../assets/dashboard/project-status.svg" width="880">
</picture>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="../assets/dashboard/subsystems-dark.svg">
  <source media="(prefers-color-scheme: light)" srcset="../assets/dashboard/subsystems.svg">
  <img alt="Subsystem progress" src="../assets/dashboard/subsystems.svg" width="880">
</picture>\n\n**Implementation coverage: ${total.implemented}% · Documented verification: ${total.documented}% · Newly registered evidence: ${total.evidenced}% · ${total.total} requirements.**\n\nImplementation = (documented verified + implemented + beta) / total; partial is not counted as complete. Documented verification is a historical documentation claim, not an independent re-test. New evidence coverage counts requirements with a recorded evidence reference; it does not measure pass rate. Percentages are rounded, depend on the catalog scope and do not represent effort or release readiness.\n\n## Subsystem summary\n\n| Subsystem | Requirements | Implemented incl. beta | Documented verified | Planned | Unverified |\n|---|---:|---:|---:|---:|---:|\n`;
 for(const g of reg.groups){const s=stats(g.features);doc+=`| ${g.name} | ${s.total} | ${s.implemented}% | ${s.documented}% | ${s.counts[4]} | ${s.counts[5]} |\n`;}
 for(const g of reg.groups){doc+=`\n## ${g.name}\n\n| ID | Feature | Status | Source | Issue | Acceptance criterion | New evidence |\n|---|---|---|---|---|---|---|\n`;for(const f of g.features){doc+=`| ${f.id} | ${md(f.name)} | ${labels[statuses.indexOf(f.status)]} | [source](../${f.source}) | ${f.issue?`[#${f.issue}](https://github.com/Neguchads/cdos-nintendods-recomp/issues/${f.issue})`:"—"} | ${md(f.acceptance)} | ${f.runtime_evidence.length} |\n`;}}
 return {dashboards,doc,total,summary:JSON.stringify({baseline:reg.baseline_commit,overall:total,subsystems:reg.groups.map(g=>({id:g.id,name:g.name,...stats(g.features)}))},null,2)+"\n"};
}
const root=path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const registry=JSON.parse(fs.readFileSync(path.join(root,'quality/features.json'),'utf8'));
const result=render(registry);
for(const group of registry.groups) for(const feature of group.features) if(!fs.existsSync(path.join(root,feature.source))) throw Error('Missing source: '+feature.source);
const files={...Object.fromEntries(Object.entries(result.dashboards).map(([name,data])=>['assets/dashboard/'+name,data])),'docs/FEATURE_STATUS.md':result.doc,'quality/progress.json':result.summary};
const check=process.argv.includes('--check');
for(const [file,data] of Object.entries(files)){const dest=path.join(root,file);if(check){if(!fs.existsSync(dest)||fs.readFileSync(dest,'utf8').replace(/\r\n/g,'\n')!==data)throw Error('Stale generated file: '+file);}else{fs.mkdirSync(path.dirname(dest),{recursive:true});fs.writeFileSync(dest,data);}}
console.log(JSON.stringify(result.total));
