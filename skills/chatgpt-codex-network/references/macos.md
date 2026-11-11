# macOS target

Run checks on the Mac containing the affected application. Record its exact client/version and launch method. An environment set in Terminal may differ from a GUI process launched through Finder/Dock.

## Inspect

When Python 3 is available, run:

```sh
python3 scripts/inspect_environment.py --system-proxy
```

The optional native snapshot uses `/usr/sbin/scutil --proxy` and summarizes selected top-level HTTP/HTTPS/SOCKS/PAC fields. It excludes PAC paths/queries and unrelated nested scoped settings. Scoped/interface/PAC decisions and a running GUI process's environment remain uncollected. With no top-level manual proxy, the app can still use scoped or PAC policy.

If Python is unavailable, inspect locally with `scutil --proxy` and relevant service settings in System Settings → Network → service → Details → Proxies. Keep shared findings sanitized. `scutil --dns` can clarify resolver scope when DNS is implicated; keep private domains out of published reports.

Find the actual application rather than assuming `/Applications` or a particular bundle name. Read version/bundle identity from its metadata or UI. Correlate a selected app PID's retries with socket destinations using `lsof -nP -a -p <PID> -iTCP`. Do not bulk-dump process environments or app profiles to discover auth settings.

## Repair and verify

Use supported client/session/system proxy settings that cover the actual failing stack. Check relevant app-version fixes before choosing a workaround. A process-specific Terminal launch may test environment inheritance but needs a full app exit and confirmation that the new process owns the connection. `open -a` may activate an existing instance; shell variables are not proof of GUI inheritance.

Preserve code signing, hardened runtime, SIP, certificate validation and application sandboxing. Inspect relevant Electron fuses before proposing Node/debug injection into an Electron client; those mechanisms may be disabled, and a product with a native implementation may not use Electron. Linux ptrace/LD_PRELOAD instructions do not establish macOS compatibility. Any available macOS per-app proxy needs its own TCP/UDP, DNS and child-process assessment.

For wrong-certificate errors, investigate TLS inspection and the actual trust path. Follow supported network/app guidance without replacing trust validation with insecure TLS flags. Keep local gateways and LAN/SSH direct where intended, and configure gateway egress independently.

Accept the original authenticated operation in the Mac app with the intended TUN state. This reference and parser tests are not macOS runtime acceptance.

Sources: [Apple scutil manual](https://github.com/apple-oss-distributions/configd/blob/main/scutil.tproj/scutil.8), [Apple proxy settings](https://support.apple.com/guide/mac-help/change-proxy-settings-on-mac-mchlp2591/mac), [Electron fuses](https://www.electronjs.org/docs/latest/tutorial/fuses), [OpenAI network guidance](https://help.openai.com/en/articles/9247338-network-recommendations-for-chatgpt-errors-on-web-and-apps).
