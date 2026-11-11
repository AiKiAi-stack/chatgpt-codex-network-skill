# Linux process-scoped fallback

Read this for an evidenced socket path that supported proxy configuration does not cover, when the user wants an application-scoped alternative to TUN. This is a candidate implementation, not a universal preferred method.

## Decision boundary

[graftcp](https://github.com/hmgle/graftcp) redirects TCP connect syscalls for an application and descendants through SOCKS5/HTTP, with optional UDP/53-to-TCP DNS forwarding. It uses ptrace and seccomp. Tracing can affect privilege-changing subprocesses such as sudo, debuggers and performance. Require demonstrated compatibility with the user's mandatory workloads before activating it as the default entry point; keep an ordinary launch route.

The upstream v0.8.3 relay uses a wildcard TCP listener for unique 127/8 route tokens. Unregistered destination addresses are rejected; this differs from binding only to loopback. Account for that implementation when assessing exposure. Replacing TUN does not automatically improve overall security.

Preserve native sandboxing. A tracer's own `Seccomp=2` is insufficient proof: compare native namespaces, NoNewPrivs and filter evidence with ordinary startup. Reject this candidate if it needs the app sandbox disabled.

## Prepare a host-specific launcher

Discover the executable, original desktop entry, working proxy and direct networks. Verify the release asset/checksum from upstream; record platform and architecture. Keep helpers and licenses separate from personal diagnostics.

The launcher checks proxy availability, sets supported client proxy options, then starts the original application under the tracer. Pass arguments as an array, preserving URLs and filenames. Chromium HTTP proxy/bypass settings cover its network stack while tracing covers unconfigured Node TCP sockets.

Configure this tracer version's DNS support deliberately: it may require DNS-over-TCP reachable through the proxy. Preserve local services and LAN/SSH networks. Keep UDP/voice explicit: a TCP recipe does not cover all application traffic. Disabling QUIC can select Chromium's TCP route, but does not establish voice acceptance.

Apply IPv4-only resolution when an address-family comparison demonstrates an IPv6-specific failure and the scoped workaround resolves it. Equal successful results do not justify a family restriction. On supported glibc systems, process-scoped `RES_OPTIONS=no-aaaa` suppresses stub-resolver AAAA queries. It affects descendants, leaves explicit IPv6/hosts addresses usable, and conflicts with application DNSSEC validation. Re-evaluate it when the IPv6 path changes. [Resolver semantics](https://man7.org/linux/man-pages/man5/resolv.conf.5.html).

Install a per-user desktop override with backups and an ordinary-launch action after isolated tests pass. Preserve the package-managed app. Record whether the new process is active: a single-instance app can receive new arguments while the old process remains unwrapped.

## Acceptance

- Reproduce the native failure without interception, then repeat with the launcher and TUN off.
- Exercise a gateway request reaching its upstream, plus affected LAN/SSH routes.
- Check native sandbox evidence, startup after full exit, and restore/remove behavior.
- Report elevation, debugging, voice/UDP, other OSes and long-running overhead according to what was tested.

## Bounded prior observation

One Ubuntu installation of ChatGPT 26.1021.22027 was tested on 2026-11-11 with graftcp v0.8.3. Ordinary startup failed to initialize durable WSS with TUN off; a process launcher plus an evidenced IPv4 DNS workaround initialized that authenticated path. A local Magpie model request succeeded, LAN SSH remained direct, and native renderer sandbox evidence was preserved. Voice/UDP, Pages editing, elevation-heavy workflows and long-term overhead were not accepted. This is a regression scenario, not proof for a different host/version.
