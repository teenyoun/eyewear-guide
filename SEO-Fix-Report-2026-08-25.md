# EyewearGuide SEO 收录优化报告（2026-08-25）

## 诊断结论：为什么谷歌迟迟不收录

GSC 网址检查显示页面状态为"已抓取 - 尚未编入索引"，且"无引荐来源网页"。全站扫描发现 4 个硬伤：

| # | 问题 | 严重度 | 影响 |
|---|------|--------|------|
| 1 | robots.txt 的 Sitemap 仍指向旧域名 `teenyoun.github.io` | 高 | Google 找不到新站 sitemap |
| 2 | canonical 新旧域名分裂（部分指旧域名，12 篇完全缺失） | 高 | 被判定为重复内容，权重不集中 |
| 3 | 12 篇文章无 Related Guides 内链模块 | 中 | 页面孤立，权重无法传递 |
| 4 | 全站 0 篇有 JSON-LD 结构化数据 | 中 | 缺少 Article 信号，无法进富媒体结果 |

另外：新域名 `glasses.teenyoun.com` 绑定时 Google 已收录旧域名内容，域名切换后 canonical 未同步，导致 Google 困惑哪个是权威版本。

## 已执行的修复（2026-08-25，已推送部署）

1. **canonical 全站统一** → `https://glasses.teenyoun.com/...`（46 篇全部修复，其中 24 篇修正/补齐）
2. **og:url 旧域名引用清零**（12 篇）
3. **JSON-LD Article schema 全站注入**（46 篇，含 headline/description/datePublished/author/publisher）
4. **Related Guides 内链补齐**（34 → 46 篇全覆盖）
5. **robots.txt** → `Sitemap: https://glasses.teenyoun.com/sitemap.xml`
6. **sitemap.xml 重建**（47 条 URL，全为新域名）
7. **generate.py 生成器升级**：未来新文章自动带 robots meta + canonical + og 标签 + JSON-LD + 搜索链接 CTA（不再用失效的 ASIN 深链和 `href="#"` 占位）

## 需要用户操作（GSC 内 2 分钟）

1. 打开 Google Search Console → 网址检查 → 输入任意文章 URL
2. 对重点页面（尤其是显示"已抓取-未收录"的）点 **"请求编入索引"**（每天限额约 10-15 个 URL，分 2-3 天提交完 46 篇，优先高 priority 页面：0.9 分的那批约 15 篇）
3. 确认 sitemap 状态：GSC → 站点地图 → 确认 `https://glasses.teenyoun.com/sitemap.xml` 状态为"成功"（如显示错误，删除重新提交一次）

## 预期与说明

- **收录时间**：新站/新域名冷启动，Google 通常需要 4-8 周建立信任。本次修复消除了信号分裂，预计 2-4 周内"已抓取-未收录"的页面会陆续转正。
- **亚马逊零点击的原因**：不是链接问题，是流量问题 —— 没有索引就没有 Google 流量，点击自然为 0。Amazon Associates 报告本身还延迟 24 小时。索引转正 + Pinterest/Quora 持续引流后，点击才会出现。
- **短期补充引流**（不依赖 Google）：Bing Webmaster Tools 收录快（也喂 ChatGPT/Edge 搜索）；Quora 回答已持续发布带链接。

## 后续维护

- 每日 cron 继续跑，新文章自动继承全部 SEO 要素
- 每 1-2 周复查 GSC 收录曲线；如某篇收录特别慢，单独"请求编入索引"
- 流量起来后，可将搜索链接逐步替换为高转化 ASIN 链接（注意先验证 ASIN 有效性）
