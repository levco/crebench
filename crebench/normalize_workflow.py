"""Presentation-only extraction, with original values retained for audit.

Does not read gold values. A numeric token followed by an explanatory note is
transcribed as that token. ISO dates and free text remain unchanged.
"""
import copy,re
TEXT_FIELDS={'subject_lease_expiry','renewal_option_exercised','binding_constraint','prepayment_friction'}

def normalize(answer):
    result=copy.deepcopy(answer);changes=[]
    for f in result.get('fields',[]):
        value=f.get('value');field=f.get('id')
        if field=='renewal_option_exercised' and value is False:
            new='Not evidenced'
        elif not isinstance(value,str):continue
        else:new=value.strip()
        if field=='renewal_option_exercised' and (re.fullmatch(r'no(?:\s+[-—/(;:].*)?',new,flags=re.I) or new.lower() in {'false','not evidenced as exercised','no exercise evidenced'}):
            new='Not evidenced'  # Brief asks whether provided materials evidence exercise.
        elif field not in TEXT_FIELDS:
            if re.fullmatch(r'[-+]?\d+(?:\.\d+)?×',new):new=new[:-1]+'x'
            m=re.fullmatch(r'(\(?[-+]?\$?[\d,]+(?:\.\d+)?(?:%|x)?\)?)\s+(?:\([^\n]*\)|[←→][^\n]*)',new)
            # A qualifier can explain a unit/convention, but cannot revise a value.
            if m and not re.search(r'\b(actually|instead|corrected|correction|should be|rather than|not |approximately|approx\.)',new[m.end(1):],re.I):new=m.group(1)
        if new!=value:
            f['original_display_value']=value;f['value']=new;changes.append({'field':field,'original':value,'normalized':new})
    return result,changes
