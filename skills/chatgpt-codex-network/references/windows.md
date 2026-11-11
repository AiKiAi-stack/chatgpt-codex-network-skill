# Windows target

Use this on the Windows machine running the affected application. A WSL/Linux/SSH shell elsewhere cannot establish a Windows GUI process's configuration. Record the exact ChatGPT/Codex client, version, OS and proxy app before choosing a repair.

## Inspect

When Python 3 is installed, run the skill collector locally:

```powershell
py -3 .\scripts\inspect_environment.py --system-proxy
```

It collects current-process environment and selected current-user Internet Settings registry values. It does not inspect a running GUI process's environment, WinHTTP session policy, PAC decisions or live socket routing. Missing/inaccessible settings remain unknown. PAC URLs are summarized without their path or query; a configured PAC is not proof it was used.

If Python is unavailable, inspect the same settings locally with native tools and retain only the necessary sanitized fields. Avoid a raw registry dump. Use existing PowerShell for process/version and socket ownership, for example:

```powershell
Get-Process | Where-Object ProcessName -Match 'ChatGPT|Codex|magpie|clash|mihomo' |
  Select-Object Id,ProcessName
Get-AppxPackage '*ChatGPT*' | Select-Object Name,Version
Get-AppxPackage '*Codex*' | Select-Object Name,Version
```

Package queries can be empty for an unpackaged install. Obtain that app's version from its own UI or executable metadata. Use a selected PID with `Get-NetTCPConnection -OwningProcess <PID>` to correlate retries with direct/proxy destination addresses. PID correlation and connection state alone do not establish which URL was requested.

Windows user Internet Settings, WinHTTP default/advanced policy, process environment and per-session proxy decisions are distinct. Inspect `netsh winhttp show proxy` or `show advproxy` when the affected stack makes them relevant; redact the result. A difference between them is a diagnostic observation, not a reason to automatically import/reset machine-wide WinHTTP settings.

## Repair and verify

Choose a supported application/client proxy setting or evidenced version fix that reaches the failing socket. If preparing a process-specific launcher, preserve arguments, scope environment changes to that process tree, and fully exit/restart the GUI app. Merely setting variables in a PowerShell tab does not reconfigure a running desktop process.

Keep literal gateway loopback addresses in the applicable bypass mechanism, including IPv6 if its listener is used. Gateway upstream settings remain separate. Preserve UAC, Defender, certificate verification and the application's package/sandbox protections. Evaluate any existing Windows process-proxy tool using its actual TCP/UDP, DNS and child-process coverage; installing a driver or privileged tool is a distinct change to assess within authorization. The Linux ptrace recipe is not executable Windows repair guidance.

Accept the original authenticated operation on Windows with the intended TUN state, plus gateway and feature-specific checks. This reference supplies a documented investigation path; real Windows application acceptance is still required.

Sources: [Microsoft WinINet/WinHTTP session behavior](https://learn.microsoft.com/en-us/windows/win32/winhttp/setting-wininet-proxy-configurations-in-winhttp), [netsh winhttp](https://learn.microsoft.com/en-us/windows-server/administration/windows-commands/netsh-winhttp), [Get-NetTCPConnection](https://learn.microsoft.com/en-us/powershell/module/nettcpip/get-nettcpconnection).
