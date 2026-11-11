# Transport diagnosis

Use the branches relevant to the user's operation. Record target host, app version and evidence scope with each conclusion.

## Compare routes

1. Confirm the listener and proxy protocol using the configured address. An HTTP proxy can carry HTTPS/WSS through CONNECT; a gateway API port is a different service.
2. Compare the affected process's environment with its parent and children. A successful shell request establishes the shell route, not the GUI main process's route. Desktop policy/PAC may exist even when environment variables are empty.
3. Probe the same destination directly and through the configured proxy where permitted, with verified certificates and bounded timeouts. Keep anonymous transport probes free of authentication.
4. Where IPv6 is implicated, vary only the address family. Determine whether DNS, the proxy's outbound connection or target TLS fails before choosing a workaround.
5. Observe the actual app's handshake, initialization and operation. An HTTP status or open TCP connection is a narrower observation.

Use existing tools such as curl and OS network/log interfaces. Redact proxy credentials, bearer tokens, cookies, signed URLs and private payloads before displaying or retaining evidence. Raw process arguments and profiles may contain secrets and personal paths.

## Interpret observations

| Observation | Next discriminating check |
| --- | --- |
| Browser works; desktop cloud chat fails | Compare Chromium requests with desktop main-process socket routing |
| Codex CLI works; desktop fails | Identify the client/process owning the failing request |
| Proxy variables present but WSS fails | Check this version's connection implementation and actual route |
| Authenticated native request returns access/quota error | Inspect the product/account/provider response; packet routing may be irrelevant |
| Local gateway returns 502 | Check whether the request reached the gateway, then its upstream |
| TUN works; proxy mode fails | Locate a bypassed socket, DNS/address-family difference or required UDP path |

## Local gateways

Discover the listener instead of assuming its usual port. Check exact loopback bypass entries in the client's network library; `localhost` or a wildcard need not match literal `127.0.0.1`. IPv4 and IPv6 may have different listeners.

Where requests still enter Clash/mihomo, local-address DIRECT rules can complement client bypass configuration. Preserve existing equivalent rules. Gateway outbound traffic follows its own settings, possibly overridden by individual providers/accounts. Prefer its documented CLI/API/UI to editing live settings behind its process.

Magpie is an example, not a dependency. A native model request reaching its configured upstream verifies more than listing cached models.

## Primary sources

Recheck installed-version behavior when using current documentation or default-branch source.

- [OpenAI network requirements](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps): HTTPS/WSS and voice requirements.
- [Electron proxy switch](https://www.electronjs.org/docs/latest/api/command-line-switches#--proxy-serveraddressport): Chromium proxy configuration.
- [Electron fuses](https://www.electronjs.org/docs/latest/tutorial/fuses): packaged-app environment/debug injection controls.
- [Codex outbound proxy source](https://github.com/openai/codex/blob/main/codex-rs/http-client/src/outbound_proxy.rs): version-sensitive native behavior.
- [Desktop WSS report #49829](https://github.com/openai/codex/issues/49829): reporter observations with version boundaries; match local evidence before assigning the same cause.
- [Magpie documentation](https://usemagpie.ai/docs/start): gateway and loopback guidance.
