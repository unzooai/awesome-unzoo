# ContentMatrix

通过本机 Unzoo 浏览器管理图文内容、账号、素材和发布任务，支持头条、百家号、大鱼号和企鹅号。

## 下载

当前同步版本：**0.0.11**。

| 平台 | 版本 | 安装包与校验 |
| --- | --- | --- |
| macOS 11+ / Apple Silicon（arm64） | 0.0.11 | [签名公证版 DMG](https://github.com/unzooai/awesome-unzoo/releases/download/content-matrix/v0.0.11/content-matrix-0.0.11-macos-arm64.dmg) · [版本说明与 SHA256SUMS-macos.txt](https://github.com/unzooai/awesome-unzoo/releases/tag/content-matrix/v0.0.11) |
| Windows 10 / 11（x64） | 0.0.11 | [安装程序 EXE](https://github.com/unzooai/awesome-unzoo/releases/download/content-matrix/v0.0.11/ContentMatrix_0.0.11_x64-setup.exe) · [版本说明与 SHA256SUMS.txt](https://github.com/unzooai/awesome-unzoo/releases/tag/content-matrix/v0.0.11) |

0.0.11 改善 Windows 后台命令窗口和头条助手遮挡按钮时的处理。Mac 构建包由上游补充发布，本仓库完成签名和公证后同步。

## 安装与准备

- Mac：打开 DMG，将 `ContentMatrix.app` 拖入「应用程序」。本包使用 Developer ID Application 签名，并完成 Apple 公证及应用、DMG 的票据装订。
- Windows：运行 EXE 安装程序；需具备 WebView2 运行时。该 Windows 安装包原样同步，未附带 Authenticode 签名。
- 使用前安装并登录 Unzoo Browser，确保对应账号 profile 可用。安装包自带执行环境，无需另装 Node.js。
- 仅向自己有权限操作的账号发布拥有相应权利的内容。

## 验证范围

本次检查了原包的上游 SHA-256、产品身份、内部版本和架构；Mac 包检查签名、公证票据、Gatekeeper、DMG 完整性，并验证内置 Node SEA CLI 的隔离命令分发。未运行真实平台发布或账号登录操作，也未在 Windows 设备上执行安装验证。

Mac 包的 Info.plist 声明 10.13，但主程序及 CLI 的 Mach-O 构建信息均要求 11.0，因此本仓库按 **macOS 11+** 标注；这不是对各 macOS 版本的设备测试结果。

Mac 下载同版本的 **`SHA256SUMS-macos.txt`**，Windows 下载 **`SHA256SUMS.txt`**。将 `shasum -a 256 文件名.dmg` 或 PowerShell 的 `Get-FileHash .\文件名.exe -Algorithm SHA256` 输出与对应清单比较。摘要校验不能代替开发者签名验证。

主应用采用 [MIT 许可证](https://github.com/randyjin/content-matrix/blob/v0.0.11/LICENSE)，第三方组件遵循各自许可证。[上游仓库](https://github.com/randyjin/content-matrix) · [反馈问题](https://github.com/unzooai/awesome-unzoo/issues/new/choose)。
