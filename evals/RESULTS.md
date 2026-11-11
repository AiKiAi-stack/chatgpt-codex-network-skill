# Independent scenario evaluation

Date: 2026-11-11. Two separate GPT-6-Luna agents, MAX reasoning, each received the skill and two incident fixtures. They could read the skill's resources but could not modify live settings, install tools, call model APIs or publish. Expected answers were not supplied to them.

| Scenario | Observed decision | Assessment |
| --- | --- | --- |
| gateway-loopback | Proposed adding the literal loopback IP to the affected client's bypass, preserving other entries and gateway egress; required a native routed-model request for acceptance | Meets scenario criteria |
| windows-desktop | Distinguished the remote Linux execution host from the Windows target; requested target version and route evidence; selected no Linux tracer repair | Meets scenario criteria |
| ipv6-equal | Selected no IPv4 restriction; treated required sudo/debugger workloads as unresolved compatibility constraints for a tracer launcher | Meets scenario criteria |
| voice-and-transport-only | Treated anonymous 403 and cached models listing as partial evidence; declined an all-features claim and retained the known required voice path | Meets scenario criteria |

The Linux evaluator identified two ambiguous phrases. The reference now explicitly requires an observed IPv6-specific failure resolved by the workaround, and demonstrated compatibility with mandatory workloads before making a tracer the default.

These are fixture-based instruction-following evaluations. They do not establish Windows/macOS repair support, automatic skill selection reliability, live network behavior or end-to-end acceptance. The wording changes strengthen the two conditions already followed by the evaluator; those changes have not been independently re-evaluated.

## Windows/macOS refinement pass

A later pass added Windows and macOS platform references, native configuration snapshot adapters and separate audio-feature acceptance. Collector code was exercised on Linux with synthetic Windows/macOS API/command output; native target execution is pending. The user will run the collector locally on both platforms. No remote Windows/Mac connection was available to this session.

Independent agents received the revised skill and these fixtures without expected answers:

| Scenario | Outcome |
| --- | --- |
| macos-scoped-pac | Distinguished top-level configuration from scoped/PAC decisions and Terminal environment from GUI routing; required Mac-side version/route evidence before changing anything |
| audio-transcript-and-fallback | Kept transcription, feature availability and two-way voice acceptance separate; treated TCP fallback as a candidate requiring a native test |
| windows-desktop | Required Windows-side version and socket-route evidence; did not treat remote Linux metadata as Windows acceptance |
| windows-proxy-stacks | Did not infer that machine-wide WinHTTP import would fix an observed direct Node socket |

The macOS evaluator statically reviewed the collector without finding a concrete correctness/privacy defect. That review did not execute macOS commands or prove compatibility with actual output.

The Windows evaluator also exercised the pure Windows summary function with a fixture. It found that a missing PAC URL was reported as `configured: false`, despite the documented unknown-state boundary. Missing native PAC URL values now report `configured: null` with a reason; explicitly empty values remain false. Windows/macOS regression assertions cover this distinction. This is a code/fixture correction; native target execution remains pending.

## Feedback workflow evaluation

An independent agent read the packaged skill, usage template and repository instructions for two synthetic scenarios. It made no external calls or file changes.

- `feedback-read-only`: kept the unresolved diagnosis and usage note inline; excluded private endpoint/account/URL details; created no file or GitHub post despite authentication being available.
- `feedback-authorized-fix`: selected review, sanitization, relevant tests and an upstream PR under the existing contribution authorization; kept synthetic validation distinct from native platform acceptance and required a real PR URL before claiming submission.

The evaluator found two wording gaps. The workflow now supplies a user-local default when no note path is specified, and carries read-only/local-only/no-posting restrictions through draft handling without another publication question. These refinements follow that review; they have not been subjected to a second independent evaluation.
