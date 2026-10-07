#!/usr/bin/env python3
"""Check real bundled font bytes/import settings, not a mocked Resources.Load."""
from pathlib import Path
import hashlib,json,re,subprocess,sys
from fontTools.ttLib import TTFont
root=Path(__file__).resolve().parents[1]
proof=json.loads((root/'Docs/Validation/AndroidSource/ReviewFix/provenance.json').read_text())
for name,entry in proof['files'].items():
 data=(root/name).read_bytes()
 assert hashlib.sha256(data).hexdigest()==entry['sha256'],name
 assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==entry['gitBlobSha1'],name
source=(root/'Assets/Scripts/UI/GameFont.cs').read_text()
path=re.search(r'BundledUiPath\s*=\s*"([^"]+)"',source)[1]
font=root/'Assets/Resources'/ (path+'.otf')
assert font.is_file() and font.stat().st_size==8331336
meta=font.with_suffix('.otf.meta').read_text();assert 'TrueTypeFontImporter:' in meta and 'includeFontData: 1' in meta
license=font.parent/'LICENSE.txt';assert 'SIL OPEN FONT LICENSE Version 1.1' in license.read_text()
for p in [font.with_suffix('.otf.meta'),license.with_suffix('.txt.meta')]:
 guid=re.search(r'^guid: (\w+)',p.read_text(),re.M)[1]
 matches=[str(m.relative_to(root)) for m in (root/'Assets').rglob('*.meta') if re.search(r'^guid: '+guid+r'$',m.read_text(),re.M)]
 assert len(matches)==1,(guid,matches)
with TTFont(font) as f:
 assert len(f.getBestCmap())==30890
 copyright=[n.toUnicode() for n in f['name'].names if n.nameID==0]
 assert copyright and any('Adobe' in n for n in copyright)
 print('Original embedded copyright retained:',copyright[0])
subprocess.run([sys.executable,str(root/'Tests/FontCoverageAudit.py'),'--font',str(font),'--strict'],check=True)
print('PASS real Android Resources font, embedded data, unique GUIDs, OFL and exact iOS source bytes; no Unity rendering claim')
