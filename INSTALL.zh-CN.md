# 导入与验收

1. 使用原版 FCL 1.3.3.1。确认 FCL 实际运行 ABI：64 位版本选择 openjdk26-fcl-aarch64.tar.xz，32 位版本选择 openjdk26-fcl-arm.tar.xz。不能只根据 CPU 名称推断，64 位 Android 不一定允许 32 位应用。
2. 核对对应 .sha256，把 tar.xz 放到 FCL 文件选择器能访问的位置。
3. 打开 Java 管理，导入对应 tar.xz。不要预先解压，也不要将整个 dist 目录的归档当作 Java 包导入。
4. 在游戏实例的 Java 设置中明确选择刚导入的 Java 26。导入包名称会作为 FCL 的运行时目录名。
5. 无须安装 Termux、pkg 或 Termux:X11。FCL 会自行应用其 AWT 桥接库。

## 分层验收

先通过 FCL 的 Jar 执行功能选择 dist/acceptance-tests/FclJdkProbe.jar，并指定刚导入的 Java26。检查日志中的 COMPILER_API_PASS、CHILD_JAVA_PASS、JDK_BASIC_PASS。它测试编译器 API、可写临时目录，以及使用 Serial/G1 启动子 JVM；不是完整 GC 压力测试。

再执行 CacioProbe.jar，检查 AWT_SWING_OFFSCREEN_PASS 及工作目录中的 cacio-probe.png。该程序自动创建并关闭窗口，因此还需使用持续显示窗口的实际程序检查触控、键盘输入、中文字体、窗口层级和缩放。追加 JVM 参数 -Dfcl.probe.clipboard=true 可启用 Android 剪贴板检查。

随后分别在计划使用的 OpenGL、Vulkan 路径运行 Minecraft 26.2 + Forge 65.1.0，记录渲染器名称及版本、驱动、GPU、Android API、启动日志、主菜单/进入世界/持续运行结果。Vulkan 原生渲染与 OpenGL 经 Vulkan 转换须分别记录。当前没有任一路径的游戏运行结果。

还需覆盖 JNI/LWJGL、长时间 GC/JIT、多线程、音频、Robot、打印及可用诊断工具。ARM32 jhsdb 的上游后端缺失已列为已知问题，不属于已通过项目。

## 回报故障

提供设备型号、Android 版本、FCL ABI、导入包名、游戏/Forge 版本、渲染选项和完整启动日志。出现 hs_err_pid*.log 时一并保存。导入成功仅说明包结构被识别，不代表 JVM、GUI 或游戏已经通过验收。