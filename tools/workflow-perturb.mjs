// Change declared input cells on a COPY for artifact acceptance testing.
import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const [source,changesPath,output]=process.argv.slice(2);
const changes=JSON.parse(await fs.readFile(changesPath,'utf8'));
const wb=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
for(const [loc,value] of Object.entries(changes)) {
  const at=loc.lastIndexOf('!');if(at<1)throw Error('Sheet!A1 address required');
  const sheet=loc.slice(0,at).replace(/^'|'$/g,'');const cell=loc.slice(at+1);
  if(!/^\$?[A-Z]{1,2}\$?[1-9][0-9]{0,3}$/.test(cell)||!Number.isFinite(value))throw Error('Finite numeric cell update required');
  wb.worksheets.getItem(sheet).getRange(cell).values=[[value]];
}
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
console.log(JSON.stringify({output,changed:changes}));
