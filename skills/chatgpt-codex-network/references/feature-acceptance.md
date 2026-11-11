# Feature acceptance

Use when diagnosing audio or making claims that include it. Check feature availability for the exact app/version/account before running a network acceptance test.

## Distinguish the operation

| Feature | Native acceptance signal |
| --- | --- |
| Text chat / Codex stream | A new authenticated request completes and streams normally |
| Microphone dictation | A short spoken phrase becomes text in the intended input field |
| Real-time voice conversation | The user and assistant exchange audio; assistant playback and a second conversational turn work |
| Gateway-backed model | A native client receives a fresh answer from that gateway's external provider |
| Pages realtime | The available Pages operation opens/connects and performs the relevant edit/update |

A user saying “can you hear me?” followed by a transcript establishes that input arrived as text. It does not establish a successful two-way voice call, identify which component transcribed it, or prove that dictation used the same route as text chat.

## Test audio

First separate microphone permission/device problems from network failures. Use the available UI and metadata, and request only the brief human microphone interaction actually needed. Avoid recording or retaining private speech by default. A sample such as “This is a microphone test” is sufficient.

OpenAI's network guidance describes real-time voice over UDP 3478 with TCP 443 fallback when UDP is unavailable. A TCP-only proxy can therefore be a candidate, but fallback must work in the actual client before claiming voice support. It is equally invalid to infer voice success from text/WSS or to declare TCP-only voice impossible just because UDP is absent. Preserve the known working route while comparing them.

For each required feature, record target OS, client version, network route/TUN state, action, result and evidence. Use `passed`, `failed`, `not_tested`, or `unavailable_in_this_client`. Keep fixture-based reasoning and live acceptance separate. Report connection/playback/reconnection problems independently when they differ.

Sources: [OpenAI dictation FAQ](https://help.openai.com/en/articles/12168547-voice-dictation-faq), [ChatGPT Voice](https://help.openai.com/en/articles/20001274-chatgpt-voice), [OpenAI network requirements, voice firewall settings](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps). Check current product availability rather than applying a historical platform retirement notice to every later client.
