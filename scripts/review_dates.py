"""Advisory report; does not change review status or dates."""
from datetime import date
from content import pages
today=date.today(); found=0
print(f'Review report: {today}')
for path,m,_ in pages():
    if m.get('status')=='archived': continue
    due=date.fromisoformat(m['next_review'])
    reasons=[]
    if due<=today: reasons.append(f'review due {due}')
    if not m.get('last_reviewed'): reasons.append('not yet substantively reviewed')
    if 'pending' in m.get('owner','').lower(): reasons.append('owner assignment pending')
    if reasons: print(f"{m['resource_id']}: {'; '.join(reasons)} | {path.name}");found+=1
print(f'{found} resources require editorial attention.')
