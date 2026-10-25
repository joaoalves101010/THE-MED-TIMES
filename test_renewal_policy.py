"""Isolated synthetic policy tests. No production candidate, no network, no deployment."""
import copy,unittest
from renewal_policy import validate_renewal

def fixture():
 old=[{'id':f'old-{i}','title':f'Previous distinct subject {i}','sourceUrl':f'https://example.org/old/{i}','paragraphs':[f'Previous report findings {i}']} for i in range(96)]
 new=[{'id':f'new-{i}','title':f'New distinct subject {i}','sourceUrl':f'https://example.org/new/{i}','paragraphs':[f'New report findings {i}']} for i in range(96)]
 review={'policyVersion':2,'novelty':{'previousEditionId':'004','semanticReviewCompleted':True,'relevantArchivesReviewed':True,'archiveReviewNotes':'Synthetic fixture compares event identities against all relevant historical examples.','method':'Synthetic test only: each distinct topic compared with all previous topics.'},'relevantUpdateIds':[a['id'] for a in new],'articles':{a['id']:{'status':'verified','novelty':{'topicKey':f'new scientific question {i}','isNewTopic':True,'comparedAgainstAllPreviousTopics':True,'comparedAgainstAllCandidateTopics':True,'differenceFromPrevious':'Synthetic fixture describes a distinct research question absent from the previous edition.'}} for i,a in enumerate(new)}}
 return new,old,review
class RenewalTests(unittest.TestCase):
 def check_reject(self,change):
  n,o,r=fixture();change(n,o,r)
  with self.assertRaises(AssertionError):validate_renewal(n,o,r,'004')
 def test_positive_dry_fixture(self):
  n,o,r=fixture();v=validate_renewal(n,o,r,'004');self.assertEqual(v['newTopicCount'],96)
 def test_old_id(self):self.check_reject(lambda n,o,r:n[0].update(id=o[0]['id']))
 def test_url_alias(self):self.check_reject(lambda n,o,r:n[0].update(sourceUrl=o[0]['sourceUrl']+'/?utm_source=alias#part'))
 def test_title_alias(self):self.check_reject(lambda n,o,r:n[0].update(title='  PREVIOUS DISTINCT SUBJECT 0!!!'))
 def test_body_alias(self):self.check_reject(lambda n,o,r:n[0].update(paragraphs=['PREVIOUS REPORT findings 0.']))
 def test_carry_forward(self):self.check_reject(lambda n,o,r:r['articles']['new-0'].update(status='carried_forward'))
 def test_semantic_missing(self):self.check_reject(lambda n,o,r:r['novelty'].update(semanticReviewCompleted=False))
 def test_topic_review_missing(self):self.check_reject(lambda n,o,r:r['articles']['new-0'].pop('novelty'))
 def test_only_eight_updates(self):self.check_reject(lambda n,o,r:r.update(relevantUpdateIds=r['relevantUpdateIds'][:8]))
 def test_duplicate_primary(self):self.check_reject(lambda n,o,r:n[1].update(sourceUrl=n[0]['sourceUrl']+'?x=2'))
 def test_duplicate_topic(self):self.check_reject(lambda n,o,r:r['articles']['new-1']['novelty'].update(topicKey=r['articles']['new-0']['novelty']['topicKey']))
 def test_duplicate_title(self):self.check_reject(lambda n,o,r:n[1].update(title=n[0]['title']))
 def test_duplicate_body(self):self.check_reject(lambda n,o,r:n[1].update(paragraphs=n[0]['paragraphs']))
 def test_candidate_semantic_missing(self):self.check_reject(lambda n,o,r:r['articles']['new-0']['novelty'].pop('comparedAgainstAllCandidateTopics'))
 def test_query_identity_distinct(self):
  from renewal_policy import normalized_url
  self.assertNotEqual(normalized_url('https://example.org/article?id=1'),normalized_url('https://example.org/article?id=2'))
 def test_archive_review_missing(self):self.check_reject(lambda n,o,r:r['novelty'].pop('relevantArchivesReviewed'))
 def test_wrong_prior(self):self.check_reject(lambda n,o,r:r['novelty'].update(previousEditionId='003'))
 def test_policy_required(self):self.check_reject(lambda n,o,r:r.pop('policyVersion'))
if __name__=='__main__':unittest.main()
