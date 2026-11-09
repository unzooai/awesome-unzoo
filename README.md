# Awesome Unzoo

Unzoo 软件分发中心。这里提供安装包、版本更新说明和下载校验，不包含所分发软件的源代码。

## 下载软件

<!-- catalog:start -->

| 软件 | 简介 | 平台 | 稳定版 | 预览版 |
| --- | --- | --- | --- | --- |
| 番茄搬运工 | 将自己的本地小说批量发布到番茄小说创作后台，支持排期、章节同步和进度管理。 | macOS 11+ · Apple Silicon (arm64) / Windows 10 / 11 · x64 | [0.1.3](https://github.com/unzooai/awesome-unzoo/releases/tag/fq-story-move/v0.1.3) | 待发布 |
| ContentMatrix | 通过 Unzoo 浏览器将图文内容发布到头条、百家号、大鱼号和企鹅号，管理账号、素材与发布任务。 | macOS 11+ · Apple Silicon (arm64) / Windows 10 / 11 · x64 | [0.0.11](https://github.com/unzooai/awesome-unzoo/releases/tag/content-matrix/v0.0.11) | 待发布 |
| XhsMatrix | 通过 Unzoo 浏览器管理小红书账号、素材、内容派生、发布排期和养号任务。 | macOS 12+ · Apple Silicon (arm64) / Windows 10 / 11 · x64 | [1.0.11](https://github.com/unzooai/awesome-unzoo/releases/tag/xhs-matrix/v1.0.11) | 待发布 |

<!-- catalog:end -->

- 点击上表中的版本号进入对应软件的下载页，在 **Assets** 中选择适合设备的安装包。
- [所有版本与更新记录](https://github.com/unzooai/awesome-unzoo/releases) · [问题反馈](https://github.com/unzooai/awesome-unzoo/issues/new/choose)
- GitHub 自动提供的 **Source code (zip / tar.gz)** 只是本分发仓库的快照，不是软件源代码，也不是安装包。
- 每款软件使用独立版本，例如 `my-app/v1.0.0`。本仓库的全局 “Latest” 不代表某款软件的最新版，请以上表为入口。
- 自动目录中的稳定版按版本号选择，预览版单独列出；旧版始终可从 Releases 查找。

## 软件使用说明

- [番茄搬运工](docs/software/fq-story-move.md)：将自己的本地小说批量发布到番茄小说创作后台，支持排期、章节同步和进度管理。

## 校验下载

下载所需安装包与同版本的 `SHA256SUMS.txt`，在同一文件夹内校验：

```sh
# macOS / Linux：将 app.apk 替换为实际文件名，与 SHA256SUMS.txt 中对应的一行比较
shasum -a 256 app.apk
```

```powershell
# Windows PowerShell
Get-FileHash .\app.exe -Algorithm SHA256
```

校验值用于检测下载损坏或文件变化，不代表系统签名、公证或安全审计。

## 维护与授权

维护者参见 [发布操作说明](docs/MAINTENANCE.md)。安装包上传至 Releases，Git 仅保存目录、说明和维护工具。

仓库中的维护脚本与文档采用 [MIT 许可证](LICENSE)。**各软件安装包不因托管在此仓库而自动采用 MIT 授权**，请以 [软件登记表](software.json) 中的 `license` 字段及包内许可说明为准。

机器可读下载目录：[catalog.json](catalog.json)。该目录由 GitHub Actions 在发布后自动更新。
