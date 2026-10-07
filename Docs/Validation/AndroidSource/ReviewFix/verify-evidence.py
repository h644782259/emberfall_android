from pathlib import Path
import ast,hashlib,json
base=Path(__file__).resolve().parent;root=base.parents[3];old=base.parent
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
for directory in [old,base]:
 for name,digest in json.loads((directory/'manifest.json').read_text()).items():assert sha(directory/name)==digest,name
prior=json.loads((old/'Evidence/report.json').read_text());assert prior['passed'] and len(prior['checks'])==13
r=json.loads((base/'Evidence/report.json').read_text());assert r['passed'] and len(r['checks'])==15 and all(c['passed'] for c in r['checks']) and not r['sourceChangedDuringRun']
assert (base/'Evidence/exit-code.txt').read_text().strip()=='0'
for name,digest in r['sourceSha256'].items():assert sha(root/name)==digest,name
parsed=ast.parse((root/'Tools/validate-android-source.py').read_text());fn=next(n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name=='inputs');scope={'root':root,'sha':sha};exec(compile(ast.Module(body=[fn],type_ignores=[]),'<verified-input-enumerator>','exec'),scope);assert scope['inputs']()==r['sourceSha256']
delta={n for n in prior['sourceSha256'].keys()|r['sourceSha256'].keys() if prior['sourceSha256'].get(n)!=r['sourceSha256'].get(n)}
expected={'Assets/Editor/GroundLootValidation.cs','Docs/Android.md','Tools/validate-android-source.py','Tests/AndroidResourceBoundaryTests.py','Tests/EditorAssemblyBoundaryTests.py'}
expected.update('Assets/Resources/Fonts/'+n for n in ['NotoSansSC-Regular.otf','NotoSansSC-Regular.otf.meta','LICENSE.txt','LICENSE.txt.meta'])
expected.update('Docs/Validation/AndroidSource/ReviewFix/'+n for n in ['provenance.json','verify-evidence.py','README.md'])
assert delta==expected,(delta-expected,expected-delta)
for c in r['checks']:assert (base/'Evidence'/c['log']).is_file()
print('PASS 15 frozen checks, current inputs, explicit review delta and unmodified historical evidence; no Unity/device claim')
