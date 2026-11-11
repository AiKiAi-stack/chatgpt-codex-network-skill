# 在 Windows 和 Mac 上本地采集

解压采集包后，在 `chatgpt-codex-network` 文件夹中打开终端。脚本需要 Python 3；整个文件夹也可以交给目标机器上的 Agent，由它读取 `SKILL.md` 并执行本机只读采集。缺少 Python 时，Agent 可按相应平台参考使用已有系统工具。

如果下载或克隆的是完整 GitHub 仓库，先进入其中的 `skills/chatgpt-codex-network` 目录，再执行下面的命令。

## Windows PowerShell

```powershell
py -3 .\scripts\inspect_environment.py --system-proxy --no-processes |
  Out-File -FilePath windows-network.json -Encoding utf8
```

如果机器使用 `python` 而没有 `py` 启动器，可使用已经安装的 Python 3 命令。此处的快照包含当前终端代理环境与当前用户 Internet Settings；运行中的 GUI 进程环境、WinHTTP 策略、PAC 决策和真实路由仍需后续检查。

## macOS Terminal

```sh
python3 scripts/inspect_environment.py --system-proxy --no-processes > macos-network.json
```

快照包含当前终端代理环境与 `scutil --proxy` 的部分顶层字段。界面程序的实际环境、PAC 对某个 URL 的决定和接口作用域配置仍需后续检查。

## 同时记录

- 操作系统版本，应用名称和版本：ChatGPT 或 Codex、桌面应用或 CLI。
- 代理软件名称；采集时 TUN 开启还是关闭。
- 原本失败的具体操作，以及本机是否也使用 Magpie 或其他模型网关。

采集过程读取配置并输出摘要，保持网络和应用状态。它不连接外部测试端点、不读取登录文件、不采集麦克风、不重启应用。JSON 隐藏代理凭据及 URL 路径/查询，仍保留代理服务器主机和端口；分享前可检查这些字段。

将生成的 `windows-network.json` / `macos-network.json` 与上述信息放回本聊天或交给本机 Agent。PowerShell 可能写入 UTF-8 BOM；Python 读取时可以使用 `encoding='utf-8-sig'`。个人采集结果留在仓库之外。

## “语音”分别指什么

听写是按麦克风，把话变成输入框中的文字。双向语音通话需要用户说话、助手播放声音，并能继续下一轮。收到一段转写文本只验证了文本到达。

先验证实际使用的功能。文字、听写、双向语音和 Pages 分别记录 `passed`、`failed`、`not_tested` 或 `unavailable_in_this_client`。官方语音网络说明支持 UDP 与 TCP 回退；TCP-only 方案是否能通话，要在对应客户端中验证。
