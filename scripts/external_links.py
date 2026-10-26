"""Bounded advisory external-link report. No publication changes or notifications."""
from concurrent.futures import ThreadPoolExecutor
from urllib.request import Request,urlopen
from urllib.error import URLError,HTTPError
from pathlib import Path
import re
from content import ROOT
urls=set()
for p in [*ROOT.glob('*.md'), *(ROOT/'docs').rglob('*.md')]:
    for raw in re.findall(r'https?://[^\s<>\)\]"{}]+',p.read_text(encoding='utf-8')):
        url=raw.rstrip('.,;')
        if 'YOUR-' not in url: urls.add(url)
def check(url):
    try:
        req=Request(url,method='GET',headers={'User-Agent':'SIDM-link-review/0.1'})
        with urlopen(req,timeout=15) as r: return f'{r.status} {url}'
    except (URLError,HTTPError,TimeoutError,OSError) as e: return f'REVIEW {url}: {e}'
print('Advisory only: rate limits and access controls can cause false failures.')
with ThreadPoolExecutor(max_workers=4) as pool:
    for line in pool.map(check,sorted(urls)): print(line)
