# Android 完整源码工程

本仓从 Windows PR #51 合并后的 main `e1397a26049e624d98daa0b20159526e045f6076` 初始化，包含完整 `Assets` 及 `.meta`、`Packages`、`ProjectSettings`，共享运行时保留方案页、营地切职业、单宝箱和奖励表现全部已审内容。Android main 以干净初始提交 `d86ee81a5622e026fc1cdf8875c2de67b8ce54e4` 建立，后续修复保留该历史。初始导入；排除源仓 `ArtSource/Review` 中三份非运行时评审视频，也不携带含这些视频的旧 Git 历史。源提交文件清单与 blob 哈希保存在 `Docs/Validation/AndroidSource/source-baseline.json`。不是 10 月 3 日旧基线 `8654c803` 的包，也不是可以覆盖到旧包上的差量脚本。

## 在 Unity 中打开

1. Unity Hub 添加仓库根目录，使用 `ProjectSettings/ProjectVersion.txt` 指定的 **Unity 6000.6.3f1**。
2. 给同一编辑器安装 Android Build Support、Android SDK & NDK Tools、OpenJDK；使用该编辑器匹配的工具链，不沿用其它版本的 SDK/NDK/JDK。
3. 等待完整资源导入和脚本编译，在 Build Profiles 中切换到 Android；场景为 `Assets/Scenes/Main.unity`。
4. `Emberfall → 配置 Android 工程` 设置包名 `com.h644782259.emberfall.android`、ARM64、IL2CPP、Android API 26 最低版本、已安装的自动目标 SDK、OpenGL ES 3、双向横屏。后台暂停与触控沿用共享运行时。自动初始化也会应用这些平台设置。
5. 需要在用户自己的机器构建时选择 `Emberfall → 构建 Android 调试 APK`。此入口实际调用 Android BuildPipeline，输出到 `Builds/Android/Emberfall-Android.apk`，拒绝覆盖已有输出。不生成 AAB，不导出 Gradle 工程，不使用自定义签名；正式商店签名与上架由独立发布流程处理。

命令行构建入口（这是供用户以后执行的命令，本次源码发布不执行构建）：

```sh
Tools/Build-Android.sh /path/to/Unity/6000.6.3f1/Editor/Unity
```

Windows PowerShell 可直接调用对应 `Unity.exe`：

```powershell
& 'C:\Program Files\Unity\Hub\Editor\6000.6.3f1\Editor\Unity.exe' -batchmode -quit -buildTarget Android -projectPath 'C:\Projects\emberfall_android' -executeMethod Emberfall.Editor.AndroidBuild.BuildApk -logFile 'C:\Projects\emberfall_android-build.log'
```

必须传 `-buildTarget Android`，保证编译的是 Android 条件代码。构建前检查模块、活动平台和完整场景；构建失败或没有真实输出文件时抛错。APK/AAB、Gradle 缓存、个人 keystore、签名配置、Library/Temp、视频均不进入源码仓库。

## 验证边界

```sh
python3 Tools/validate-android-source.py /path/to/dotnet
```

初次 13 项源码检查保存在 `Docs/Validation/AndroidSource/Evidence`，原报告保留；它漏检了真实字体资源与 Editor/Runtime 程序集边界。复核修复后的 15 项检查保存在 `Docs/Validation/AndroidSource/ReviewFix/Evidence`：检查完整工程与源提交逐文件对应、配置和构建调用、Android 条件运行时编译、字体/返回键/前后台/触控隔离。新增构建入口测试执行真实 C# 控制流，但 UnityEditor/BuildPipeline 是明确的托管替身，仅验证参数、拒绝条件和状态恢复，不生成游戏 APK。

继承的跨平台业务验证见 `Docs/Validation/RewardRevealPolish`：原完整 286 项中 283 通过、3 份旧夹具失败，随后仅适配这三份测试，7 项冻结补验通过；原失败报告保持原样。Android 初始化补平台配置和构建入口，复核后另补原版中文字体及 Editor 反射访问，不把继承验证说成 Android 原生构建。

当前环境没有 Unity Editor/Android SDK/设备，**未执行真实 Unity 导入、IL2CPP/Gradle 构建、APK 安装、触控、音频、GPU 或设备性能验收**。设备验收需覆盖：中文字体、横屏安全区、五技能/双页控制、Back 与退出确认、前后台无误触/不重复奖励、配装和试招折叠、存档重启、完整副本与奖励展示。没有下载包交付。

Unity 官方参考：[Android 环境要求](https://docs.unity3d.com/6000.0/Documentation/Manual/android-requirements-and-compatibility.html)、[Android 架构配置](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/PlayerSettings.Android-targetArchitectures.html)、[APK/AAB 输出开关](https://docs.unity3d.com/6000.0/Documentation/ScriptReference/EditorUserBuildSettings-buildAppBundle.html)。具体安装模块以项目指定的 6000.6.3f1 为准。

中文 UI 字体从同项目 iOS `d8f091cccca54649aa8fe733aa53b1743536aeec` 原样引入：`Resources/Fonts/NotoSansSC-Regular.otf`、导入 meta 与 SIL OFL 1.1 许可。字体内嵌 Adobe 版权信息保留，未开启系统字体回退。GroundLootValidation 同步该提交的反射读取修复，不扩大运行时 `CombatEpoch` 的可见性。独立程序集检查使用真实运行时源码与 UnityEngine 2021.3.33 固定引用，但仅提供少量 UnityEditor API 替身，因此不是完整 Unity 6000.6.3f1 Editor 编译。
