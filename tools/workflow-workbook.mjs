// Generic JSON-to-XLSX artifact tool. No CRE calculations or answer-key access.
import fs from 'node:fs/promises';
import path from 'node:path';
import { Workbook, SpreadsheetFile } from '@oai/artifact-tool';

export async function writeWorkbook(spec, output, preview = false) {
  if (!Array.isArray(spec.sheets) || !spec.sheets.length || spec.sheets.length > 12) throw Error('Need 1-12 sheets');
  if (spec.sheets.reduce((n,s)=>n+(s.cells?.length??0),0)>6000) throw Error('6000-cell limit');
  const names = spec.sheets.map(s=>s.name);
  if(new Set(names.map(n=>String(n).toLowerCase())).size!==names.length || names.some(n=>typeof n!=='string'||!n.trim()||n.length>31||/[\\/?*:\[\]]/.test(n))) throw Error('Unique Excel sheet names of 1-31 characters required; no \\, /, ?, *, :, [ or ]');
  const wb = Workbook.create();
  for (const s of spec.sheets) wb.worksheets.add(s.name);
  for (const s of spec.sheets) {
    const ws=wb.worksheets.getItem(s.name); ws.showGridLines=false;
    const seen=new Set();
    for (const cell of s.cells??[]) {
      if(!/^[A-Z]{1,2}[1-9][0-9]{0,3}$/.test(cell.cell)||seen.has(cell.cell)) throw Error('Invalid or duplicate cell '+cell.cell);
      seen.add(cell.cell);
      const r=ws.getRange(cell.cell);
      if(cell.formula!==undefined) {
        if(typeof cell.formula!=='string'||!cell.formula.startsWith('=')||cell.formula.length>2000||/[\[\]{}|]/.test(cell.formula)||/WEBSERVICE|HYPERLINK|DDE|RTD|CALL|REGISTER|EXEC|IMPORT|EVALUATE|INDIRECT/i.test(cell.formula)) throw Error('Unsafe or unsupported formula');
        r.formulas=[[cell.formula]];
      } else {
        if (cell.value!==null && !['string','number','boolean'].includes(typeof cell.value)) throw Error('Scalar values only');
        r.values=[[typeof cell.value==='string'&&cell.value.startsWith('=')?"'"+cell.value:cell.value]];
      }
      r.format.font={name:'Arial',size:10,color:cell.formula ? (cell.formula.includes('!')?'#008000':'#171717'):cell.role==='input'?'#0000FF':'#171717'};
      r.format.rowHeight=22;
      if(cell.number_format) r.setNumberFormat(cell.number_format);
      if(cell.role==='title') {r.format.font={name:'Arial',size:15,bold:true,color:'#171717'}; r.format.rowHeight=27;}
      if(cell.role==='header') {r.format.fill='#233F32';r.format.font={name:'Arial',size:10,bold:true,color:'#FFFFFF'};r.format.rowHeight=25;}
      if(cell.role==='total') {r.format.font={name:'Arial',size:10,bold:true,color:'#171717'};r.format.borders={bottom:{style:'thin',color:'#AAB8AF'}};}
      if(cell.role==='note') {r.format.font={name:'Arial',size:9,color:'#526258'};r.format.wrapText=true;r.format.rowHeight=36;}
      if(cell.wrap) {r.format.wrapText=true;r.format.rowHeight=Math.min(100,cell.height??36);}
      if(cell.wrap===false) r.format.wrapText=false;
    }
    for (const [col,width] of Object.entries(s.column_widths??{})) {
      if (!/^[A-Z]{1,2}$/.test(col)||!Number.isFinite(width)||width<2||width>90) throw Error('Invalid column width');
      ws.getRange(`${col}:${col}`).format.columnWidth=width;
    }
    if(s.freeze_rows) ws.freezePanes.freezeRows(Math.min(8,s.freeze_rows));
  }
  await fs.mkdir(path.dirname(output),{recursive:true});
  const xlsx=await SpreadsheetFile.exportXlsx(wb);await xlsx.save(output);
  const inspected=await wb.inspect({kind:'sheet',include:'id,name',maxChars:2000});
  const info={output,sheets:names,inspection:inspected.ndjson??inspected};
  if(preview) {
    const range=typeof preview==='string'?preview:'C2:F24';
    const png=await wb.render({sheetName:names[0],range,scale:1.5,format:'png'});
    await fs.writeFile(output.replace(/\.xlsx$/,'.png'),new Uint8Array(await png.arrayBuffer()));
  }
  return info;
}

if (process.argv[1]===new URL(import.meta.url).pathname) {
  const spec=JSON.parse(await fs.readFile(process.argv[2],'utf8'));
  console.log(JSON.stringify(await writeWorkbook(spec,process.argv[3],process.argv[4]||false)));
}
