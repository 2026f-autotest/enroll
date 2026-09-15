# 领取入口维护

## 一次性配置

1. 保持 `2026f-autotest/enroll` 为公开仓库，启用 Issues 和 Actions。仅维护者有写权限。
2. 在本仓库的 [Actions Secrets](https://github.com/2026f-autotest/enroll/settings/secrets/actions) 保存 `ENROLL_GITHUB_TOKEN`。它是有权在 `2026f-autotest` 创建仓库、设置 Actions 变量、分配协作者、触发配置检查及读取组织 Secret 元数据的维护者凭证。不要把它设成组织共享 Secret。
3. 确认四个课程模板已启用 Template repository，课程组织 Secret 的访问范围均为 Public repositories。
4. 用维护者自己的 GitHub 账号提交一份领取申请，确认 Actions 成功、机器人回复链接、`STUDENT_GITHUB` 正确以及学员配置检查成功，再发布领取入口。

默认 `GITHUB_TOKEN` 仅处理本仓库 Issue 回复和关闭；跨仓库操作使用 `ENROLL_GITHUB_TOKEN`。课程上传 Token 不会经过申请表或建仓脚本。

当前应急版使用维护者凭证，后续可以迁移到组织 GitHub App；当前并未实现 App 认证。维护者凭证失效时，在同一个仓库 Secret 更新后重试申请即可。

## 日常流程

`.github/ISSUE_TEMPLATE/enroll.yml` 是申请表，`.github/workflows/enroll.yml` 接收新 Issue 事件，`enroll.py` 读取申请人的 `issue.user.login` 并从 `courses.json` 选择固定模板。Issue 文本不会拼接进 shell，也不能指定其他人的 GitHub 账号。仓库配置由公共模块 `provision.py` 执行；四个课程的备用 CLI 使用该模块的相同副本。

新申请按以下顺序执行：

1. 检查申请人、公开模板、必需章节分支和组织 Secret 的共享范围。
2. 复制全部模板分支到 `preparing-课程模板名-GitHub登录名`，设置 `STUDENT_GITHUB`。
3. 触发 `check-config.yml`，读取 GitHub 返回的本次运行 ID，等待该运行和 `configuration` 作业都成功。
4. 启用评测并分配学员写权限。
5. **最后一次仓库配置写入是改成正式名称** `课程模板名-GitHub登录名`；用仓库 ID 核对改名结果。
6. 回复正式仓库和邀请链接，关闭申请。

GitHub 必须先有仓库才能绑定变量和运行 CI，因此“正式仓库最后出现”通过临时名称实现。准备失败时保留 `preparing-` 仓库供重试，不发布正式名称；准备阶段的评测和上传均跳过。邀请在最终改名前生成，学员使用机器人回复的正式邀请链接。已有正式仓库按原身份重新检查，不回退名称或覆盖代码。

配置检查仅确认身份映射及课程 Secret 已注入，不检查 OpenCamp 报名，也不上传成绩。学员提交代码后，由其作业仓库自己的 CI 评分及上传 OpenCamp。

没有名单收集、重复领取统计、报名名单查询或后台接入。重复申请沿用同名、同模板、同学员仓库，保留已有代码；不增加额外仓库。异常同名仓库不会被覆盖。

## 重试与排队

- 网络超时、连接中断及 HTTP 408/500/502/503/504：最多请求 4 次，普通退避为 2、4、8 秒。每次请求最多 30 秒，单个 API 操作预算为 180 秒。
- 429 或明确的限流 403：遵守 `Retry-After` 和 `X-RateLimit-Reset`；没有有效提示时至少等待 60 秒。要求等待的时间超过剩余预算就明确失败，不提前重试。
- 普通 401/403/404、参数错误不盲目重试。创建仓库、写身份变量、最终改名遇到响应丢失，会按固定名称及仓库 ID/身份核对，避免误覆盖。评论响应丢失不盲目重复发送。
- 配置 CI 最多等 10 分钟；入口作业最多 20 分钟。只有本次配置作业实际成功才能交付，失败、跳过和超时均不当成成功。
- 领取工作流串行处理，使用 GitHub `queue: max`，最多等待 100 个运行。超出队列容量、平台中断或作业超时时，Issue 仍保留，可由维护者手动重试。

## 处理失败申请

在本仓库 Actions 选择“领取作业仓库”，点击 Run workflow，输入原 Issue 编号。重试仍读取原申请人的账号，不使用执行重试的助教账号。不要让学员修改课程 Token。

入口首次启用时，历史 Issue 不会自动补跑；维护者通过以上重试功能补跑即可。课程配置错误或账号未在 OpenCamp 绑定时，分别检查配置工作流和成绩上传作业。

## 暂停入口

在 Actions 中停用“领取作业仓库”工作流，即可停止新申请的自动建仓；已有学员仓库的评测照常运行。

## 官方机制

- [新建 Issue 触发 Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#issues)
- [默认 GITHUB_TOKEN 的仓库权限边界](https://docs.github.com/en/actions/concepts/security/github_token)
- [从模板创建仓库 API](https://docs.github.com/en/rest/repos/repos#create-a-repository-using-a-template)

- [GitHub API 重试和限流建议](https://docs.github.com/en/rest/using-the-rest-api/best-practices-for-using-the-rest-api)
- [配置检查的精确运行 ID](https://github.blog/changelog/2026-02-19-workflow-dispatch-api-now-returns-run-ids/)
- [Actions 串行队列与容量](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)

## 课程页面入口

将[简明使用流程](COURSE_USAGE.md)放到课程页面，使用其中对应课程的领取链接。`rustlings.yml`、`base.yml`、`rcore.yml`、`arceos.yml` 已预选对应课程，学员直接提交申请。

## 修改申请标题和机器人回复

- 新申请的默认标题：编辑 `.github/ISSUE_TEMPLATE/rustlings.yml`、`base.yml`、`rcore.yml` 或 `arceos.yml` 的 `title`，格式为 `[课程名称]作业仓库`。
- 领取表单：同一文件中的 `name` 是入口名称，`body` 中的 `options` 是课程选项。课程名称与 `courses.json` 的 `title` 保持一致；通用表单同步修改 `enroll.yml`。
- 以后自动发送的回复：编辑根目录 `enroll.py` 中 `process_application()` 的 `body` 文案，保留仓库、邀请、Actions 和配置检查链接。
- 已经发送的回复：使用维护者账号打开 Issue，点击对应评论右上角 `… → Edit`，修改后点击 `Update comment`。已有 Issue 标题在页面标题旁点击 `Edit` 修改。

修改文件后提交到 `main` 即可生效。已有评论需要单独编辑。

[代码审查与修复记录](AUDIT.md)记录维护者需要了解的验证结果和后续事项。
