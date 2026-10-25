[English](README.en.md) | 中文

# opc-agent-team

A set of 33 role cards for one-person companies (OPC): QA, design, engineering, growth, customer success, executive review, risk control and market insight, written as AI agent prompts. Each card runs as a Claude Code subagent or can be handed to Codex or any agent that reads Markdown. Cards are generic; everything project-specific lives in your own `project-profile.md`. Default posture is read-only, test accounts and fake data only.

# 一人公司 AI 角色团

把一人公司需要的各路岗位做成可点名运行的 AI 代理角色卡：33 个岗位，覆盖质量、设计、研发、增长、客户成功、经营评审、风控和洞察。适合小型 SaaS、微信小程序 + Web 管理后台这类产品，不绑定任何具体项目。

三条设计原则：

- 角色卡是通用的，项目差异只写进你自己的 `project-profile.md`，每个角色开工先读它。
- 每个角色只回答自己那一类问题，结论必须有证据（截图、代码位置、数据），代理的报告只算待核实线索。
- 默认只读，只用测试账号和假数据；发布、发消息、生产写入、付费、改价一律不做，只出建议和文案。

## 岗位总表

| 部门 | 角色名 | 岗位 | 什么时候派 |
| --- | --- | --- | --- |
| 调度 | `chief-of-staff` | 幕僚长 | 需要决定本次该派哪些岗位、写运行计划、汇总去重各岗位报告并分诊时使用 |
| 经营 | `ceo-reviewer` | 经营评审 | 需要对产品方向、投入取舍、继续调整或停止做出判断时使用 |
| 经营 | `finance-pricing` | 定价与单位经济 | 需要设计或调整付费档、虚拟积分定价、核算成本与毛利、设计付费验证实验时使用 |
| 经营 | `legal-counsel` | 法务 | 收费前或签约前，需要梳理协议文本、知识产权、主体与收益归属、收费与发票，并列出须执业律师确认的事项时使用 |
| 经营 | `legal-compliance` | 合规 | 涉及小程序平台审核规则与类目、隐私与个人信息、虚拟物品与诱导行为、开源许可、内容安全、对外宣传用语时使用 |
| 风控 | `risk-control-reviewer` | 风控规则审查 | 积分、奖励、邀请、促销、免费期、举报等业务规则上线或调整前，需要审查会不会被钻空子并给出限额与监控建议时使用 |
| 洞察 | `cross-domain-strategist` | 跨界策略师 | 增长遇到瓶颈或季度规划时，需要从其他行业借成熟机制并设计带判定线的小实验时使用 |
| 洞察 | `market-scout` | 竞品与爆品侦察员 | 需要定期扫描竞品、替代方案和近期爆品，只用公开信息提炼值得学与不该学的点时使用 |
| 产品 | `data-analyst` | 数据分析 | 需要看漏斗、活跃与留存口径、发现指标缺口、制定只读聚合查询规范时使用 |
| 产品 | `product-manager` | 产品经理 | 需要把需求、反馈或缺陷整理成问题定义、方案与提案，并判断是否应做成配置而不是改代码时使用 |
| 产品 | `user-researcher` | 用户研究 | 需要准备访谈提纲、归类用户反馈、做模拟用户采访并说明其局限时使用 |
| 设计 | `interaction-designer` | 交互设计 | 需要评审导航结构、返回路径、弹层、键盘操作，以及空态、错误态、未开通态的完整性时使用 |
| 设计 | `ux-writer` | 界面文案 | 需要统一界面用词、检查按钮动词与错误提示可行动性、维护术语表时使用 |
| 设计 | `visual-design-reviewer` | 视觉设计评审 | 需要评审界面层级、间距、配色、主题与皮肤组合的截图墙，并对照获奖级品质标准给出改进项时使用 |
| 研发 | `architect-reviewer` | 架构评审 | 需要评审技术方案、可配置性、数据模型与迁移风险，判断“第 N 个客户要不要改代码”时使用 |
| 研发 | `code-reviewer` | 代码评审 | 需要评审代码改动的正确性、回归风险与测试覆盖，找出会在真实使用中出错的地方时使用 |
| 研发 | `release-sre` | 发版与运维 | 需要准备发版清单、核对备份可恢复、设计回滚、检查健康与容量磁盘告警时使用 |
| 研发 | `security-reviewer` | 安全评审 | 需要评审越权、租户隔离、令牌与会话、注入、日志脱敏、依赖漏洞时使用 |
| 质量 | `qa-accessibility` | 可访问性测试 | 需要检查大字体、适老化、色弱、对比度、触控尺寸与读屏支持，确保各类用户都能用时使用 |
| 质量 | `qa-cross-platform` | 跨端一致性测试 | 需要核对小程序、Web 管理后台与用户手册三者在功能、数据、术语和步骤上是否一致时使用 |
| 质量 | `qa-daily-task-tester` | 高频任务真跑测试 | 需要在测试租户里把用户每天做的高频任务从头到尾真实走一遍，记录步数、耗时、卡点，并核对写入后各读取端是否一致时使用 |
| 质量 | `qa-edge-case-breaker` | 边界与异常破坏测试 | 需要用异常输入、跨月跨年、时区、断网弱网、切后台、重复点击、未保存返回、键盘遮挡、安卓返回键等手段主动弄坏功能时使用 |
| 质量 | `qa-new-user-tester` | 新人体验测试 | 需要以零上下文新用户身份走首次体验，覆盖不同类型的新人，并配合独立评审代理复核时使用 |
| 质量 | `qa-performance` | 性能测试 | 需要检查首屏时间、小程序包体余量、慢接口 p95、内存占用与长列表流畅度时使用 |
| 质量 | `qa-permission-tester` | 身份权限测试 | 需要按多身份与多入口的矩阵测试权限、跨租户访问、代为操作的只读限制和迟到响应时使用 |
| 增长 | `channel-bd` | 渠道合作 | 需要寻找并评估行业协会、会议、同行社群、合作伙伴等渠道，并准备合作提纲与评估表时使用 |
| 增长 | `community-ops` | 社群运营 | 需要运营用户群、维护种子用户、组织共建者计划并安排运营节奏时使用 |
| 增长 | `content-marketer` | 内容营销 | 需要为公众号、小红书、朋友圈、视频号规划选题和素材，使用真实场景而不用未授权客户案例时使用 |
| 增长 | `growth-hacker` | 增长 | 需要设计拉新回路、邀请与转发机制、激活第一步，并把增长单位定为团队时使用 |
| 增长 | `search-aso` | 搜索与商店优化 | 需要优化微信搜一搜、小程序名称与简介关键词、应用商店信息与官网搜索收录时使用 |
| 客户成功 | `onboarding-specialist` | 客户接入 | 需要设计新客户接入路径、准备模板、缩短首次成功时间，或新客户接入受阻需要诊断时使用 |
| 客户成功 | `retention-churn` | 留存与流失 | 需要设计流失预警信号、回访提纲、续费与再激活实验时使用 |
| 客户成功 | `support-desk` | 客服支持 | 需要归类工单、维护 FAQ、保持手册与界面一致，并撰写回复文案时使用 |

## 5 分钟上手

1. 复制 `project-profile.template.md` 为你项目根目录下的 `project-profile.md`，按实际情况填写产品形态、测试账号获取方式、可写范围、禁止动作、发版节奏、关键指标。密码不要写进去，只写获取方式。
2. 构建并安装角色：

   ```
   python3 scripts/build.py && cp dist/claude-code/agents/*.md ~/.claude/agents/
   ```

   想只在某个项目内使用，把目标改成该项目的 `.claude/agents/`。
3. 先点名 `chief-of-staff`，告诉它这次的场景（例如“下周三发版”），它会对照 `playbooks/` 选岗位并填写 `templates/run-plan.md`。
4. 按计划逐个点名岗位，每个岗位按 `templates/report.md` 交回报告。
5. 让 `chief-of-staff` 汇总去重，得到一页分诊单，由你决定处理顺序。

## 运行方式

Claude Code：安装后在对话里直接点名，例如“用 qa-permission-tester 按项目档案跑一遍权限矩阵”，也可以让主对话按 description 自动派发。

Codex、Antigravity 或其他代理：构建后每个角色有一份完整的 Markdown（`dist/markdown/<name>.md`，已附共用边界）。在项目的 `AGENTS.md` 里写一句：

```
需要质量检查时，按 <本仓库路径>/dist/markdown/qa-permission-tester.md 执行，先读项目根目录的 project-profile.md。
```

## 自动化辅助工具

仓库内置轻量级调度辅助工具 `scripts/runner.py`（无第三方依赖）：

1. **按编排生成计划**：
   ```bash
   python3 scripts/runner.py plan pre-release --out run-plan.md
   python3 scripts/runner.py plan pre-release --reports ./reports   # 带出上次分诊单的 P0/P1
   ```
2. **按改动文件智能推荐岗位**：
   ```bash
   python3 scripts/runner.py suggest src/auth/guard.ts src/billing/pricing.vue
   git diff --name-only | python3 scripts/runner.py suggest -
   ```
3. **多岗位报告汇总与分诊**：
   ```bash
   python3 scripts/runner.py triage ./reports --out triage-summary.md
   python3 scripts/runner.py triage ./reports --archive ./reports   # 写为 triage-YYYYMMDD.md，同日不覆盖
   ```

## 开源工具与系统生态

部分角色可以搭配本机命令行工具取得第一手证据，多数角色一个，并标明数据是否出本机，详见 [可选开源工具](docs/ecosystem.md)：Gitleaks、Semgrep、Playwright、axe-core、Lighthouse、Vale、ScanCode Toolkit。

## 编排

按场景组合岗位，见 `playbooks/`：

| 编排 | 场景 |
| --- | --- |
| [发版前质量周](playbooks/pre-release.md) | 一个版本发布前的完整质量检查 |
| [新功能上线](playbooks/feature-launch.md) | 新功能或新流程开放入口之前 |
| [月度增长复盘](playbooks/monthly-growth.md) | 每月初复盘漏斗、留存、内容与渠道 |
| [季度经营评审](playbooks/quarterly-business.md) | 每季度决定继续、调整或停止 |
| [新客户接入受阻](playbooks/onboarding-blocked.md) | 客户卡在接入的某一步 |
| [事故复盘](playbooks/incident-review.md) | P0 问题或回滚之后 |
| [小程序提审上架](playbooks/miniprogram-review.md) | 小程序首次提审、含新类目或收费入口的版本、被驳回后重提 |

## 安全边界

所有角色共用的边界在 `roles/_shared.md`，构建时附到每个角色末尾：

- 只读优先；只使用项目档案里的测试账号和测试租户。
- 不提审、不发布、不发消息、不付费、不改价、不删数据、不改真实客户配置。
- 生产数据只做聚合，不输出个人信息；示例一律使用虚构数据。
- 每条结论附证据；模拟用户得出的判断只算待验证假设。
- 遇到需要人扫码、登录或批准的步骤就停下交回。

## 目录

```
roles/<部门>/<角色>.md      角色卡源文件（唯一正文）
roles/_shared.md            全体角色共用边界
playbooks/                  运行编排
templates/report.md         岗位报告模板（P0 至 P3 分级）
templates/run-plan.md       一次运行的计划模板
project-profile.template.md 项目档案模板
docs/ecosystem.md           可选开源工具
scripts/build.py            生成 dist/
scripts/runner.py           自动化编排与派工辅助工具
scripts/check.py            校验角色卡、编排、禁词与链接
tests/test_build.py         构建与校验的测试
```

## 角色卡格式

文件头是简单的 `key: value`，不依赖 yaml 库：`name`（全仓唯一的小写连字符）、`title`、`dept`、`description`（写清什么时候该派它）、`tools`、`model`、`cadence`、`inputs`、`outputs`、`handoff`。正文固定八节：使命、什么时候派、开工先读、工作步骤、必查清单、不做的事、交付、交接给谁。每张卡 60 至 150 行。

## 开发

只用 Python 标准库，无需安装依赖：

```
python3 scripts/check.py
python3 -m unittest discover -s tests
python3 scripts/build.py
```

## 借鉴来源

- [gstack](https://github.com/garrytan/gstack)：把软件团队的岗位做成可点名的技能，每个岗位有固定的流程与产出。
- [contains-studio/agents](https://github.com/contains-studio/agents)：按部门组织的子代理集合，以及“什么时候该派它”的描述写法。
- [Midscene.js](https://github.com/web-infra-dev/midscene)：用自然语言驱动界面操作与验证的思路，用于真实界面上的走查。
- [UXAgent](https://arxiv.org/abs/2504.09407)：用模拟用户做可用性测试的方法，以及它只能产生待验证假设的局限。

## 联系与合作

想让角色团适配你的项目，或需要一对一搭建，欢迎在 X 私信：[@Fandral2008](https://x.com/Fandral2008)。

## 许可

MIT，见 `LICENSE`。
