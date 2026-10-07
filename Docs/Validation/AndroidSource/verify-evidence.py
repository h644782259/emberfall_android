from pathlib import Path
import json,hashlib,ast
base=Path(__file__).resolve().parent;root=base.parents[2]
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
manifest=json.loads((base/'manifest.json').read_text())
for name,digest in manifest.items():assert sha(base/name)==digest,name
r=json.loads((base/'Evidence/report.json').read_text());assert r['passed'] and len(r['checks'])==13 and all(c['passed'] for c in r['checks']) and not r['sourceChangedDuringRun']
assert (base/'Evidence/exit-code.txt').read_text().strip()=='0'
for name,digest in r['sourceSha256'].items():assert sha(root/name)==digest,name
parsed=ast.parse((root/'Tools/validate-android-source.py').read_text());fn=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='inputs');scope={'root':root,'sha':sha};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<verified-input-enumerator>','exec'),scope);assert scope['inputs']()==r['sourceSha256']
for attempt in ['InitialAttempt','SecondAttempt','ThirdAttempt']:
 old=json.loads((base/attempt/'report.json').read_text());assert not old['passed'] and not old['sourceChangedDuringRun'] and len(old['checks'])==13
 assert {c['name'] for c in old['checks'] if not c['passed']}=={'full-source-inventory'}
 assert (base/attempt/'exit-code.txt').read_text().strip()=='1'
 for c in old['checks']:assert (base/attempt/c['log']).is_file()
for c in r['checks']:assert (base/'Evidence'/c['log']).is_file()
print('PASS: 13 final frozen Android source checks; all inputs and archived artifacts match; three original inventory failures retained; no Unity or APK/device claim')
