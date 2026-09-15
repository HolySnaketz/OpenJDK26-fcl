# 构建说明

本轮工作主目录：D:\projects\arron\shuoshuo-07\openjdk26-fcl。
WSL 临时目录：/home/arron/projects/openjdk26-fcl-build。

复用了先前 openjdk26-android 项目的官方源码缓存、OpenJDK25 引导 JDK、NDK r29、Termux API28 交叉编译工具链、依赖 sysroot 及原始 configure 参数。因此本组脚本目前针对本机环境，不能仅解压源码包后就视为独立、离线可复现环境。

## 正式输入

- 官方 RI 源码：../openjdk26-android/downloads/openjdk-26+35_src.zip，SHA256 215fb2cc080e334538f5c57a2be3d34e64e97cf3c7655fe485b3cf13c87e1602。
- patches/0001 至 0008：按文件名顺序应用。其中前五个从已验证 Android 移植演进，后三个为 FCL 路径、嵌入启动及 Cacio 兼容修复。
- dependency-sources/libandroid-spawn/：重新编译的依赖源码及许可证。
- research/fcl-tree.json：固定 FCL 提交的源码目录索引；相关 Java/C 文件和 Cacio Jar 只读参考，未修改 FCL APK。

## 当前环境中的入口

从本项目目录在 WSL 执行：

```sh
python3 scripts/verify-patches.py
# /data/TERMUX_ARCH 必须对应当前 ABI，且另一个构建已退出
python3 scripts/build.py aarch64
python3 scripts/build.py arm
# 仅作增量构建时
python3 scripts/build.py ARCH --resume
python3 scripts/build-spawn.py
python3 scripts/package.py ARCH
python3 scripts/build-probes.py
python3 scripts/probe-cacio.py
```

切换 ABI 使用原项目 scripts/switch-staging-arch.sh ARCH。不要同时构建两个 ABI，因为 Termux 交叉编译头文件和库仍共享 /data 暂存位置。打包可读取另一个 ABI 已保存的 staging 目录，脚本会解析其绝对符号链接并检查 ELF 机器类型。

package.py 拒绝覆盖已有 package-ARCH 暂存目录；需要重打包时先检查并保留旧目录。输出 tar.xz 根目录直接包含 JDK 内容，动态库被物化为普通文件，RUNPATH 使用 $ORIGIN。所有非系统依赖的源位置和原始哈希记录在 manifest。

源代码归档中的 openjdk/ 已应用全部补丁，不要重复打补丁。scripts 中 prepare/fix/add/extend/use 开头的一次性脚本保留为实现过程记录，不是重放入口；复现源代码以官方 RI + patches/*.patch 为准。

最终检查及运行边界见 README.md。主机 Cacio 测试使用官方 Linux JDK26 加 --patch-module 测试本次 Java 兼容类；该测试不使用 ARM ELF，不能声称验证 Android 原生桥接或 GPU。