# Android 源码发布验证

源为 Windows PR #51 合并后的 main `e1397a26049e624d98daa0b20159526e045f6076`，Unity 6000.6.3f1。Android 为独立完整源码仓库，采用无父提交的初始 main，避免携带原仓评审视频历史；不修改 Windows/iOS main。

工程审计保留源提交的 11,741 个文件内容，其中所有 606 个共享运行时文件（含 `.meta`）完全一致。仅四个原文件有平台相关改动：`.gitignore`、`README.md`、`Assets/Editor/ProjectTools.cs`、`ProjectSettings/ProjectSettings.asset`；排除三份 `ArtSource/Review/*.mp4` 非运行时视频。新增 Android Editor 构建入口及 `.meta`、Bash 入口、构建边界测试、源码验证器和文档。Assets、Packages、ProjectSettings 完整，Main 场景和包锁定文件保留。

最终 `Evidence/report.json` 为 13 项冻结验证：完整源码清单、Android 持久配置、66 份固定 API 引用、应用暂停、Android 生命周期、Android 字体、实际构建入口控制流、生命周期源码约束、真实生产触控链、移动暂停切换、移动行囊返回、移动机会输入，以及全部运行时的 `UNITY_ANDROID` 条件编译。报告列明实际结果及 `sourceChangedDuringRun`。托管 SDK 为 8.0.425，显式 `DOTNET_TieredCompilation=0`。运行时参考包沿用仓库固定 UnityEngine.Modules 2021.3.33，校验原包 SHA-512 和每份引用 DLL。

新增构建入口检查共 18 条，编译并执行实际 AndroidBuild.cs，UnityEditor/BuildPipeline 是明确替身。验证缺少模块、错误活动平台、自定义签名、缺少完整场景、已有输出时拒绝；检查 Android Development/Main 场景参数，并测试构建异常、失败报告、缺少输出时正确拒绝与恢复 Editor 输出开关。临时测试文件不是 APK，随后清理。

原始失败保留，未重写为成功：

- `InitialAttempt`：源仓含三份评审视频，发布排除检查失败。
- `SecondAttempt`：Git 中的 LF PowerShell blob 与 `.gitattributes` 指定的 CRLF 工作树直接比对失败；按既有属性进行精确换行规范化后修复审计。
- `ThirdAttempt`：Git 默认将中文文件名转义，审计误把转义文本当路径；改为 NUL 分隔的原始路径清单。

这些失败均为发布完整性审计，不涉及玩法变更。最终源清单 `source-baseline.json` 记录原仓全部文件 blob SHA-1 和三份明确排除视频；当前文件逐项比对，新增文件受明确白名单约束。

执行：`python3 Tools/validate-android-source.py /path/to/dotnet`。验证归档：`python3 Docs/Validation/AndroidSource/verify-evidence.py`。继承的跨平台业务验证仍保留在各历史目录，本次未把它们冒充 Android 原生验证。

**未运行 Unity Editor、真实导入或 UnityEditor API 编译、IL2CPP、Gradle、SDK/NDK/JDK、签名、APK 构建安装或 Android 设备验收。没有生成或上传游戏包，也没有处理或上传视频。** 用户在匹配的 Unity 环境中按 `Docs/Android.md` 操作后，仍需完成真实构建及设备验收。
