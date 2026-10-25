"""Public export invariants: immutable archives, editorial source integrity and no private records."""
import hashlib,json,re,unittest
from pathlib import Path
from archive_previews import sha
P=Path(__file__).resolve().parent
class PortableExportTests(unittest.TestCase):
 def test_live_cover_bound_and_safe(self):
  from edition_cover import verify_cover
  meta=verify_cover(P)
  self.assertEqual(meta['editionId'],json.loads((P/'edition.json').read_text())['editionId'])
  self.assertEqual(meta['image']['width'],1000)
  self.assertEqual(meta['image']['height'],1480)
 def test_public_identity(self):
  cfg=json.loads((P/'edition.json').read_text())
  self.assertEqual(cfg['projectId'],'the-med-times')
  if cfg['editionId']=='004':self.assertIn(cfg['publishingMode'],('manual-snapshot','scheduled-github-snapshot'))
  else:self.assertEqual(cfg['publishingMode'],'scheduled-github-snapshot')
 def test_no_private_records_in_output(self):
  for item in (P/'dist').rglob('*'):
   self.assertNotIn(item.name,{'RELEASE_MANIFEST.json','release-evidence.json','EDITORIAL_REVIEW.json','release-provenance','maintenance-provenance','.env','.openai'})
 def test_assets_byte_identical_to_source(self):
  for item in (P/'src/assets').rglob('*'):
   if item.is_file():self.assertEqual(item.read_bytes(),(P/'dist/assets'/item.relative_to(P/'src/assets')).read_bytes())
 def test_cover_images_unchanged_and_no_unused_previews(self):
  used=set()
  for item in (P/'src/archive-previews').glob('*.json'):
   meta=json.loads(item.read_text());used.add(meta['filename'])
   self.assertEqual(sha((item.parent/meta['filename']).read_bytes()),meta['imageSha256'])
   self.assertEqual((item.parent/meta['filename']).read_bytes(),(P/'dist/assets/archive-previews'/meta['filename']).read_bytes())
  self.assertEqual(used,{p.name for p in (P/'src/archive-previews').glob('*.png')})
  self.assertEqual(used,{p.name for p in (P/'dist/assets/archive-previews').glob('*.png')})
 def test_photo_rights_preserved_without_machine_paths(self):
  for photo in json.loads((P/'src/editions/002/photos.json').read_text()).values():
   self.assertNotIn('localPath',photo)
   self.assertTrue(photo['cleared']);self.assertEqual(photo['license'],'CC BY-ND 3.0')
   self.assertTrue(photo['licenseUrl']);self.assertTrue(photo['credit'])
 def test_current_preview_bound_to_actual_html_css_assets(self):
  eid=json.loads((P/'edition.json').read_text())['editionId']
  meta=json.loads((P/f'src/archive-previews/edition-{eid}.json').read_text())
  self.assertEqual(sha((P/'dist/index.html').read_bytes()),meta['sourceHtmlSha256'])
  self.assertEqual(sha((P/'dist'/meta['sourceCssRoute']).read_bytes()),meta['sourceCssSha256'])
  for filename,digest in meta['sourceAssetsSha256'].items():self.assertEqual(sha((P/'dist/assets'/filename).read_bytes()),digest)
if __name__=='__main__':unittest.main()
