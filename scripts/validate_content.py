"""Validate editorial metadata. Does not certify factual correctness."""
import datetime as dt
import sys
from content import pages
required = ['title','description','resource_id','section','status','owner','last_updated',
            'last_reviewed','next_review','topics','source_versions','ai_assistance','contributors']
errors=[]; ids=set(); urls=set(); count=0
try:
    for path, m, body in pages():
        count += 1
        for key in required:
            if key not in m: errors.append(f'{path}: missing {key}')
        for key in ['title','description','resource_id','owner','ai_assistance']:
            if not isinstance(m.get(key),str) or not m.get(key,'').strip(): errors.append(f'{path}: empty {key}')
        url=m.get('permalink','')
        if not url.startswith('/') or url in urls: errors.append(f'{path}: missing or duplicate permalink')
        urls.add(url)
        ident=m.get('resource_id')
        if ident in ids: errors.append(f'{path}: duplicate resource_id {ident}')
        ids.add(ident)
        if m.get('status') not in ['working-draft','reviewed','endorsed','archived']:
            errors.append(f'{path}: invalid status')
        dates={}
        for key in ['last_updated','next_review','last_reviewed']:
            value=m.get(key)
            if key=='last_reviewed' and value is None: continue
            try: dates[key]=dt.date.fromisoformat(str(value))
            except ValueError: errors.append(f'{path}: invalid {key}')
        if m.get('status') in ['reviewed','endorsed']:
            if not m.get('last_reviewed') or not m.get('reviewer'):
                errors.append(f'{path}: reviewed/endorsed resources require reviewer and last_reviewed')
            if 'pending' in m.get('owner','').lower(): errors.append(f'{path}: assign an actual owner')
        if m.get('status')=='endorsed' and not m.get('approval_reference'):
            errors.append(f'{path}: endorsement requires approval_reference')
        for key in ['topics','source_versions','contributors']:
            if not isinstance(m.get(key),list): errors.append(f'{path}: {key} must be a list')
        if not body.strip(): errors.append(f'{path}: empty body')
except ValueError as exc: errors.append(str(exc))
if errors:
    print('\n'.join(errors)); sys.exit(1)
print(f'PASS: {count} pages have valid metadata and unique identifiers.')
