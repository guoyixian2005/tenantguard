# TenantGuard AI — 海外社群冷启动发帖长文与获客指南

> **目标平台**：Reddit (`r/Landlord`, `r/realestateinvesting`, `r/PropertyManagement`)、BiggerPockets 论坛、Facebook 房东社群  
> **核心策略**：**Value-First（价值先行，拒绝硬广）**。以专业数据和真实防骗案例拆解切入，建立绝对信任后再顺带引流到 `comilla.world`。

---

## 一、 Reddit 发帖规则与防封指南

1. **绝对禁忌**：千万不要写成广告推销帖（如：“Check out my new SaaS!”），会被管理员瞬间删帖封号；
2. **正确姿态**：以**独立房东（DIY Landlord）+ 取证研究者**的双重身份发帖，提供 95% 的深度防坑干货，把产品当作文末顺带提及的“免费自制辅助工具”；
3. **最佳发帖时间**：美东时间（EST）周二至周四上午 8:30 ~ 10:30，或晚上 7:30 ~ 9:00（海外房东集中刷论坛的高峰期）。

---

## 二、 完整发帖文案（中英双语对照，直接复制英文部分）

### 帖子标题 (Post Title)
> **I audited 50 fake paystubs submitted to independent landlords this year. Here are the 4 dead giveaways scammers almost always forget to hide.**

---

### 正文内容 (Post Body)

```markdown
Hey everyone,

Over the past six months, I’ve been running deep forensic audits on suspected fake paystubs and altered bank statements submitted to mom-and-pop landlords. With eviction moratorium memories still fresh and average legal eviction costs hovering around $15,000–$25,000, tenant application fraud is at an all-time high.

Between $5 online fake stub generators (ThePayStubs, PaystubMaker) and basic Adobe Acrobat PDF edits, about 1 in 5 bad tenants are now doctoring their income numbers.

Traditional screening reports (TransUnion, SmartMove) only pull past bureau debts—they completely ignore whether the uploaded income PDF was generated yesterday. 

After dissecting 50+ confirmed fake documents, here are the 4 biggest red flags you should look for before handing over the keys:

---

### 1. The FICA Social Security Math Trap (Statutory 6.2%)
Online fake stub generators are notoriously bad at math. 
Under US federal law, Social Security tax is strictly **6.2%** of gross earnings (up to the annual cap). 
- **The giveaway**: Scammers love round numbers. If gross pay is $4,500, Social Security MUST be exactly **$279.00**. Fake stubs frequently round it to $150.00, $200.00, or use outdated percentage charts.
- **Tip**: Grab a calculator and multiply Gross Pay by 0.062. If it’s off by more than 10 cents, you are almost certainly looking at an altered or counterfeit document.

### 2. The Medicare Math Discrepancy (Statutory 1.45%)
Just like Social Security, statutory Medicare deduction is strictly **1.45%** of all gross wages. 
- Real commercial payroll software (ADP, Workday, Paychex, Gusto) never makes arithmetic mistakes on Medicare. 
- If someone claims $6,000 gross monthly pay, Medicare deduction must equal **$87.00**. We routinely catch documents where Medicare is listed as $40 or $50 because the template creator didn't know the exact federal percentage.

### 3. Basic Arithmetic Failure: Gross - Deductions ≠ Net Pay
This sounds obvious, but it catches manual Photoshop fraudsters every single time:
- Applicants often use a PDF editor to change "Net Pay" from $3,000 to $5,000 to meet your 3x rent rule.
- But they forget to adjust the Total Deductions column. 
- **The test**: Add up Gross Pay, subtract Total Deductions, and verify if it matches Net Pay to the penny. In over 30% of modified PDFs, the arithmetic literally does not balance.

### 4. Digital PDF Metadata Footprints
Enterprise payroll platforms generate PDFs using proprietary automated backend engines. Counterfeiters generate them using consumer design tools.
If you open the PDF properties (File > Properties in Acrobat or Inspector on Mac):
- If the **Producer** or **Creator** says *Canva*, *Adobe Photoshop*, *iLovePDF*, *Sejda*, or *PDFescape*, reject it immediately. No legitimate employer processes payroll through Canva.
- Also, look at the **Modified Date**. If the paystub is dated March 15th but the PDF Modified Date is October 4th at 11:42 PM, someone altered the file right before applying.

---

### Free Tool I Built for Fellow Landlords:
Because manually doing these calculations on multiple applicants gets tedious, I built a lightweight automated verification tool: **[TenantGuard.ai](https://comilla.world)**.

It automatically inspects PDF metadata, recalculates FICA tax down to the penny, and flags arithmetic inconsistencies in 60 seconds.

Feel free to run a free sample scan at **https://comilla.world** to test it out. If you have an applicant document right now that looks suspicious, feel free to redact personal info and comment below—happy to help audit it for you!

Stay safe out there!
```

---

## 三、 评论区互动话术库 (Comment Handling Playbook)

| 场景 | 评论类型 | 推荐回复话术 (Copy-Paste) |
| :--- | :--- | :--- |
| **质疑合规性** | *"Does this violate FCRA?"* | *"Great question! TenantGuard is an automated document integrity and arithmetic verifier, not a credit bureau. It simply checks the mathematical accuracy of files the tenant voluntarily provides to you, similar to checking math on an application."* |
| **求助检测** | *"I have a stub that looks fishy, can you check?"* | *"Sure! Send me a DM with the sensitive names/SSN blacked out, or you can drag the PDF directly into comilla.world to get the automated breakdown instantly."* |
| **同行点赞** | *"This is great info, saved my skin."* | *"Glad it helped! The 6.2% FICA check alone has caught so many scammers for us. Always calculate it before signing!"* |
