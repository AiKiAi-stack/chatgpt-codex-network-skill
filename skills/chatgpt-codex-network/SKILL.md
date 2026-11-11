---
name: chatgpt-codex-network
description: Diagnose and repair ChatGPT or Codex connection failures involving proxies, DNS, TLS, WebSocket streaming, or local model gateways, including failures that disappear with TUN enabled.
---

# ChatGPT / Codex network diagnosis

Identify the failing connection and choose the smallest repair that restores the user's operation. Treat an application launcher as one possible repair, selected by evidence and platform support.

## Establish the target and a reproducible symptom

Identify the affected product, app/CLI version, OS, execution host, failing action, proxy client/protocol, and any local gateway. Distinguish the agent's execution environment from the computer running the affected application. Inspect available state before asking for missing details.

Run `scripts/inspect_environment.py` when Python 3 is available on the affected host. It summarizes proxy variables without credentials; Linux also reports selected application processes and their environments. On Windows/macOS, `--system-proxy` adds a sanitized native configuration snapshot. Read [Windows](references/windows.md) or [macOS](references/macos.md) only for that target platform. The collector identifies its execution host; its output does not establish an application's effective route.

Choose a repeatable action that detects the reported failure: opening the affected cloud chat, sending a native streamed request, a Pages connection, or a gateway-backed model request. Record the initial verdict. If the real operation is inaccessible, complete useful transport checks and state what remains unverified.

Keep text chat, microphone dictation and real-time voice conversation distinct. For a reported audio problem or a claim covering audio, read [feature acceptance](references/feature-acceptance.md). Collect version/platform and actual availability first; a missing feature is not automatically a network failure.

## Locate the failing layer

Follow the actual connection owner instead of inferring routing from the window that displays the error. Consult [transport diagnosis](references/transport-diagnosis.md) for relevant probes and primary sources.

| Connection owner | Investigate |
| --- | --- |
| Chromium renderer / Electron networking | Effective session, system or PAC proxy; bypass; HTTPS/WSS reachability |
| Desktop main-process Node socket / `ws` | This app version's proxy-aware agent or connection implementation; environment inheritance alone may be insufficient |
| Codex native client | Its installed version's supported settings, proxy environment and bypass behavior |
| Agent → local model gateway | Exact loopback address, listener, `NO_PROXY` and proxy routing |
| Gateway → external provider | Gateway's own proxy and provider/account overrides |

Compare DNS, TCP, verified TLS, protocol handshake and authenticated application initialization separately. A 401, 403 or 404 to an anonymous probe establishes neither a completed WebSocket nor an account failure. Use native authenticated evidence to distinguish access, quota and transport errors. Keep credentials and request contents out of captures.

For an IPv6 hypothesis, compare IPv4 and IPv6 to the same destination through the relevant route. Preserve system-wide IPv6; apply any family workaround to the narrowest evidenced scope. TUN success is a diagnostic observation, not a security verdict or proof that all protocols require TUN.

## Select and apply a repair

Prefer supported app/client/gateway configuration when it covers the actual failing path. Check current primary documentation and version-specific fixes before retaining a workaround. Retest after changing one relevant variable.

When supported configuration leaves a demonstrated direct socket path, compare the user's acceptable alternatives using the target-platform reference. For a Linux application that must run without TUN, read [the process-scoped fallback](references/linux-process-proxy.md). Preserve a working voice route while checking any officially supported TCP fallback in the actual client.

Apply changes within existing user authorization. Prepare the exact files/settings and rollback before seeking authorization for additional scope. Installing a skill does not authorize proxy changes, app restarts, downloads or publication. Preserve certificate verification, application sandboxing and privilege controls. If a candidate requires weakening those controls, leave it uninstalled and report that constraint.

Keep local-gateway requests and established LAN/SSH routes working. Configure gateway egress separately. Discover executable paths, ports, user directories and proxy authentication; host-specific values are inputs, not defaults copied from an example. Protect downloaded helpers with a verified release identity and retain their license.

## Verify and deliver

Re-run the original failing operation under the intended final network state. Validate each gateway route and any affected SSH/LAN path. For a launcher, also check native sandbox preservation, restart persistence and rollback. Instruction-following evaluations and transport diagnostics are separate from end-to-end app acceptance.

When a TUN toggle can disconnect the current session, use an independent bounded restoration mechanism as well as normal cleanup, and confirm restoration. Coordinate launcher activation when the running app hosts this conversation; distinguish installed files from the active process.

Report the cause, changes, observed tests and remaining limits, including OS/client version and TUN state for each feature. Distinguish passed, failed, not tested and unavailable in this client. Store only sanitized findings, never authentication files or full personal application profiles.

After a diagnosis or repair, read [usage records and contributions](references/feedback.md). Record the actual outcome and any reusable improvement; prepare an Issue or PR when useful and submit within the current user's authorization. Keep unresolved results and unsubmitted drafts explicit.
