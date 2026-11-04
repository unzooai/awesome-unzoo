# 多软件分发维护

## 让 Codex 操作

以后直接在这个文件夹的聊天中说：

> 发布「软件名」，版本 1.2.3，安装包在 `/绝对路径/app-1.2.3-android-arm64.apk`，更新内容是……

首次发布还需给出简介、支持的平台、软件许可说明。包名、包内版本、签名是否正确需按具体软件检查；此仓库不构建或签名软件。

维护流程：登记软件 → 提交登记信息 → 检查安装包 → 生成 SHA-256 → 创建草稿并上传 → 检查远端文件清单、大小及 GitHub 返回的摘要 → 公开发布 → 自动更新目录。日常只需提供软件与安装包，无需把软件源代码放入本仓库。

## 目录

| 路径 | 用途 |
| --- | --- |
| `software.json` | 手工维护的软件登记信息，不存版本号 |
| `catalog.json` | 从 Releases 生成的下载目录，不手工编辑 |
| `README.md` | 用户下载入口，标记区域自动更新 |
| `scripts/distribute.py` | 本地发布及目录同步工具 |
| `inbox/` | 本地临时安装包，已被 Git 忽略 |
| `.github/workflows/catalog.yml` | 验证与自动目录维护 |

## 首次登记

需要 Python 3.11+。发布还需要 [GitHub CLI](https://cli.github.com/) 已登录且对 `unzooai/awesome-unzoo` 有写权限。目录同步只需 Python；在 Actions 中使用仓库自带 `GITHUB_TOKEN`，无需另存个人令牌。

以下内容为示例，不会自动登记虚构软件：

```sh
python3 scripts/distribute.py add \
  --id my-app \
  --name 'My App' \
  --description '一句话介绍软件' \
  --platform Android \
  --license 'Proprietary; see the license included with the installer'

python3 scripts/distribute.py check
git add software.json
git commit -m 'docs: register my-app'
git push origin main
```

`id` 仅用小写英文、数字、连字符，登记后保持稳定。`license` 应准确填写该软件实际授权，不要根据本仓库的 MIT 许可证推定。

## 发布新版本

安装包建议命名为 `my-app-1.2.3-android-arm64.apk`、`my-app-1.2.3-macos-arm64.dmg` 等，使用英文、数字、点号、加号、下划线、连字符。同一版本的不同平台包一起发布。

将更新说明写在本地文件中，例如 `inbox/notes.md`：

```sh
# 先检查计划，不上传
python3 scripts/distribute.py publish my-app 1.2.3 \
  inbox/my-app-1.2.3-android-arm64.apk \
  --notes-file inbox/notes.md --dry-run

# 执行发布；先上传草稿，验证后才公开
python3 scripts/distribute.py publish my-app 1.2.3 \
  inbox/my-app-1.2.3-android-arm64.apk \
  --notes-file inbox/notes.md
```

- 自动附带 `SHA256SUMS.txt` 与 `release.json`。清单只含文件名、大小与摘要，不含本地路径。
- 使用 `--draft` 可保留完整草稿供检查，之后在 Releases 页面公开发布。
- `1.3.0-beta.1` 会自动标记预览版；也可显式加 `--prerelease`。
- 每个附件保守限制为小于 2 GiB；不使用 Git LFS 存安装包。
- 使用标签 `my-app/v1.2.3`，不同软件可以各自发布 `1.2.3`。
- 同一个版本不覆盖、不重打标签。修复应发布新版本；失败草稿先检查，保留其现状，再按实际失败步骤恢复。
- 若发布已成功而后续目录同步失败，**不要重新发布**，只需运行 `sync` 或手动触发 Actions。

## 自动维护

每次推送 main、发布/编辑/删除 Release，以及每天定时检查时，Actions 验证配置并更新 `README.md` 和 `catalog.json`，无变化不提交。也可在 Actions 中点击 **Run workflow**。草稿不进入目录；稳定版按数值版本选择，预览版独立显示。预览版主次修订号相同时按发布时间选择。

发布工具会要求软件登记信息已推送到 main。通过 GitHub 网页手工发布时，也要遵守上述标签规则并先登记软件。手工上传的包不会自动补算 SHA-256；需要先在本地生成并上传校验文件，推荐使用发布工具。

如果其他工作流使用 `GITHUB_TOKEN` 创建 Release，该事件本身不会触发另一个工作流；请在同一工作流显式同步目录，或调用 `workflow_dispatch`。每日检查也会补齐。

需要修复坏版本时，保留历史记录并在 Release 中注明问题，发布一个更高版本；不要把用户正在使用的链接悄悄换成不同内容。

## 检查与排错

```sh
python3 -m unittest discover -s tests -v
python3 scripts/distribute.py check
python3 scripts/distribute.py sync
git diff --check
```

Actions 若因分支保护不能推送目录，会明确失败；应调整目录维护方式或走 PR，不要关闭保护。发布脚本创建草稿后出错时，已上传内容会保留在草稿中，不会自动删除或强制覆盖。

## 边界

仓库只维护分发所需材料；不要提交各软件源码、凭据、签名私钥、调试日志或安装包。仅发布你有权分发的软件，软件包的许可证、签名、公证与系统兼容性应分别维护。

参考：[GitHub Releases](https://docs.github.com/en/repositories/releasing-projects-on-github/about-releases)、[GitHub CLI 发布命令](https://cli.github.com/manual/gh_release_create)、[GITHUB_TOKEN 触发规则](https://docs.github.com/en/actions/concepts/security/github_token)。
