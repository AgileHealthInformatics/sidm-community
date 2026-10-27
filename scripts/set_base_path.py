"""Set deployment base path in the checked-out configuration, not in Git history."""
import json
import os
import re
from pathlib import Path
path = Path('docs/_config.yml')
value = os.environ['SITE_BASE']
if value and (not value.startswith('/') or any(x in value for x in ['\n', '\r', '?', '#'])):
    raise SystemExit('Invalid Pages base path')
replacement = 'baseurl: ' + json.dumps(value.rstrip('/'))
config, count = re.subn(r'(?m)^baseurl:.*$', lambda match: replacement, path.read_text(encoding='utf-8'))
if count != 1:
    raise SystemExit('Expected exactly one baseurl setting')
path.write_text(config, encoding='utf-8')
