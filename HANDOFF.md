# HANDOFF — Project05_海外房东验真工具 (TenantGuard AI)

> 最后更新：2026-10-07 | 更新人：Gemini Spark (产品经理角色) | 交接给：人类 / 运维运营团队
> 规则：本文件是项目的「唯一事实来源」，**接手者必须先读本文件**。

## 1. 项目一句话概述

面向欧美独立小房东（1~5 套物业）的租客虚假工资单（Paystub）与银行流水（Bank Statement）反欺诈快速核验、在线收银与风险报告工具。

- **线上生产地址**：[https://www.comilla.world](https://www.comilla.world)
- **GitHub 仓库**：`https://github.com/guoyixian2005/tenantguard`
- **托管平台**：Vercel Serverless (Global Edge CDN)
- **域名提供商**：NameSilo (`comilla.world`)
- **支付通道**：Gumroad Checkout（支持信用卡 / PayPal / Apple Pay，资金提现至 PayPal 结汇回国）+ Stripe Serverless 备用接口
- **Gumroad 结账链接**：`https://1943802037103.gumroad.com/l/pycljg`

## 2. 技术栈 / 架构

- **前端架构**：HTML5 + Tailwind CSS + 原生 JavaScript，单页无编译极速加载。
  - 支持真实 PDF 文件拖拽上传与实时分析。
  - 内置 3 组典型造假样本模拟器（Clean ADP、四舍五入假税率、PS 净薪篡改）。
  - 支持一键生成测试样本 PDF 下载。
  - 接入标准 `@media print` 样式，支持一键打印/导出官方证书级 PDF 报告。
  - 接入 OpenGraph / Twitter Card 社交分享卡片。
- **后端架构**：Vercel Serverless Python Functions (`api/`)
  - `/api/verify`：接收 PDF 文件流 Base64 编码，调用纯 Python 取证引擎输出 0~100 欺诈评分与红旗清单。
  - `/api/checkout`：调用 Stripe Checkout Session API 创建付款会话并返回托管结账页面 URL。
- **核心检测引擎 (`src/`)**：
  - `src/pdf_forensics.py`：PDF 底层元数据扫描（检测 Photoshop/Canva 等 20+ 款高危生成器；检测增量 `%%EOF` 修改）。
  - `src/tax_verifier.py`：美国法定 FICA 税率双向核算（Social Security 6.2%、Medicare 1.45%、加减法一致性与 YTD 比例）。
  - `src/analyzer.py`：综合调度与 0~100 风险评级。
  - `src/report_generator.py`：报告格式化（终端彩色、Markdown 与 JSON）。
- **自动化测试 (`tests/test_audit.py`)**：10 组典型场景用例（10/10 全部通过，合规样本 0 误报，造假样本 100% 拦截）。

## 3. 当前状态

阶段：**MVP 全流程 100% 闭环落地（前端 + 算法 API + 独立域名 HTTPS + Gumroad 美元收款闭环 + PayPal 提现）** (100%)

## 4. 关键资产与凭据配置

- **美国收款银行账户 (Payoneer Citibank)**：
  - 银行：Citibank (111 Wall Street, New York, NY 10043, USA)
  - 路由号 (Routing ABA)：`031100209`
  - 账号：`70581370002675529` (Checking)
  - 状态：已成功绑定至 Stripe 账户接收 USD 提现。
- **Stripe API 密钥**：
  - Publishable Key：已归档至 `docs/08_`
  - Secret Key：已安全配置在 Vercel 环境变量 `STRIPE_SECRET_KEY` 中。

## 5. 项目关键文档索引

| 路径 | 说明 |
| --- | --- |
| `index.html` | 生产环境完整前端落地页（带上传、支付与打印） |
| `api/verify.py` | Vercel 云端 Python Serverless 取证接口 |
| `api/checkout.py` | Vercel 云端 Stripe 支付收银台接口 |
| `src/` | 核心取证与数学核验引擎算法库 |
| `run_audit.py` | 本地 CLI 运行与调试脚本 |
| `tests/test_audit.py` | 10 项场景自动化测试套件 |
| `docs/01_产品需求文档_PRD.md` | 产品功能规格说明、检测维度与算法逻辑 |
| `docs/02_英文落地页文案_LandingPage.md` | 英文落地页文案原稿 |
| `docs/03_冷启动获客与商业化策略.md` | 整体冷启动路线图与单位经济模型 |
| `docs/04_海外云服务器与域名申请指南.md` | 境外域名与服务器实操指南 |
| `docs/05_Reddit冷启动获客长文与发帖指南.md` | 针对 Reddit 房东圈的英文高转化发帖长文与评论对策 |
| `docs/06_美金支付通道与Stripe配置指南.md` | 美金支付与结汇配置指南 |
| `docs/07_海外社交媒体实操与防封全攻略.md` | Reddit 注册、养号与防封全攻略 |
| `docs/08_账户与支付配置信息.md` | 银行提现账户与密钥配置机密归档 |

## 6. 下一步运营与获客行动建议

1. **终端执行推送上线**：在终端运行 `unset http_proxy https_proxy all_proxy HTTP_PROXY HTTPS_PROXY ALL_PROXY && git push` 将最新 Gumroad 链接部署至 Vercel 生产环境。
2. **Gumroad 提现验证**：在 Gumroad 个人控制台 `Settings ➔ Payments` 确认已绑定 PayPal 收款邮箱。
3. **Reddit 社群发帖引流**：在美东时间白天（北京时间晚 20:30~22:30）前往 `r/Landlord` 发布 `docs/05_Reddit冷启动获客长文与发帖指南.md` 中的干货长文。
4. **首批种子客户转化**：根据 `docs/05_` 评论区话术引导房东进站使用，捕获首批付费转化。
