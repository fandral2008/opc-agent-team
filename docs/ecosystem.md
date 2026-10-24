# 可选开源工具

本文档列出各角色在本机可以搭配的命令行工具，工具输出作为报告证据；没有合适工具的角色写“无需专门工具”。工具均为可选项，数据是否出本机以第四列为准。

涉及个人信息或健康类数据时，只用标为“本地”的工具；任何云版服务（如 PostHog、Sentry 的云端版本）须自建，或脱敏后再上报，个人信息与健康类数据不得直接上传。

## 调度层（Chief）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `chief-of-staff` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 经营与法务层（Exec）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `ceo-reviewer` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `finance-pricing` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `legal-compliance` | [ScanCode Toolkit](https://github.com/aboutcode-org/scancode-toolkit) | `scancode -l --json-pp out.json <源码目录>` 扫描依赖与源码的许可证，冲突项写入报告证据 | 本地 |
| `legal-counsel` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 风控层（Risk）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `risk-control-reviewer` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 洞察层（Insight）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `market-scout` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `cross-domain-strategist` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 产品层（Product）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `product-manager` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `user-researcher` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `data-analyst` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 设计层（Design）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `ux-writer` | [Vale](https://github.com/errata-ai/vale) | `vale --output=JSON <文案目录>`，用项目术语表写规则检出用词不一致 | 本地 |
| `interaction-designer` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `visual-design-reviewer` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 研发层（Engineering）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `security-reviewer` | [Gitleaks](https://github.com/gitleaks/gitleaks) / [Semgrep](https://github.com/semgrep/semgrep) | `gitleaks detect --source . --redact` 查凭证泄漏；`semgrep scan --config <仓库内规则目录> --metrics=off` 查越权、注入等代码模式，规则文件放在项目里，不从规则市场在线拉取 | 本地（Semgrep 须使用本地规则并关闭上报） |
| `architect-reviewer` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `code-reviewer` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `release-sre` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 质量层（QA）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `qa-daily-task-tester` | [Playwright](https://github.com/microsoft/playwright) | `npx playwright test` 在测试租户走通主干流程，再逐个读取端核对数据 | 本地 |
| `qa-accessibility` | [axe-core](https://github.com/dequelabs/axe-core) | `npx @axe-core/cli <页面地址>` 列出对比度与缺少标签的元素 | 本地 |
| `qa-performance` | [Lighthouse](https://github.com/GoogleChrome/lighthouse) | `npx lighthouse <页面地址> --output=json` 取首屏与资源体积，对比基线 | 本地 |
| `qa-permission-tester` | [Playwright](https://playwright.dev/docs/auth) | 按身份保存登录状态，用同一套路由和接口逐个身份回放 | 本地 |
| `qa-edge-case-breaker` | [Playwright](https://github.com/microsoft/playwright) | 用网络模拟与路由拦截制造离线、高延迟和重复请求 | 本地 |
| `qa-cross-platform` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `qa-new-user-tester` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 增长层（Growth）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `growth-hacker` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `content-marketer` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `community-ops` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `search-aso` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `channel-bd` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 客户成功层（Customer）

| 角色 | 工具 | 用法 | 数据是否出本机 |
| --- | --- | --- | --- |
| `support-desk` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `onboarding-specialist` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |
| `retention-churn` | 无需专门工具 | 按角色卡的清单人工核查 | 不涉及 |

## 使用方式

1. 先跑工具，保存原始输出。
2. 把关键命中（文件与行号、分数、违规元素）写进报告的证据栏。
3. 由角色按业务背景判定级别（P0 至 P3），已知合理设计写入项目档案的排除说明，不重复上报。
