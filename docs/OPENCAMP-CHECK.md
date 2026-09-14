# OpenCamp 秋冬季页面核对（2026-09-14）

只读检查学生侧公开页面及该页面使用的排行榜查询接口，没有访问或修改管理后台。

| 阶段 | 页面 | 公开页面 courseId | 当前排行榜核对 |
| --- | --- | ---: | --- |
| Rust 进阶 & OS 入门 | [stage/4](https://opencamp.cn/os2edu/camp/2026fall/stage/4) | 2074 | Alayfolk64，0 分 |
| rCore-Tutorial | [stage/5](https://opencamp.cn/os2edu/camp/2026fall/stage/5) | 2073 | Alayfolk64，0 分；已有记录，非本轮章节上传 |
| 组件化操作系统 | [stage/6](https://opencamp.cn/os2edu/camp/2026fall/stage/6) | 2078 | Alayfolk64，0 分 |

课程 2074 与 2078 的榜单结果，与真实 CI 测得并上传的 0 分一致。模板实验未完成；该检查不代表满分评分场景已经验证。2078 榜单更新时间为 2026-09-13 19:01:01 UTC，与上传成功运行时间相符。

Chrome 已打开秋冬季课程页面，但自动化连接随后只返回导航浮层、无法读取完整表格。补充读取了相同公开页面的服务端 HTML，确认三个课程编号；再按页面公开前端的调用方式，只读查询 `/api/courseRank/getListPager`，核对上述账号与分数。没有读取浏览器 Cookie 或登录凭证。

## 网站仍保留的旧入口

- 基础阶段：`https://classroom.github.com/a/EfPsBczk`
- rCore：`https://classroom.github.com/a/BB_-JTzv`
- 组件化操作系统：`https://classroom.github.com/a/EicsWSAg`

三个阶段仍引用往期 Classroom 入口，CNB 链接也仍使用 2026S。新的 GitHub 领取入口启用后，可把旧 Classroom 链接替换为下面这段学员说明；本次未修改网站。

> 作业仓库领取：<https://github.com/2026f-autotest/enroll/issues/new?template=enroll.yml>
>
> 登录 GitHub，选择本阶段课程并提交申请；机器人会回复作业仓库和邀请链接。接受邀请后按仓库 README 完成实验并 push，CI 自动评测并同步 OpenCamp。请在 OpenCamp 加入课程并绑定同一个 GitHub 账号。

本地证据：`tmp/opencamp-stage4.html`、`tmp/opencamp-stage5.html`、`tmp/opencamp-stage6.html`，以及 `tmp/opencamp-rank-2074.json`、`tmp/opencamp-rank-2073.json`、`tmp/opencamp-rank-2078.json`。榜单记录仅保留本次核对所需的公开字段。
