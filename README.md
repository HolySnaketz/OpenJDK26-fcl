# OpenJDK 26 for FCL

面向 **Fold Craft Launcher（FCL）1.3.3.1** 的 OpenJDK 26 Android 移植，提供 ARM64（`aarch64`）与 ARM32（`arm`）Java 导入包。基于官方 **OpenJDK 26+35 RI**，适配 FCL 的运行时路径、嵌入启动及 Cacio/AWT 桥接，无须修改 FCL APK。

## 状态

已完成 ARM64 与 ARM32 的专用 make images 和候选包打包；ARM64 版本已在设备 PLC110 验证通过

| 项目 | ARM64 | ARM32 |
|---|---|---|
| 官方 OpenJDK 26+35 RI 源码 | 是 | 是 |
| 完整 JDK 镜像、AWT/Swing、JNI 头文件、jmods、命令手册 | 已包含 | 已包含 |
| C1/C2、G1 等上游 server 默认功能 | 保留 | 保留 |
| 编译与 tar.xz 结构检查 | 通过 | 通过 |
| ELF ABI、依赖文件闭包、相对 RUNPATH | 110 个 ELF 通过 | 109 个 ELF 通过 |
| 16 KiB PT_LOAD 对齐 | JDK 与随包库检查通过 | 不属于本项 ARM64 验收 |
| 原版 FCL 实际导入/启动 | 通过 | 未验证 |
| Minecraft 26.2 + Forge 65.1.0 | 未验证 | 未验证 |
| jhsdb / SA | 编译保留，运行未验证 | 上游无 ARM32 后端，不能宣称可用 |

产物见 openjdk26-fcl-aarch64.tar.xz、openjdk26-fcl-arm.tar.xz，以及同名 SHA-256 和 manifest。

## 已完成的适配

- FCL 导入器要求 tar.xz，归档根目录直接包含 release/bin/lib；包内不使用符号链接，避免导入器重写相对链接的行为。
- JVM 临时目录使用 FCL 提供的 TMPDIR；JLI 嵌入启动使用 JAVA_HOME，修复 Android 同时定义 __linux__ 导致错误分支的问题。
- FCL 解压未恢复普通文件执行权限；JLI 在 FCL 环境内启动时为自身拥有的 bin 普通文件及 jspawnhelper 恢复用户执行位。Android 系统执行策略是否另有限制，需真机验证。
- 使用 FCL 原有 Cacio 与 AWT 原生桥接。新增 SurfaceManagerFactory 兼容类，并接回易失图像创建路径，解决 Cacio 在 JDK26 上找不到旧接口的问题。
- 所需非系统 Android 动态库随包提供，使用相对 RUNPATH；不依赖安装 Termux、pkg 或 Termux:X11。编译时复用了原项目的 Android sysroot。
- fontconfig 使用包内配置扫描 Android 系统字体。libandroid-spawn 从固定参考源重新编译，满足 16 KiB 对齐。

FCL 导入时会用 APK 内的 libawt_xawt.so 替换包内同名库。未经修改的 FCL 桥接行为仍是运行边界；包内保留该库不代表导入后使用原生 X11。

## 主机侧证据

官方主机 JDK26 + FCL 1.3.3.1 原版 Cacio + 本次 Java 兼容补丁：AWT/Swing 初始化、窗口组件、按钮事件、离屏绘图、易失图像绘制通过。

剪贴板测试进入 CTCClipboard 的 Android 原生方法后，由于主机没有 FCL 原生桥接而无法继续；未伪造该接口，也未计为通过。Cacio 自身会输出 setZOrder 尚未实现的提示，不能因此宣称通用桌面 GUI 的全部行为都已满足。

测试日志：logs/cacio-host26.log、logs/cacio-host26-clipboard-unavailable.log。测试程序自身的主机 javac/子进程/Serial/G1 冒烟检查通过：logs/jdk-probe-host26.log。这些证据不能替代 Android 测试。

8 个补丁顺序零模糊应用并与当前编译源比对，59 个涉及文件一致：research/patch-verification.json、logs/patch-proof.log。

注：本文档由ChatGPT生成

## 关于依赖

FCL 1.3.3.1 源码提交：f06b5c539b42c58172e33204dbd8e4220bd49403。
JDK 基线：官方 OpenJDK 26+35 RI。依赖参考：Termux packages c0df78899f52c9905e07321c999f24dd434bb7ae。
游戏暂按 Minecraft 26.2；Forge 使用查询时官方推荐 26.2-65.1.0。具体 OpenGL/Vulkan 渲染选项、GPU、Android 版本和 ARM32 用户态支持尚无设备信息。

说明（内容由ChatGPT生成）：[INSTALL.zh-CN.md](INSTALL.zh-CN.md)、[BUILD.zh-CN.md](BUILD.zh-CN.md)。
来源：[FCL 固定版本](https://github.com/FCL-Team/FoldCraftLauncher/tree/1.3.3.1)、[Forge 26.2](https://files.minecraftforge.net/net/minecraftforge/forge/index_26.2.html)、[官方 JDK26 RI 源码](https://download.java.net/openjdk/jdk26/ri/openjdk-26+35_src.zip)。
