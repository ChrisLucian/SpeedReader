---
name: windows-code-signing
description: Use when Windows Smart App Control / SmartScreen blocks the SpeedReader EXE, or when changing the signing step in build.ps1.
---

# Windows code signing (Smart App Control)

- HIGH-RISK/REPEAT: Smart App Control (SAC) trusts only signatures chaining to a Microsoft-trusted CA, or binaries with cloud reputation. **Self-signed certs never work** — do not suggest them.
- HIGH-RISK/REPEAT: SAC checks DLLs/`.pyd`s too, not just the EXE. Sign every binary in `SpeedReader.dist` that isn't already `Valid` (python314.dll etc. are PSF-signed; leave them alone).
- Cheapest trusted path: Azure Artifact Signing (formerly Trusted Signing). `build.ps1` uses Microsoft's `sign` dotnet tool:
  `sign code artifact-signing <files> -ase <endpoint> -asa <account> -ascp <profile>` (`trusted-signing` subcommand is deprecated). Verify flags with `sign code artifact-signing --help`.
- Config: env vars `ARTIFACT_SIGNING_ENDPOINT`, `ARTIFACT_SIGNING_ACCOUNT`, `ARTIFACT_SIGNING_PROFILE`. No secrets in the repo; auth is `DefaultAzureCredential` (`az login --scope "https://codesigning.azure.net/.default"`).
- Endpoint must match the account's region (e.g. `https://eus.codesigning.azure.net`). Signer needs the *Certificate Profile Signer* role.
- Certs live 72h; always timestamp (the tool's default does). Never pin thumbprints.
- Check SAC state: `(Get-ItemProperty HKLM:\SYSTEM\CurrentControlSet\Control\CI\Policy).VerifiedAndReputablePolicyState` (0 off, 1 on, 2 evaluation).
- Verify: `Get-AuthenticodeSignature SpeedReader.dist\SpeedReader.exe` → `Valid`.
- One profile (`Chris-Lucian-Cert-Profile`, publisher `Christopher Lucian`) signs ALL projects (open source + Steam games); `ARTIFACT_SIGNING_*` vars are deliberately generic, set once per machine. Game builds: see user skill `artifact-signing-games`.
- Privacy: leave "Include street address/postal code" unchecked on profiles — the subject is public in every signed file.
