"""Versioned presentation corrections; original research-v1 grader is unchanged.

Do not repair facts, units, calculations, sources, or selections. The original
schema left fact types open and requested numeric units. Accept a scalar wrapped
in an explicit compatible unit and a source-proven parent/SPV label annotation.
"""
from copy import deepcopy
import math
import re

VERSION = 'research-v1.1-scoring'

def normalize(answer, case, records):
    result = deepcopy(answer)
    changes = []
    by_id = {r['record_id']: r for r in records}
    by_entity = {r['entity_id']: r for r in records}
    unit = case.get('unit')
    units = {'property_size': {unit}, 'price_per_unit': {'USD_per_' + str(unit)}}
    for row in result.get('shortlist', []):
        facts = row.get('facts', {})
        for field, allowed in units.items():
            value = facts.get(field)
            if (isinstance(value, dict) and set(value) == {'value', 'unit'}
                    and value['unit'] in allowed and type(value['value']) in (int, float)
                    and math.isfinite(value['value'])):
                facts[field] = value['value']
                changes.append(dict(record_id=row.get('record_id'), field=field, original=value,
                                    normalized=value['value'], reason='Explicit numeric wrapper with the unit required by the brief'))
        source = by_id.get(row.get('record_id'), {})
        parent = by_entity.get(source.get('parent_entity_id'), {})
        name = facts.get('firm_name')
        if source.get('firm_kind') == 'property_SPV' and source.get('parent_link') == 'executed_ownership_schedule' and parent and isinstance(name, str):
            # Only the two observed unambiguous forms, with BOTH entity names
            # exactly supported by the supplied source relationship.
            forms = [f"{parent['firm_name']} (transaction closed by property SPV {source['firm_name']})",
                     f"{parent['firm_name']} (parent of SPV {source['firm_name']})"]
            if name in forms:
                facts['firm_name'] = parent['firm_name']
                changes.append(dict(record_id=row['record_id'], field='firm_name', original=name,
                                    normalized=parent['firm_name'], reason='Source-proven parent label with accurate SPV annotation'))
    return result, changes
