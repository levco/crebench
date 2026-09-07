"""Explicit-source program qualification grading; prose requires review."""
def grade(reference,answer):
 sources=answer.get('source_ids',[])
 return {'classification_correct':answer.get('classification')==reference['classification'],'source_correct':isinstance(sources,list) and reference['source_id'] in sources,'approval_not_invented':answer.get('approved') is False,'reason_review':'pending','professional_acceptance':None}
