using System.IO;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEngine;
using UnityEngine.Rendering;

namespace Emberfall.Editor
{
    // Local debug APK entry. No release keystore or credential is read or configured here.
    public static class AndroidBuild
    {
        public const string ApplicationId = "com.h644782259.emberfall.android";
        public const string ScenePath = "Assets/Scenes/Main.unity";

        [MenuItem("Emberfall/配置 Android 工程 Configure Android", false, 2)]
        public static void Configure()
        {
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, ApplicationId);
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.SetApiCompatibilityLevel(NamedBuildTarget.Android, ApiCompatibilityLevel.NET_Standard_2_0);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.Android.targetSdkVersion = AndroidSdkVersions.AndroidApiLevelAuto;
            PlayerSettings.Android.bundleVersionCode = 1;
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.AutoRotation;
            PlayerSettings.allowedAutorotateToLandscapeLeft = true;
            PlayerSettings.allowedAutorotateToLandscapeRight = true;
            PlayerSettings.allowedAutorotateToPortrait = false;
            PlayerSettings.allowedAutorotateToPortraitUpsideDown = false;
            PlayerSettings.fullScreenMode = FullScreenMode.FullScreenWindow;
            PlayerSettings.runInBackground = false;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.OpenGLES3 });
        }

        [MenuItem("Emberfall/构建 Android 调试 APK Build Android", false, 3)]
        public static void BuildApk()
        {
            if (!BuildPipeline.IsBuildTargetSupported(BuildTargetGroup.Android, BuildTarget.Android))
                throw new BuildFailedException("请为 Unity 6000.6.3f1 安装 Android Build Support、SDK/NDK Tools 和 OpenJDK。");
            if (EditorUserBuildSettings.activeBuildTarget != BuildTarget.Android)
                throw new BuildFailedException("先在 Build Profiles 切换到 Android；命令行必须使用 -buildTarget Android，以正确编译 Android 条件代码。");
            if (PlayerSettings.Android.useCustomKeystore)
                throw new BuildFailedException("此入口仅用于本地调试 APK，不使用自定义签名。发布签名由用户在独立发布流程中处理。");
            string project = Path.GetFullPath(Path.Combine(Application.dataPath, ".."));
            string output = Path.Combine(project, "Builds", "Android", "Emberfall-Android.apk");
            if (File.Exists(output) || Directory.Exists(output))
                throw new BuildFailedException("输出已存在，请先自行移走，构建入口不会覆盖：" + output);
            if (!File.Exists(Path.Combine(project, ScenePath)))
                throw new BuildFailedException("完整工程缺少 Main 场景，不能从差量脚本构建。");
            ProjectTools.EnsureSettings();
            Configure();
            ProgressionValidation.Validate();
            AssetDatabase.SaveAssets();
            bool previousBundle = EditorUserBuildSettings.buildAppBundle;
            bool previousExport = EditorUserBuildSettings.exportAsGoogleAndroidProject;
            try
            {
                EditorUserBuildSettings.buildAppBundle = false;
                EditorUserBuildSettings.exportAsGoogleAndroidProject = false;
                Directory.CreateDirectory(Path.GetDirectoryName(output));
                BuildReport report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
                {
                    scenes = new[] { ScenePath }, target = BuildTarget.Android,
                    targetGroup = BuildTargetGroup.Android, locationPathName = output,
                    options = BuildOptions.Development
                });
                if (report == null || report.summary.result != BuildResult.Succeeded || !File.Exists(output))
                    throw new BuildFailedException("Android APK 构建未完成；检查 Unity 构建日志。未执行安装或设备验收。");
                Debug.Log("Android 调试 APK 已构建，仍需安装到设备验收：" + output);
                if (!Application.isBatchMode) EditorUtility.RevealInFinder(output);
            }
            finally
            {
                EditorUserBuildSettings.buildAppBundle = previousBundle;
                EditorUserBuildSettings.exportAsGoogleAndroidProject = previousExport;
            }
        }
    }
}
