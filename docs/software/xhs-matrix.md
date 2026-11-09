# XhsMatrix

通过本机 Unzoo 浏览器管理小红书账号、素材、内容派生、发布排期和养号任务。

## 下载

当前同步版本：**1.0.11**。

| 平台 | 安装包与校验 |
| --- | --- |
| macOS 12+ / Apple Silicon（arm64） | [签名公证版 DMG](https://github.com/unzooai/awesome-unzoo/releases/download/xhs-matrix/v1.0.11/xhs-matrix-1.0.11-macos-arm64.dmg) |
| Windows 10 / 11（x64） | [安装程序 EXE](https://github.com/unzooai/awesome-unzoo/releases/download/xhs-matrix/v1.0.11/XhsMatrix_1.0.11_x64-setup.exe) |

[版本说明与 SHA256SUMS.txt](https://github.com/unzooai/awesome-unzoo/releases/tag/xhs-matrix/v1.0.11)。本版本修复 Windows 最终发布按钮及养号开关帖、卡片定位与失败恢复等问题，具体行为以该版本软件为准。

## 安装与准备

- Mac：打开 DMG，将 `XhsMatrix.app` 拖入「应用程序」。本包使用 Developer ID Application 签名，并完成 Apple 公证及应用、DMG 的票据装订。
- Windows：运行 EXE 安装程序；需具备 WebView2 运行时。该 Windows 包原样同步，未附带 Authenticode 签名。
- 使用前单独安装 Unzoo Browser 并准备对应账号 profile；安装包包含所需 Node 运行时、SQLite 原生组件、FFmpeg 和 mihomo。
- 仅操作自己有权限管理的账号，发布拥有相应权利的内容。使用浏览器驱动或随机操作间隔不代表平台规则或账号风控豁免。

## 验证范围

本次检查上游原包 SHA-256、产品身份、内部版本和架构。Mac 包完成嵌套代码签名、公证票据、Gatekeeper 和 DMG 完整性验证；实际运行了签名后的 Node、内存 SQLite 查询、FFmpeg 和 mihomo 的只读检查。未执行真实发布、养号互动、账号登录或 Windows 安装测试。

应用 Info.plist 声明 10.15，但主程序及内置 Node 等实际要求 macOS 11，捆绑的 FFmpeg 要求 macOS 12，因此完整工具按 **macOS 12+** 标注；未在各系统版本上逐一测试。

下载同版本 `SHA256SUMS.txt`，将 `shasum -a 256 文件名.dmg` 或 PowerShell 的 `Get-FileHash .\文件名.exe -Algorithm SHA256` 输出与清单比较。摘要校验不能代替开发者签名验证。

主应用采用 [MIT 许可证](https://github.com/randyjin/xhs-matrix/blob/v1.0.11/LICENSE)；FFmpeg、mihomo、Node 和其他第三方组件遵循各自许可证。[上游仓库](https://github.com/randyjin/xhs-matrix) · [反馈问题](https://github.com/unzooai/awesome-unzoo/issues/new/choose)。
