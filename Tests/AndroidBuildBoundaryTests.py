from pathlib import Path
import importlib.util,subprocess,tempfile,os,sys
root=Path(__file__).resolve().parents[1];spec=importlib.util.spec_from_file_location('cv',root/'Tools/cloud-validation.py');cv=importlib.util.module_from_spec(spec);spec.loader.exec_module(cv)
with tempfile.TemporaryDirectory(prefix='emberfall-android-entry-') as tmp:
 p=Path(tmp);(p/'NuGet.Config').write_text('<configuration><packageSources><clear/></packageSources></configuration>')
 project=cv.write_project(p/'project',[root/'Assets/Editor/AndroidBuild.cs',root/'Tests/AndroidBuildBoundaryTests.cs'],'class Program{static void Main(string[] a){AndroidBuildBoundaryTests.Run(a[0]);}}')
 subprocess.run([sys.argv[1],'run','--project',str(project),'--',str(p/'fixture')],check=True,env=dict(os.environ,DOTNET_CLI_HOME=str(p/'cli'),DOTNET_NOLOGO='1'))
