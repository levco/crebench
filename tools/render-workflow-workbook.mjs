import fs from 'node:fs/promises';
import {FileBlob,SpreadsheetFile} from '@oai/artifact-tool';
const [source,sheet,range,output]=process.argv.slice(2);
const w=await SpreadsheetFile.importXlsx(await FileBlob.load(source));
const png=await w.render({sheetName:sheet,range,scale:1.3,format:'png'});
await fs.writeFile(output,new Uint8Array(await png.arrayBuffer()));
console.log(JSON.stringify({source,sheet,range,output}));
