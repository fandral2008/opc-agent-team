English | [中文](README.md)

# opc-agent-team

A set of 33 role cards for one-person companies (OPC): QA, design, engineering, growth, customer success, executive review, risk control and market insight, written as AI agent prompts. Each card runs as a Claude Code subagent or can be handed to Codex or any agent that reads Markdown. Cards are generic; everything project-specific lives in your own `project-profile.md`. Default posture is read-only, test accounts and fake data only.

Each role a one-person company needs is packaged as a named, callable agent card: 33 roles covering quality, design, engineering, growth, customer success, business review, risk control and insight. It suits small SaaS products and setups such as a WeChat mini program plus a web admin console, and is not tied to any specific project.

Three design principles:

- Role cards are generic. Project differences go only into your own `project-profile.md`, which every role reads before starting.
- Each role answers only its own class of questions. Conclusions must come with evidence (screenshots, code locations, data); an agent's report counts only as a lead to be verified.
- Read-only by default, with test accounts and fake data only. Publishing, sending messages, production writes, payments and price changes are never done; the role only produces recommendations and draft copy.

## Role table

| Department | Role name | Role | When to dispatch |
| --- | --- | --- | --- |
| Orchestration | `chief-of-staff` | Chief of staff | Use when you need to decide which roles to dispatch this time, write a run plan, and consolidate, de-duplicate and triage the reports from all roles |
| Business | `ceo-reviewer` | Executive review | Use when you need a judgment on product direction, investment trade-offs, or whether to continue, adjust or stop |
| Business | `finance-pricing` | Pricing and unit economics | Use when you need to design or adjust paid tiers and virtual-credit pricing, work out cost and gross margin, or design paid-validation experiments |
| Business | `legal-counsel` | Legal counsel | Use before charging or signing, to sort out agreement text, intellectual property, entity and revenue ownership, and billing and invoices, and to list the items a practicing lawyer must confirm |
| Business | `legal-compliance` | Compliance | Use for mini program platform review rules and categories, privacy and personal information, virtual goods and inducement behavior, open-source licenses, content safety, and promotional wording |
| Risk | `risk-control-reviewer` | Risk-rule review | Use before credits, rewards, invites, promotions, free periods or reporting rules go live or change, to review whether they can be gamed and to recommend limits and monitoring |
| Insight | `cross-domain-strategist` | Cross-domain strategist | Use when growth hits a bottleneck or during quarterly planning, to borrow proven mechanisms from other industries and design small experiments with pass/fail thresholds |
| Insight | `market-scout` | Competitor and hit-product scout | Use to periodically scan competitors, alternatives and recent hit products using public information only, and distill what is worth learning and what is not |
| Product | `data-analyst` | Data analysis | Use to examine funnels, define activity and retention metrics, find metric gaps, and set read-only aggregate query standards |
| Product | `product-manager` | Product manager | Use to turn requirements, feedback or defects into a problem definition, options and proposals, and to judge whether something should be a configuration rather than a code change |
| Product | `user-researcher` | User research | Use to prepare interview outlines, categorize user feedback, and run simulated user interviews while stating their limits |
| Design | `interaction-designer` | Interaction design | Use to review navigation structure, back paths, popups and keyboard operation, and the completeness of empty, error and not-enabled states |
| Design | `ux-writer` | UX writing | Use to unify interface wording, check button verbs and whether error messages are actionable, and maintain the glossary |
| Design | `visual-design-reviewer` | Visual design review | Use to review a screenshot wall of interface hierarchy, spacing, color, themes and skin combinations, and to propose improvements against an award-level quality standard |
| Engineering | `architect-reviewer` | Architecture review | Use to review technical plans, configurability, data models and migration risk, and to judge whether the Nth customer should require a code change |
| Engineering | `code-reviewer` | Code review | Use to review code changes for correctness, regression risk and test coverage, and to find what will break in real use |
| Engineering | `release-sre` | Release and SRE | Use to prepare release checklists, verify backups are restorable, design rollback, and check health, capacity and disk alerts |
| Engineering | `security-reviewer` | Security review | Use to review privilege escalation, tenant isolation, tokens and sessions, injection, log redaction and dependency vulnerabilities |
| Quality | `qa-accessibility` | Accessibility testing | Use to check large fonts, senior-friendly mode, color blindness, contrast, touch target size and screen-reader support, so that every kind of user can use the product |
| Quality | `qa-cross-platform` | Cross-platform consistency testing | Use to check that the mini program, the web admin console and the user manual agree on features, data, terminology and steps |
| Quality | `qa-daily-task-tester` | Daily-task walkthrough testing | Use to run the tasks users do every day end to end in a test tenant, recording step counts, time and sticking points, and checking that every read surface is consistent after a write |
| Quality | `qa-edge-case-breaker` | Edge-case and failure breaking | Use to actively break features with abnormal input, month and year boundaries, time zones, offline and weak networks, backgrounding, repeated taps, unsaved back navigation, keyboard occlusion and the Android back button |
| Quality | `qa-new-user-tester` | New-user experience testing | Use to walk through the first-time experience as a zero-context new user, covering different types of newcomers, with an independent review agent cross-checking |
| Quality | `qa-performance` | Performance testing | Use to check first-screen time, mini program package-size headroom, slow-endpoint p95, memory usage and long-list smoothness |
| Quality | `qa-permission-tester` | Identity and permission testing | Use to test permissions with a matrix of identities and entry points, cross-tenant access, read-only limits when acting on behalf of someone, and late responses |
| Growth | `channel-bd` | Channel partnerships | Use to find and evaluate channels such as industry associations, conferences, peer communities and partners, and to prepare collaboration outlines and evaluation sheets |
| Growth | `community-ops` | Community operations | Use to run user groups, look after seed users, organize a co-builder program and plan the operating rhythm |
| Growth | `content-marketer` | Content marketing | Use to plan topics and material for WeChat official accounts, Xiaohongshu, Moments and WeChat Channels, using real scenarios rather than unauthorized customer cases |
| Growth | `growth-hacker` | Growth | Use to design acquisition loops, invite and sharing mechanics and the first activation step, with the team as the unit of growth |
| Growth | `search-aso` | Search and store optimization | Use to optimize WeChat search, mini program name and description keywords, app store listings and website search indexing |
| Customer Success | `onboarding-specialist` | Customer onboarding | Use to design the onboarding path for new customers, prepare templates, shorten time to first success, or diagnose a new customer who is blocked during onboarding |
| Customer Success | `retention-churn` | Retention and churn | Use to design churn warning signals, follow-up outlines, and renewal and reactivation experiments |
| Customer Success | `support-desk` | Support desk | Use to categorize tickets, maintain the FAQ, keep the manual consistent with the interface, and write reply copy |

## Get started in 5 minutes

1. Copy `project-profile.template.md` to `project-profile.md` in your project root and fill it in: product form, how to obtain test accounts, writable scope, forbidden actions, release cadence, key metrics. Do not put passwords in it; write only how to obtain them.
2. Build and install the roles:

   ```
   python3 scripts/build.py && cp dist/claude-code/agents/*.md ~/.claude/agents/
   ```

   To use them only inside one project, change the target to that project's `.claude/agents/`.
3. First call `chief-of-staff` by name and tell it the scenario for this run (for example "release next Wednesday"). It picks roles by consulting `playbooks/` and fills in `templates/run-plan.md`.
4. Call the roles one by one according to the plan; each role hands back a report using `templates/report.md`.
5. Have `chief-of-staff` consolidate and de-duplicate, producing a one-page triage sheet that you use to decide the order of work.

## How to run

Claude Code: after installing, call a role by name in the conversation, for example "use qa-permission-tester to run the permission matrix against the project profile". You can also let the main conversation dispatch automatically based on each description.

Codex, Antigravity or other agents: after building, each role has a complete Markdown file (`dist/markdown/<name>.md`, with the shared boundaries appended). Add one line to your project's `AGENTS.md`:

```
When a quality check is needed, follow <path to this repo>/dist/markdown/qa-permission-tester.md, and read project-profile.md in the project root first.
```

## Automation helper

The repo includes a lightweight dispatch helper, `scripts/runner.py` (no third-party dependencies):

1. **Generate a plan from a playbook**:
   ```bash
   python3 scripts/runner.py plan pre-release --out run-plan.md
   python3 scripts/runner.py plan pre-release --reports ./reports   # carries over the P0/P1 items from the last triage sheet
   ```
2. **Suggest roles from changed files**:
   ```bash
   python3 scripts/runner.py suggest src/auth/guard.ts src/billing/pricing.vue
   git diff --name-only | python3 scripts/runner.py suggest -
   ```
3. **Consolidate and triage reports from multiple roles**:
   ```bash
   python3 scripts/runner.py triage ./reports --out triage-summary.md
   python3 scripts/runner.py triage ./reports --archive ./reports   # writes triage-YYYYMMDD.md, never overwrites within the same day
   ```

## Open-source tools and ecosystem

Some roles can be paired with local command-line tools to obtain first-hand evidence, mostly one tool per role, with a note on whether data leaves your machine. See [Optional open-source tools](docs/ecosystem.md): Gitleaks, Semgrep, Playwright, axe-core, Lighthouse, Vale, ScanCode Toolkit.

## Playbooks

Combine roles by scenario; see `playbooks/`:

| Playbook | Scenario |
| --- | --- |
| [Pre-release quality week](playbooks/pre-release.md) | The full quality check before a version is released |
| [New feature launch](playbooks/feature-launch.md) | Before a new feature or flow is opened to users |
| [Monthly growth review](playbooks/monthly-growth.md) | Early each month, review the funnel, retention, content and channels |
| [Quarterly business review](playbooks/quarterly-business.md) | Each quarter, decide whether to continue, adjust or stop |
| [Customer blocked in onboarding](playbooks/onboarding-blocked.md) | A customer is stuck at some step of onboarding |
| [Incident review](playbooks/incident-review.md) | After a P0 issue or a rollback |
| [Mini program review submission](playbooks/miniprogram-review.md) | First submission of a mini program, a version with a new category or a paid entry point, or resubmission after rejection |

## Safety boundaries

The boundaries shared by all roles live in `roles/_shared.md` and are appended to the end of every role at build time:

- Read-only first; use only the test accounts and test tenants named in the project profile.
- No submitting for review, publishing, sending messages, payments, price changes, deleting data, or changing real customer configuration.
- Production data is used only in aggregate, and personal information is never output; examples always use fictional data.
- Every conclusion carries evidence; judgments from simulated users count only as hypotheses to be validated.
- Stop and hand back at any step that needs a person to scan a QR code, log in or approve.

## Layout

```
roles/<department>/<role>.md   role card source files (the single source of the text)
roles/_shared.md               boundaries shared by all roles
playbooks/                     run playbooks
templates/report.md            role report template (P0 to P3 severity)
templates/run-plan.md          plan template for one run
project-profile.template.md    project profile template
docs/ecosystem.md              optional open-source tools
scripts/build.py               generates dist/
scripts/runner.py              automation, orchestration and dispatch helper
scripts/check.py               validates role cards, playbooks, banned words and links
tests/test_build.py            tests for the build and validation
```

## Role card format

The header is plain `key: value`, with no YAML library needed: `name` (lowercase, hyphenated, unique across the repo), `title`, `dept`, `description` (say clearly when to dispatch it), `tools`, `model`, `cadence`, `inputs`, `outputs`, `handoff`. The body has eight fixed sections: mission, when to dispatch, what to read first, work steps, must-check list, what it does not do, deliverables, and who to hand off to. Each card is 60 to 150 lines.

## Development

Python standard library only; nothing to install:

```
python3 scripts/check.py
python3 -m unittest discover -s tests
python3 scripts/build.py
```

## Inspirations

- [gstack](https://github.com/garrytan/gstack): turns the roles of a software team into callable skills, each with a fixed process and output.
- [contains-studio/agents](https://github.com/contains-studio/agents): a collection of subagents organized by department, and the "when to dispatch it" style of description.
- [Midscene.js](https://github.com/web-infra-dev/midscene): the idea of driving and verifying a UI in natural language, used here for walkthroughs on the real interface.
- [UXAgent](https://arxiv.org/abs/2504.09407): the method of usability testing with simulated users, and its limit that it can only produce hypotheses to be validated.

## License

MIT; see `LICENSE`.
