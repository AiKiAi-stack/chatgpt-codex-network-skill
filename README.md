# ChatGPT / Codex Network Skill

供 Agent 使用的网络故障诊断与修复 Skill，处理 ChatGPT / Codex 的代理、DNS、TLS、WebSocket 和本地模型网关问题。目标是让 Agent 找到实际失败的连接、选择适合当前环境的修复方法，并在原应用中验收。

这是一个以 Skill 为交付物的 GitHub 项目。Skill 保存判断流程与证据要求；需要持续运行的代理由目标机器上的工具或启动器承担。[Agent Skills 规范](https://agentskills.io/specification)、[OpenAI Skills 文档](https://developers.openai.com/plugins/concepts/skills)。

状态：v0.1 实验版。已包含一个经过测试的 Ubuntu 场景，以及 Windows/macOS 的平台诊断指引和只读配置采集。后两者仍待实机执行与应用验收。

项目地址：[AiKiAi-stack/chatgpt-codex-network-skill](https://github.com/AiKiAi-stack/chatgpt-codex-network-skill)。

## 使用

将整个 `skills/chatgpt-codex-network` 目录安装到目标 Agent 支持的技能目录，或让它直接读取其中的 `SKILL.md`。显式调用示例：

```text
Use $chatgpt-codex-network to diagnose why my ChatGPT desktop works only with TUN enabled. I also use a local model gateway. Preserve its routing and verify the result in the desktop app.
```

只读环境摘要：

```sh
python3 skills/chatgpt-codex-network/scripts/inspect_environment.py
```

摘要隐藏代理用户名、密码、URL 路径和查询参数。Linux 下还可读取相关进程的代理环境。在 Windows/macOS 本机增加 `--system-proxy`，可采集当前用户 Internet Settings 或 scutil 顶层代理配置。摘要保留代理主机和端口，不采集 PAC 内容或逐 URL 决策；这些配置仍不代表应用的实际流量路径。详见 [本地采集说明](COLLECT.md)。

## 如何选择方法

| 观察到的原因 | 候选处理 | 主要边界 |
| --- | --- | --- |
| 应用或子进程没有使用受支持的代理配置 | 修正相应配置与继承关系 | 必须覆盖实际失败的网络栈 |
| 当前版本存在已修复的代理缺陷 | 验证合适版本并评估更新 | 需要核对当前版本、变更和回归情况 |
| 本地网关请求被代理接管 | 修正回环绕过和网关自己的出口 | 客户端与网关上游是两段连接 |
| Linux 应用仍存在无法配置的直连 TCP 路径 | 评估应用进程转发 | ptrace 可能影响 sudo、调试器和性能 |
| 必要功能依赖当前 UDP/TUN 路径 | 保留可用路径，另行验证替代方案 | TCP 连通不能证明实时语音可用 |

Ubuntu 参考场景中的 graftcp 启动器是有版本边界的成功案例。`RES_OPTIONS=no-aaaa` 只在 IPv6 对照测试证明需要时采用。Skill 优先使用覆盖问题的原生配置和有依据的版本修复，保留用户自己的目标与限制。

## 目录

```text
skills/chatgpt-codex-network/
  SKILL.md
  agents/openai.yaml
  scripts/inspect_environment.py
  references/transport-diagnosis.md
  references/linux-process-proxy.md
  references/windows.md
  references/macos.md
  references/feature-acceptance.md
  references/feedback.md
  assets/usage-note.md
tests/test_inspect_environment.py
evals/scenarios.json
```

仓库不携带个人日志、账户文件、模型密钥、用户启动器或代理二进制。Linux 转发参考使用的 [graftcp](https://github.com/hmgle/graftcp) 是独立的上游项目；Agent 在选择该方法后核实版本、校验值、许可证与目标环境。

## 验证与范围

运行代码测试：

```sh
python3 -m unittest discover -s tests -v
```

测试覆盖敏感字段隐藏、回环匹配、无效输入、进程环境不可读、Windows 注册表读取与代理映射、macOS 顶层/作用域配置隔离，以及命令失败时的未知状态。Windows/macOS 采集分支当前使用模拟系统输入和 API 测试，并非原生系统运行结果。

`evals/scenarios.json` 供独立 Agent 进行场景评估，包含网关回环、远程主机与 Windows 目标不一致、不同 Windows 代理栈、macOS PAC/作用域配置、IPv6 与提权工作负载，以及音频转文字和 TCP 语音回退边界。评估结果保存在 `evals/RESULTS.md`。

格式校验、代码测试、Agent 场景测试和真实应用验收分别记录。它们不能互相替代。

Ubuntu 先前实测覆盖 durable WebSocket 初始化、Magpie 模型请求、LAN SSH 直连和原生渲染沙箱保留。Windows/macOS 实机采集、修复实施、Pages 编辑、实时语音、长期性能和提权密集任务分别等待验证。文本输入、麦克风听写和双向语音通话按功能分别验收。

## 使用记录与共同改进

使用 Skill 的 Agent 在结束后生成简短的本地使用记录，包含实际环境、尝试过程、验证结果、遗留问题及可复用改进。普通成功记录可以留在本地；新平台验证、可复现故障或明确改进适合整理成 Issue 或 PR。

入口是随 Skill 分发的 [反馈流程](skills/chatgpt-codex-network/references/feedback.md) 和 [使用记录模板](skills/chatgpt-codex-network/assets/usage-note.md)。因此，即使只安装技能目录，Agent 也能找到记录和贡献指引。[AGENTS.md](AGENTS.md) 指导仓库内维护工作。

记录先留在用户本机。公开提交使用去除凭据、账户信息、私有地址和个人路径的副本；用户当次已经授权贡献/发布时，Agent 准备并检查后提交，否则保留完整草稿。项目不自动上传采集数据。
