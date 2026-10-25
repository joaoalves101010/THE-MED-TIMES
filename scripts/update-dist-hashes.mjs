// Run only AFTER full source/content/UI checks and editorial approval.
import fs from 'node:fs';
import path from 'node:path';
import { root, hashes } from './dist-utils.mjs';
const edition = JSON.parse(fs.readFileSync(path.join(root, 'edition.json')));
fs.writeFileSync(path.join(root, 'public-dist-sha256.json'), JSON.stringify({
  schemaVersion: 1, project: 'the-med-times', editionId: edition.editionId,
  localDate: edition.localDate, files: hashes()
}, null, 2) + '\n');
console.log('Public artifact hashes recorded. This does not certify facts or authorize publication.');
