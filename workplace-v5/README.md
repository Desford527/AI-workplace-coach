# AI职场沟通训练师 v5.0.4

基于 AI高压沟通教练 v4.18 的 Python 本地改造版。此版本按用户明确授权，随项目提供其指定的完整默认 API 配置，启动时自动替换原 API 条目。

## 直接启动

需要 Python 3.10 或更新版本。

- Windows：解压后进入 `workplace-v5`，双击 `start.bat`。
- macOS/Linux：执行 `bash start.sh`。
- 手动：`python server.py 8000`。

启动器会打开当前版本的实际地址。默认端口 8000，若旧服务占用，则顺延；不要继续使用旧版标签页或端口。页面底部及启动终端应显示 v5.0.4。旧服务器窗口可以先关闭。

## 此版本的默认 API

- 配置名称：`DeepSeek527`
- 地址：`https://api.deepseek.com`
- 对话模型：`deepseek-flash`
- 复盘模型：跟随对话模型
- API Key：随 `default-api.json` 提供用户所指定的值，不在文档或日志中回显。

首次启动自动读取随版本的配置，将本机旧 API 条目移除并设为上述默认配置。无需填写 Key，无需点击替换按钮。旧 `deepseek-cbx`、`deepseek-v4-flash` 与浏览器缓存不会覆盖新版默认配置。当前活动配置 ID 尽量保留，已保存对话、画像与历史不删除。

此版本已应用后，可继续正常编辑或新增多 API 配置；再次恢复旧 cbx/v4 条目时，启动会重新应用本版本的默认配置。自动替换不会发起模型请求；实际测试或训练才会调用服务商。

## 更新已有项目

如果要直接更新原安装目录，先关闭服务器，然后从新版覆盖：

- `server.py`
- `workplace.py`
- `default-api.json`
- `index.html`
- `web/app.js`
- `start.bat` / `start.sh`

保留本机 `user_data/` 和 `skills/`。重新启动后自动替换 API 配置。也可使用下方迁移工具创建新目录。

```bat
python migrate_local.py --source "D:\Projects\旧项目" --destination "D:\Projects\AI职场沟通训练师-v5.0.4"
```

目标必须尚不存在。迁移工具保留原目录、配置和历史的备份至新目录的 `legacy-backup/`；新副本第一次启动自动应用本版本默认 API。云项目设置与电脑之间没有实时同步；此版本通过随下载包的配置完成本机初始化。

## HTTP 402

DeepSeek 返回 HTTP 402 表示账户余额不足，需要到官方控制台检查余额和充值。默认配置替换不能解决服务商计费问题。程序保留用户原话，余额恢复后可重试。

## 已实现功能

8 个职场场景、对象画像查看/新建/编辑、冻结场景与画像快照、中文及英文连续对话、原话三层解读、六维及每轮平均总分、逐轮复盘、只读长期画像、SQLite 持久化、失败重试、HTML/JSON 导出及打印/PDF。模型协议使用 OpenAI 兼容 Chat Completions，仍支持多个服务商以及独立复盘模型。

评分固定为结论清晰、证据具体、诉求对齐、边界与风险、下一步行动、理解与协作。每维 0–100 整数，总分按六维平均四舍五入；原话引用、维度与逐轮覆盖严格校验。模型失败时不伪造成功。

记录存于 `user_data/workplace.sqlite3`，配置存于 `user_data/apiconfig.json`。备份时先停服务再复制整个 `user_data/`。画像单次支持最多 100 场成功复盘。旧五维 JSON 原样保留，完整旧对话可重新六维分析。

## 验证

```sh
python tests/test_workflow.py
python tests/default_setup_check.py
python tests/browser_check.py
```

浏览器测试需要 Playwright 和 Chromium；生产运行只用 Python 标准库。默认配置安装检查会核对随包 Key，但不发起模型请求、不打印 Key；其他模型测试使用替身，不代表真实服务商训练效果。完整结果见 ACCEPTANCE.md。

Windows exe 构建脚本已更新以包含默认配置，但未在 Windows 实测或交付 exe。源码启动可用。
