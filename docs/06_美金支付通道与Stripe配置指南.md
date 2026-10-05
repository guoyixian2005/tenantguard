# TenantGuard AI — 美金支付通道与极简收款配置指南

> **目标**：为 `comilla.world` 接入真实美金收款能力，让海外小房东点击 `$9.99` 或 `$19.99` 能直接刷信用卡付款。

---

## 一、 海外独立开发者的两大收款路径

| 方案 | 推荐指数 | 注册门槛 | 提现方式 | 适用阶段 |
| :--- | :--- | :--- | :--- | :--- |
| **方案 A：Lemon Squeezy / Creem (MoR 模式)** | ★★★★★（首选推荐） | **极低**（支持中国大陆个人护照/身份证直接注册） | 提现到 PayPal、Wise 或国内银行卡 | MVP 首期验证、零海外公司首选 |
| **方案 B：Stripe Payment Links** | ★★★★☆ | 需要拥有境外主体（如香港个人银行卡/公司，或美国 Stripe Atlas） | 直接结算到外币账户 | 项目规模化阶段 |

---

## 二、 方案 A：使用 Lemon Squeezy 零代码 5 分钟接入（最推荐）

Lemon Squeezy 是目前全球独立开发者出海最常用的“商家记录服务商”（Merchant of Record）：
- **核心优势**：自动替你处理欧美各国繁琐的数字消费税（VAT/Sales Tax），支持个人直接注册，提供现成的托管结账页（Hosted Checkout）。

### 1. 注册与创建产品
1. 访问官网：`lemonsqueezy.com`，点击注册个人账号；
2. 填写店铺信息（Store Name 填 `TenantGuard AI`，网址填 `https://comilla.world`）；
3. 按照提示完成基础身份验证（上传身份证或护照）；
4. 进入后台 **Products** 页面，创建两个产品：
   - **Product 1**：`Single Verification Scan` ➔ 定价 `$9.99`（一次性付款）
   - **Product 2**：`Applicant 3-Pack` ➔ 定价 `$19.99`（一次性付款）

### 2. 复制支付链接并绑定到网页
创建完成后，点击每个产品右侧的 **Share**，复制你的专属结账链接（如 `https://tenantguard.lemonsqueezy.com/buy/xxxx-xxxx`）。

只需把网页源码 `index.html` 对应按钮里的链接替换为你的支付链接：
```html
<!-- 单次购买按钮 -->
<a href="你的LemonSqueezy单次付款链接" target="_blank" class="...">
  Verify 1 Document ($9.99)
</a>

<!-- 3份特惠包购买按钮 -->
<a href="你的LemonSqueezy特惠包付款链接" target="_blank" class="...">
  Get 3-Pack & Save $10 ($19.99)
</a>
```

用户点击后会直接跳转到类似 Apple 风格的极简信用卡付款页，支持 Visa、Mastercard、Apple Pay 和 Google Pay！

---

## 三、 方案 B：如果已有 Stripe 账号（Stripe Payment Links）

如果你已经拥有香港或海外的 Stripe 账户：
1. 登录 Stripe 控制台 ➔ 点击顶部搜索栏搜索 **Payment Links（支付链接）**；
2. 点击 **+ New**，创建商品：
   - 名称：`TenantGuard - Single Scan`
   - 金额：`9.99 USD`
3. 点击 **Create link**，直接复制链接 `https://buy.stripe.com/xxxxxx`；
4. 将该链接粘贴到 `index.html` 中的购买按钮即可。
