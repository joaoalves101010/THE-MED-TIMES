"""Static structural guarantees. Not a substitute for browser-layout verification."""
import unittest,json,re,hashlib,math
from pathlib import Path
from archive_previews import Tree
from edition_config import long_date,EDITION_ID,CONFIG
P=Path(__file__).parent;D=P/'dist'
rows=json.loads((P/'src/editions'/EDITION_ID/'articles.json').read_text())
class ReadingStructure(unittest.TestCase):
 def test_sidecar_preserves_seven_field_editorial_contract(self):
  text=(D/'index.html').read_text()
  core=json.loads(re.search(r'id="edition-data" type="application/json">(.*?)</script>',text,re.S)[1])
  meta=json.loads(re.search(r'id="edition-search-meta" type="application/json">(.*?)</script>',text,re.S)[1])
  self.assertEqual(len(core),96);self.assertEqual(len(meta),96)
  for a in core:self.assertEqual(set(a),{'id','url','section','category','title','deck','paragraphs'})
  for a in rows:
   self.assertEqual(meta[a['id']]['date'],a['date']);self.assertEqual(meta[a['id']]['contentType'],a['contentType'])
   self.assertEqual(meta[a['id']]['readingMinutes'],max(1,math.ceil(len(' '.join([a['deck'],*a['paragraphs'],a.get('implication',''),a.get('discussionPrompt','')]).split())/200)))
 def test_legacy_assets_byte_preserved(self):
  for name in ('styles.css','app.js'):self.assertEqual((D/name).read_bytes(),(P/'src/historical-ui'/name).read_bytes())
 def test_visible_evidence_and_real_related_titles_all_articles(self):
  lookup={a['id']:a for a in rows}
  mapping_path=P/'src/editions'/EDITION_ID/'reading-related.json'
  if not mapping_path.exists():mapping_path=P/'src'/('reading-related-'+EDITION_ID+'.json')
  mapping=json.loads(mapping_path.read_text())['articles'] if mapping_path.exists() else {}
  for a in rows:
   root=Tree((D/a['url']/'index.html').read_text()).root
   evidence=root.find(lambda n:'article-evidence' in n.classes)
   self.assertIsNotNone(evidence);self.assertIn(a.get('evidenceType') or a['contentType'],evidence.text());self.assertIn(a['sourceName'],evidence.text());self.assertIn(long_date(a['verifiedAt']) if a.get('verifiedAt') else 'Data de conferência não informada',evidence.text())
   self.assertTrue(evidence.find(lambda n:n.tag=='a' and n.attrs.get('href')==a['sourceUrl']))
   related=root.find(lambda n:'related-stories' in n.classes);self.assertEqual(len(related.nodes()),2)
   if mapping:
    for target in mapping[a['id']]:self.assertIn(lookup[target['id']]['title'],related.text())
    self.assertIn('Leituras relacionadas',root.text())
   else:
    self.assertIn('Continue neste caderno',root.text())
    for target in [x for x in rows if x['section']==a['section'] and x['id']!=a['id']][:2]:self.assertIn(target['title'],related.text())
   self.assertIn('não afirmamos revisão médica independente',root.text())
   self.assertIsNotNone(root.find(lambda n:n.attrs.get('aria-current')=='location' and a['section'] in n.attrs.get('href','')))
   if a['section']=='pesquisa':self.assertNotIn('antes de se candidatar',root.find(lambda n:'sources' in n.classes).text())
 def test_full_cover_only_compact_articles(self):
  for path in [D/'index.html',*D.glob('editorias/*/index.html')]:
   root=Tree(path.read_text()).root;self.assertIsNone(root.find(lambda n:'compact-masthead' in n.classes));self.assertIn('Ciência para ler.',root.text());self.assertIn('Uma leitura crítica',root.text())
  self.assertIn('compact-masthead',(D/rows[0]['url']/'index.html').read_text())
 def test_semantic_leading_package_and_uniqueness(self):
  for path in [D/'index.html',*D.glob('editorias/*/index.html')]:
   root=Tree(path.read_text()).root;composition=root.find(lambda n:'press-composition' in n.classes)
   stories=composition.all(lambda n:'press-story' in n.classes)
   self.assertIn(stories[0].attrs['data-role'],{'lead','feature'})
   ids=[n.attrs['data-article-id'] for n in stories];self.assertEqual(len(ids),len(set(ids)))
   for band in composition.all(lambda n:'press-band' in n.classes):
    columns=[int(n.attrs['data-desktop-column']) for n in band.nodes()];self.assertEqual(sorted(columns),list(range(1,len(columns)+1)))
 def test_archive_unique_honest_proofs(self):
  root=Tree((D/'edicao/index.html').read_text()).root;archive=root.find(lambda n:'reading-archive' in n.classes)
  self.assertEqual(len(archive.nodes()),len(CONFIG.get('history',[]))+1)
  descriptions=[]
  for article in archive.nodes():
   image=article.find(lambda n:n.tag=='img');self.assertTrue((D/'edicao'/image.attrs['src']).resolve().is_file())
   self.assertIn('não captura de navegador',article.text());self.assertTrue(article.find(lambda n:n.tag=='h3').text());descriptions.append(article.find(lambda n:n.tag=='div').nodes()[-2].text())
  self.assertEqual(len(set(descriptions)),len(archive.nodes()))
 def test_canvas_and_no_misleading_cta(self):
  css=(D/'styles-reading.css').read_text();self.assertIn('--paper:#FFFFFF',css);self.assertNotIn('scroll-behavior:smooth',css)
  js=(D/'app-reading.js').read_text();self.assertNotIn('análise completa',js)
  self.assertNotIn('Acesso livre',(D/'index.html').read_text())
if __name__=='__main__':unittest.main()
