"""Lossless presentation normalization, without consulting an answer key."""
import json
import re
from .grade import grade


def pairs(items):
    result = {}
    for key, value in items:
        if key in result:
            raise ValueError(f'Ambiguous duplicate key: {key}')
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f'Non-finite number: {value}')


DECODER = json.JSONDecoder(object_pairs_hook=pairs, parse_constant=reject_constant)


def parse_answer(text):
    text = text.strip().lstrip('\ufeff')
    changes = []
    try:
        obj = DECODER.decode(text)
    except json.JSONDecodeError:
        fences = re.findall(r'```(?:json)?\s*\n([\s\S]*?)```', text, flags=re.I)
        if fences:
            if len(fences) != 1:
                raise ValueError('Multiple answer blocks require review')
            obj = DECODER.decode(fences[0].strip())
            changes.append('removed_markdown_fence_and_surrounding_prose')
            # A second JSON object outside the fenced block is ambiguous.
            outside = re.sub(r'```(?:json)?\s*\n[\s\S]*?```', '', text, flags=re.I)
            if '{' in outside or '[' in outside:
                raise ValueError('Additional structured answer outside code block requires review')
        else:
            start = text.find('{')
            if start < 0:
                raise ValueError('No structured answer; requires review')
            obj, end = DECODER.raw_decode(text, start)
            if '{' in text[end:] or '[' in text[end:]:
                raise ValueError('Multiple structured answers require review')
            changes.append('removed_surrounding_prose')
    if not isinstance(obj, dict):
        raise ValueError('Answer must be an object')
    return obj, changes


def normalize(text):
    obj, changes = parse_answer(text)
    if 'fields' in obj:
        fields = obj['fields']
        if not isinstance(fields, dict):
            raise ValueError('Fields must be an object')
    else:
        fields = {k:v for k,v in obj.items() if k != 'discrepancies'}
        changes.append('wrapped_flat_fields')
    normalized = {}
    for name, item in fields.items():
        if isinstance(item, dict) and 'value' in item:
            value, evidence = item['value'], item.get('evidence', [])
        else:
            value, evidence = item, []
            changes.append(f'wrapped_value:{name}')
        # Unambiguous display strings only. No units/rates are inferred or rescaled.
        if isinstance(value, str) and re.fullmatch(r'\s*\$?-?(?:\d{1,3}(?:,\d{3})+|\d+)(?:\.\d+)?%?\s*', value):
            value = float(value.strip().replace('$','').replace(',','').rstrip('%'))
            changes.append(f'parsed_numeric_display:{name}')
        normalized[name] = {'value': value, 'evidence': evidence}
    return {'fields': normalized, 'discrepancies': obj.get('discrepancies')}, changes


def score_text(case, text):
    answer, changes = normalize(text)
    result = grade(case, answer)
    groups = {}
    for name, kinds in [('financial', {'accuracy','conflict','calculation'}),
                        ('references', {'source_reference'}), ('contract', {'format'})]:
        checks = [c for c in result['criteria'] if c['kind'] in kinds]
        groups[name] = {'passed': sum(c['pass'] for c in checks), 'total': len(checks),
                        'failed': [c['criterion'] for c in checks if not c['pass']]}
    return {'normalizations': changes, 'normalized_answer': answer, 'groups': groups,
            'financial_complete': groups['financial']['passed'] == groups['financial']['total'],
            'criteria': result['criteria']}
