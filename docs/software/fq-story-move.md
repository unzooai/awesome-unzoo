# 番茄搬运工

把自己的本地小说批量搬运到番茄小说创作后台的 macOS / Windows 桌面工具。

应用基于 Electron，通过 Unzoo 浏览器 MCP 驱动真实浏览器，完成章节填写、发布和排期读取；支持随机操作间隔与实时搬运进度。

**仅用于把自己拥有版权的稿件发布到自己的创作后台，请勿用于抓取或搬运他人作品。**

## 下载与安装

当前版本：**0.1.3**。

| 平台 | 安装包 |
| --- | --- |
| macOS 11.0 及以上 / Apple Silicon（arm64） | [下载 DMG](https://github.com/unzooai/awesome-unzoo/releases/download/fq-story-move/v0.1.3/fq-story-move-0.1.3-arm64.dmg) |
| Windows 10 / 11（x64） | [下载 EXE](https://github.com/unzooai/awesome-unzoo/releases/download/fq-story-move/v0.1.3/fq-story-move-0.1.3-windows-x64-setup.exe) |

[版本说明与校验文件](https://github.com/unzooai/awesome-unzoo/releases/tag/fq-story-move/v0.1.3) · [软件目录与后续版本](../../README.md#下载软件)

macOS：

1. 下载 `fq-story-move-0.1.3-arm64.dmg` 并打开。
2. 将「番茄搬运工」拖入「应用程序」。
3. 从「应用程序」打开应用。

本包未完成有效的开发者签名，未附带公证票据。若首次打开提示无法验证开发者，可在「系统设置 → 隐私与安全性」中查看是否提供「仍要打开」选项；若系统仍拒绝打开，请记录完整提示并[反馈问题](https://github.com/unzooai/awesome-unzoo/issues/new/choose)。

最低系统版本来自包内声明；本次发布未执行各 macOS 版本或真实番茄后台的功能验证。该安装包面向 Apple Silicon，未提供 Intel 版本。

Windows：运行 `fq-story-move-0.1.3-windows-x64-setup.exe`，安装到当前用户目录，并创建桌面和开始菜单快捷方式。默认主程序位于 `%LOCALAPPDATA%\Programs\fq-story-move\番茄搬运工.exe`。

Windows 安装包未附带 Authenticode 签名；本次分发未在 Windows 设备上执行安装或真实后台功能验证。

## 使用前准备

- 启动 Unzoo 浏览器及 MCP 本地服务，服务地址为 `http://127.0.0.1:9399`，MCP 端点为 `/mcp`。
- 在 Unzoo 中创建对应的 profile，默认名称为「番茄」，并登录自己的番茄小说创作后台。
- 准备自己的本地小说目录，支持扁平目录和分卷子目录两种结构。

普通用户安装后，无需另外安装 Node.js。应用自带 Electron 运行时；Node.js 属于开发运行环境要求。

## 功能

| 功能 | 说明 |
| --- | --- |
| 小说管理 | 添加、编辑、删除小说，配置本地目录、番茄章节管理页地址、每日发布区间、发布时间与目录结构。 |
| 单章与批量搬运 | 将下一章填入番茄编辑器并发布；批量连续搬运，显示实时进度，支持随时停止。 |
| 发布排期 | 读取后台已排期章节，按每日发布量推算下一章的发布日期，当天排满则顺延。 |
| 章节标题同步 | 读取各卷真实章节标题与末章计划发布日期，与本地目录比对并标注已上线章节。 |
| 完篇与恢复 | 将小说标记为「完篇」，收起搬运与编辑操作，保留查看等操作，也可恢复。 |
| 登录检测 | 检查指定 Unzoo profile 是否已登录番茄创作后台。 |
| 随机操作间隔 | 章节间默认等待 5–15 秒，卷切换、翻页、点击等操作带随机延时。 |

随机延时是操作节奏设置，不保证避免平台风控。

## 使用流程

1. 启动 Unzoo 服务，确认目标 profile 已登录番茄创作后台。
2. 在应用「设置」中填写 Unzoo profile 名称和章节间隔。
3. 点击「添加小说」，填写本地目录、番茄章节管理页地址、每日发布区间、发布时间与目录结构。
4. 用「登录检测」确认后台可用。
5. 点击「开始搬运」批量发布，需要中止时点击「停止搬运」。
6. 需要校准进度时使用「同步番茄章节」或「刷新已搬运」。
7. 写完后可标记「完篇」，后续仍可恢复。

## 本机 AI 查询小说格式

打开「AI写作指南」，点击「复制 MCP 配置」，在本机 AI 客户端中添加对应的 stdio 服务。配置使用应用自带的运行时，可在桌面窗口关闭时使用；移动应用后需重新复制配置。

工具 `get_novel_format` 不传参数时返回两种小说目录结构；传入 `{"structure":"flat"}` 查询扁平目录，或传入 `{"structure":"volumeFolders"}` 查询分卷子目录。返回值包含文件命名、正文、卷名规则和示例文件。

## 0.1.3 更新

- 新增 Windows x64 安装包，改善字体、图标、文件夹选择与错误提示。
- 修复 Windows 定时发布输入，填写后核对日期、时间和定时开关。
- 支持 CRLF 换行和 UTF-8 BOM，保留正文段落并正确读取配置与卷号。
- 忽略 macOS 产生的 `._` 元数据文件，支持带引号的小说目录路径。
- 正确处理 Windows profile 路径的大小写和分隔符差异。

## 下载校验

下载同版本的 `SHA256SUMS.txt`，将以下命令的输出与其中对应安装包的一行比较。

macOS：

```sh
shasum -a 256 fq-story-move-0.1.3-arm64.dmg
```

Windows PowerShell：

```powershell
Get-FileHash .\fq-story-move-0.1.3-windows-x64-setup.exe -Algorithm SHA256
```

校验值用于核对下载文件，不等同于开发者签名、公证或功能测试。

## 许可与反馈

安装包内 `package.json` 声明软件许可证为 **MIT**。本仓库提供安装包与使用说明，不提供该软件的独立源码目录。

[反馈问题](https://github.com/unzooai/awesome-unzoo/issues/new/choose)时请注明「番茄搬运工」、软件版本、操作系统版本和复现步骤。
