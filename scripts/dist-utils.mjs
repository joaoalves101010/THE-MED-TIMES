import fs from 'node:fs';
import path from 'node:path';
import crypto from 'node:crypto';
import { fileURLToPath } from 'node:url';
export const root = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
export const dist = path.join(root, 'dist');
export function files(base, dir = base) {
  return fs.readdirSync(dir, { withFileTypes: true }).flatMap(entry => {
    const name = path.join(dir, entry.name);
    if (entry.isSymbolicLink()) throw new Error(`Symlink forbidden: ${path.relative(base, name)}`);
    return entry.isDirectory() ? files(base, name) : [path.relative(base, name).split(path.sep).join('/')];
  }).sort();
}
export const sha256 = bytes => crypto.createHash('sha256').update(bytes).digest('hex');
export const hashes = () => Object.fromEntries(files(dist).map(name => [name, sha256(fs.readFileSync(path.join(dist, name)))]));
