#!/usr/bin/env python3
"""Android source handoff checks. No Unity process, SDK build, signing or APK installation."""
from pathlib import Path
import os,sys,subprocess,tempfile,importlib.util,json,hashlib,base64,zipfile
from datetime import datetime,timezone
root=Path(__file__).resolve().parents[1]
BASE='e1397a26049e624d98daa0b20159526e045f6076'
spec=importlib.util.spec_from_file_location('cv',root/'Tools/cloud-validation.py');cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
output=root/'Docs/Validation/AndroidSource/ReviewFix/Evidence';output.mkdir(parents=True,exist_ok=True)
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def inputs():
 paths=set()
 for folder in ['Assets','Packages','ProjectSettings']:
  paths.update(p for p in (root/folder).rglob('*') if p.is_file())
 for folder in ['Tests','Tools']:
  paths.update(p for p in (root/folder).rglob('*') if p.is_file() and p.suffix in ['.py','.cs','.sh'] and 'TestResults' not in p.parts and 'ReferenceAssemblies' not in p.parts)
 paths.update(root/p for p in ['.gitignore','README.md','Docs/Android.md','Docs/Validation/AndroidSource/source-baseline.json','Docs/Validation/AndroidSource/ReviewFix/provenance.json','Docs/Validation/AndroidSource/ReviewFix/verify-evidence.py','Docs/Validation/AndroidSource/ReviewFix/README.md'])
 return {str(p.relative_to(root)):sha(p) for p in sorted(paths)}
initial=inputs();report={'baseline':BASE,'startedUtc':datetime.now(timezone.utc).isoformat(),'checks':[],'sourceSha256':initial,'scope':'Full source inventory and targeted managed Android checks; no real Unity import/build, IL2CPP, Gradle, APK or device execution.'}
def record(name,body):
 log=output/(name+'.log')
 try:message=body();ok=True
 except Exception as ex:message=repr(ex);ok=False
 log.write_text(str(message)+'\n');report['checks'].append({'name':name,'passed':ok,'log':log.name});print(('PASS ' if ok else 'FAIL ')+name,flush=True)
def inventory():
 baseline=json.loads((root/'Docs/Validation/AndroidSource/source-baseline.json').read_text());assert baseline['commit']==BASE
 entries=baseline['gitBlobSha1'];excluded=set(baseline['excludedNonRuntimeVideos']);changed={'.gitignore','README.md','Assets/Editor/ProjectTools.cs','ProjectSettings/ProjectSettings.asset','Assets/Editor/GroundLootValidation.cs'};matched=0
 for name,oid in entries.items():
  p=root/name
  if name in excluded:assert not p.exists(),name;continue
  assert p.is_file(),name
  if name in changed:continue
  data=p.read_bytes()
  # The inherited .gitattributes checks out PowerShell as CRLF; Git blobs use LF.
  if p.suffix=='.ps1':
   attr=subprocess.check_output(['git','check-attr','eol','--',name],cwd=root,text=True).strip();assert attr.endswith(': crlf'),attr;data=data.replace(b'\r\n',b'\n')
  assert hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()==oid,name;matched+=1
 runtime={str(p.relative_to(root)) for p in (root/'Assets/Scripts').rglob('*') if p.is_file()};sourceRuntime={n for n in entries if n.startswith('Assets/Scripts/')};assert runtime==sourceRuntime,'runtime additions/deletions'
 assert 'm_EditorVersion: 6000.6.3f1' in (root/'ProjectSettings/ProjectVersion.txt').read_text()
 for name in ['Assets/Scenes/Main.unity','Assets/Scenes/Main.unity.meta','Packages/manifest.json','Packages/packages-lock.json','Assets/Editor/AndroidBuild.cs','Assets/Editor/AndroidBuild.cs.meta']:assert (root/name).is_file(),name
 newAllowed={'Tests/AndroidResourceBoundaryTests.py','Tests/EditorAssemblyBoundaryTests.py','Assets/Resources/Fonts/NotoSansSC-Regular.otf','Assets/Resources/Fonts/NotoSansSC-Regular.otf.meta','Assets/Resources/Fonts/LICENSE.txt','Assets/Resources/Fonts/LICENSE.txt.meta','Assets/Editor/AndroidBuild.cs','Assets/Editor/AndroidBuild.cs.meta','Tests/AndroidBuildBoundaryTests.cs','Tests/AndroidBuildBoundaryTests.py','Tools/Build-Android.sh','Tools/validate-android-source.py','Docs/Android.md'}
 tracked=subprocess.check_output(['git','ls-files','-z','--cached','--others','--exclude-standard'],cwd=root,text=True).rstrip('\0').split('\0')
 forbidden={'.apk','.aab','.apks','.keystore','.jks','.pfx','.p12','.mp4','.mov','.webm','.unitypackage'}
 for name in tracked:
  p=Path(name);assert p.suffix.lower() not in forbidden,name
  assert not any(x.lower() in ['library','temp','builds','build','obj','.gradle','.aws','.codex'] for x in p.parts),name
  if name not in entries:assert name in newAllowed or name.startswith('Docs/Validation/AndroidSource/'),name
 assert not (root/'Builds').exists(),'no output packages should be produced by source verification'
 return {'matchingOriginalFiles':matched,'unchangedRuntimeFiles':len(runtime),'sourceFiles':len(tracked),'allowedModifiedOriginalFiles':sorted(changed),'excludedNonRuntimeVideos':sorted(excluded),'unityVersion':'6000.6.3f1'}
def config():
 s=(root/'ProjectSettings/ProjectSettings.asset').read_text();c=(root/'Assets/Editor/ProjectTools.cs').read_text()
 for token in ['Android: com.h644782259.emberfall.android','AndroidTargetArchitectures: 2','AndroidMinSdkVersion: 26','AndroidTargetSdkVersion: 0','allowedAutorotateToPortrait: 0','allowedAutorotateToPortraitUpsideDown: 0','scriptingBackend:\n    Standalone: 0\n    Android: 1','apiCompatibilityLevelPerPlatform:\n    Android: 6','activeInputHandler: 0']:assert token in s,token
 assert 'AndroidBuild.Configure();' in c and 'AndroidBuild.BuildApk();' in c
 for rule in ['*.apk','*.aab','*.jks','*.keystore','local.properties','keystore.properties','.gradle/']:assert rule in (root/'.gitignore').read_text(),rule
 subprocess.run(['bash','-n',str(root/'Tools/Build-Android.sh')],check=True)
 return 'Android persisted settings, editor initialization/guide and launcher syntax verified'
def references():
 arc=root/'Tools/ReferenceAssemblies/unityengine.modules.2021.3.33.nupkg';digest=base64.b64encode(hashlib.sha512(arc.read_bytes()).digest()).decode();assert digest==cv.PACKAGE_SHA512
 refs=cv.unity_references(False)
 with zipfile.ZipFile(arc) as z:
  for p in refs.glob('*.dll'):assert p.read_bytes()==z.read('lib/netstandard2.0/'+p.name),p.name
 return {'packageSha512Base64':digest,'referenceDlls':len(list(refs.glob('*.dll')))}
record('full-source-inventory',inventory);record('android-configuration',config);record('pinned-api-references',references)
with tempfile.TemporaryDirectory(prefix='android-source-validation-') as tmp:
 p=Path(tmp);(p/'NuGet.Config').write_text('<configuration><packageSources><clear/></packageSources></configuration>')
 env=dict(os.environ,DOTNET_CLI_HOME=str(p/'cli'),DOTNET_NOLOGO='1',DOTNET_CLI_TELEMETRY_OPTOUT='1',DOTNET_TieredCompilation='0');sdk=sys.argv[1]
 cases=[('application-pause-state',['Assets/Scripts/Core/ApplicationPauseState.cs','Tests/ApplicationPauseStateTests.cs'],'ApplicationPauseStateTests',''),('android-lifecycle',['Assets/Scripts/UI/TouchViewportState.cs','Assets/Scripts/UI/TouchReleaseLatch.cs','Assets/Scripts/Core/AudioLifecycleGate.cs','Assets/Scripts/Core/ApplicationPauseState.cs','Assets/Scripts/Core/SaveLifecycleGate.cs','Tests/AndroidLifecycleTests.cs'],'AndroidLifecycleTests',''),('game-font-android',['Assets/Scripts/UI/GameFont.cs','Tests/GameFontTests.cs'],'GameFontTests','UNITY_ANDROID')]
 for name,files,cls,defines in cases:
  proj=cv.write_project(p/name,[root/f for f in files],'using System;class Program{static void Main(){Console.WriteLine('+cls+'.Run());}}',defines=defines)
  cv.run_check(name,[[sdk,'run','--project',str(proj)]],env,output,report)
 for name,script in [('real-font-resource','AndroidResourceBoundaryTests.py'),('editor-assembly-boundary','EditorAssemblyBoundaryTests.py'),('android-build-entry','AndroidBuildBoundaryTests.py'),('android-lifecycle-source','AndroidLifecycleSourceTests.py'),('production-touch-lifecycle','ProductionTouchLifecycleTests.py'),('mobile-pause-transition','MobilePauseTransitionProductionTests.py'),('mobile-inventory-back','MobileInventoryBackProductionTests.py'),('mobile-opportunity-input','MobileOpportunityInputProductionTests.py')]:cv.run_check(name,[[sys.executable,str(root/'Tests'/script),sdk]],env,output,report)
 proj=cv.write_project(p/'android-runtime-compile',sorted((root/'Assets/Scripts').rglob('*.cs')),references=list(cv.unity_references(False).glob('*.dll')),defines='UNITY_ANDROID')
 cv.run_check('android-runtime-compile',[[sdk,'build',str(proj),'--configuration','Release','--verbosity','minimal']],env,output,report)
final=inputs();report['sourceChangedDuringRun']=[n for n in initial.keys()|final.keys() if initial.get(n)!=final.get(n)];report['completedUtc']=datetime.now(timezone.utc).isoformat();report['passed']=all(c['passed'] for c in report['checks']) and not report['sourceChangedDuringRun'];(output/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Android source checks:',report['passed'],len(report['checks']),flush=True);sys.exit(0 if report['passed'] else 1)
