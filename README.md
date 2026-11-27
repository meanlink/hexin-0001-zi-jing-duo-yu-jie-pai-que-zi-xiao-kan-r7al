# 字径 · 多语街牌缺字校勘

松桥街牌社有 7 人，为老街改造项目交付商铺导向牌和公共路引。店家用消息发中文、韩文抄件，制稿员翻字体样册，审校员再对排版软件的导出来回核对。小字漏形、公共字体错用于商铺、导出助手重选字体都会引发返工。字径接手「抄件登记 → 字库匹配 → 确认切割字体」这一段，下游制版员读取锁稿 CSV 转曲下料。

| 演示角色 | 账号 | 工作台动作 |
|---|---|---|
| 查阅 | viewer@demo.test | 查阅稿台、样册、指派和已锁稿清单 |
| 制稿 | operator@demo.test | 登记和改稿，登记字库覆盖，跑检索并指派 |
| 审校 | admin@demo.test | 拥有制稿权限，检查商用许可和字体覆盖后锁稿 |

演示密码为 `Demo2026!`。这些账号用于本地演示。

## 一天的工作

1. 08:45，制稿员从商铺导向交接表取松桥东巷的 SQ-102，原文是 `东巷 안내`，用途为商用。
2. 09:00，在样册确认 `songqiao-ming.otf`、`ting-hangul.otf` 和仅限公共用途的 `study-hangul.ttf`。
3. 09:12，在逐字审校页运行样张检索；Worker 针对 4 个可见字符检索排序并储存候选。
4. 09:20，按覆盖给东、巷指派松桥明体，给 안 指派学馆朝文并观察许可提示。
5. 09:30，审校员尝试锁稿，看到 안 的许可问题和 내 的覆盖缺口。
6. 09:36，为 안、내 改用汀声常用字。审校员再次签发，锁定 SQ-102 的 R1。
7. 09:45，从交付页导出 `SQ-102-r1.csv`，制版员有两份字体文件和对应字符。

## 启动与本地调试

```bash
cp .env.example .env
docker compose up -d --build --wait
docker compose exec -T backend python -m scripts.seed_demo
```

- 前端 [http://127.0.0.1:18340](http://127.0.0.1:18340)。
- API [http://127.0.0.1:19340/docs](http://127.0.0.1:19340/docs)。
- PostgreSQL 端口为 17840，数据库和用户见 Compose。
- 更新后端代码可运行 `docker compose up -d --build backend worker`。更新前端可运行 `docker compose up -d --build frontend`。
- `docker compose logs -f backend worker` 显示 API 与检索日志。`docker compose down` 停止服务并保留数据。

| 层 | 组件 | 说明 |
|---|---|---|
| 页面 | Nginx、HTML/CSS/JS ES Modules | 静态业务页面，`/api/` 反向代理 |
| API | Python 3.11、FastAPI、JWT | 角色隔离、审计、草稿并发防护 |
| 数据 | PostgreSQL 16 | 稿件、字库包、实际指派及每个版本的检索候选 |
| 任务 | Redis 7、Python Worker | 检索排队、结果与健康心跳 |

`backend/glyph` 是字库、稿件、检索和锁稿模块，`backend/migrations` 是领域表。四个工作页面和交互在 `frontend/glyph`。Compose 的 DB、Redis 和共享产物各有命名卷。首次引导由 `SEED_DEMO=true` 触发，手动 seed 通过自然键补齐实例。

| 环境变量 | 用途 |
|---|---|
| `FRONTEND_PORT`、`BACKEND_PORT`、`DB_PORT` | 三个宿主机端口 |
| `COMPOSE_PROJECT_NAME` | Compose 服务名前缀 |
| `DB_PASSWORD`、`JWT_SECRET` | 数据库密码、令牌签名 |
| `DEMO_PASSWORD`、`SEED_DEMO` | 演示账号初始密码、自动 seed 开关 |

## 检索与锁稿口径

把每个字体包样张的 1～3 字符 n-gram 作为语料。训练阶段以 `1 + ln((1 + 文档数)/(1 + 文档频次))` 计算 IDF。查询用稿件中含该字的行，转为 L2 归一化 TF-IDF 向量。系统先根据覆盖表和用途许可筛选，再按余弦相似度排序，字体包编号用于同分决胜。候选是建议；实际指派由制稿员逐字维护。没有合法覆盖时列表留空，必须补包或改稿。文本按 Unicode NFC 归一化，空白由下游版面处理。固定稿件和字库目录时排序可复现。

草稿可更新文案，修订后保留仍适用的指派，移除消失字符的指派并清理旧版候选。审校锁稿需要当前版每个可见字符均有授权合规的覆盖。锁稿后固定字库与字符清单。CSV 使用 UTF-8 BOM，展示在网页上的字形采用界面字体。实际字体文件由制版方管理，样册登记的是人工核对的覆盖数据和文件名。组合符和变体选择符由 API 明确拒绝。

共享枚举 `UseKind`、`LicenseKind`、`ProofState` 在 `backend/glyph/models.py`、`backend/glyph/schemas.py`、`backend/migrations/10_glyph.sql` 与 `frontend/glyph/labels.js`。角色和任务状态位于 `backend/infra/roles.py`、`frontend/session.js`。

许可证见 [LICENSE](LICENSE)。
