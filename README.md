# openwork-licence-audit

Kortix is open source. This repository is one runnable check for a question that decides a purchase and is not answered on any listicle: **when a project sells itself as "the open-source Claude Cowork alternative", which part of it is open source, and which part does a company pay for?**

It reads a public GitHub project's root `LICENSE`, its README and its top-level tree, and reports the licence structure: the directories carved out of the default licence, the directories under it, and any clause that makes production use depend on a subscription.

```sh
python3 check.py                            # different-ai/openwork
python3 check.py --repo owner/name          # any public repo
python3 check.py --repo owner/name --json   # machine-readable
```

Standard library only, no token, public files only.

## What it reports for OpenWork today

```
repo: different-ai/openwork (branch dev)
GitHub licence label: NOASSERTION
MIT mentioned in LICENSE/README: yes

directories carved OUT of the default licence: ee
paid-use clause: Production use requires an OpenWork subscription, except that it is
free for organizations with up to 5 users, free to evaluate for 30 days at any size,
and always free for development and testing.
```

Verified 2026-10-21 against [the repository's root LICENSE](https://github.com/different-ai/openwork/blob/dev/LICENSE) and [its README](https://github.com/different-ai/openwork/blob/dev/README.md). The README states the split in its own words: "Everything outside `ee/` is MIT — the desktop app and core platform are open source", and "Everything under `ee/` (OpenWork Den — the org control plane) is under the OpenWork EE License, a source-available license."

Note the GitHub label: `NOASSERTION`. A directory-split licence is not one SPDX identifier, so the repository's badge does not say MIT even though most of the tree is.

## What sits inside `ee/`

OpenWork's own directory table names it: **OpenWork Den — the org control plane, MCP gateway, and inference**. That is a precise list, and it is the list a company buyer should read twice. The desktop app, the shared packages and the server are MIT. The layer that turns a set of individual installs into something an organisation operates — the control plane, the gateway every connector call passes through, and the inference routing — is the layer under the EE licence.

So both statements below are true at once, and most comparison pages only make one of them:

- OpenWork is a genuinely open-source desktop agent. The application a person downloads and runs on their own files is MIT, and no account is needed to use it locally.
- The open-source part is the *individual's* part. Above five users, production use of the organisation layer needs a subscription.

Neither statement is an accusation. It is how a commercial open-source project funds itself. It is also exactly the distinction a five-person team does not need to make and a fifty-person company cannot avoid.

## Why this check exists

The search "open source claude cowork" returns lists that compare features and stars. Stars are not a buying criterion, and a licence line copied between lists is wrong within a quarter. What a buyer needs is the sentence in the repository's own LICENSE file, read on the day of the decision, with the exception directories named.

Run the same check on any candidate. The output is a decision input:

| Reading | What it means for a company |
|---|---|
| No exception directories, an OSI licence in `LICENSE` | The whole tree is open source; the vendor's paid product is hosting or support, not the code you need |
| Exception directories that hold the org layer | You can self-host the app; the organisation features are the vendor's product |
| A paid-use clause tied to seat count | Model the subscription as a per-seat cost before you compare it with anything metered |

## The alternative shape, for contrast

Kortix, the open-source AI Operating System, is one repository per company: agents, skills, memory, connector configuration and triggers are files in a git repo the company owns, and sessions run on isolated machines from that configuration ([kortix.com](https://kortix.com)). It is open source, it self-hosts for free, and on Kortix Cloud credits pay for the agent computer by the second — a stopped computer costs nothing ([pricing](https://kortix.com/pricing)). There is no separate organisation edition sold as a licence: the org layer is the repository, the permissions file and the change request a person reviews.

That is a different object from a desktop app, and the comparison only makes sense once both are named correctly. The handbook at [opensourceclaudecowork.com](https://opensourceclaudecowork.com) works through the deployment-shape question for teams, and [Kortix vs OpenWork](https://kortix.com/blog/kortix-vs-openwork) takes the feature comparison from there.

## Limits of this check

- It reads the root `LICENSE` and README. A project that licenses per file through `REUSE.toml` or `LICENSES/` (OpenWork carries both) may need a file-level read for a definitive answer; the root file is where the split is declared.
- It does not judge whether a licence is good or bad, only where the boundary sits.
- It reports the paid-use clause as written. Commercial terms change; the date on the run is part of the answer.
