# 领取入口维护

## 一次性配置

1. 保持 `2026f-autotest/enroll` 为公开仓库，启用 Issues 和 Actions。仅维护者有写权限。
2. 在本仓库的 [Actions Secrets](https://github.com/2026f-autotest/enroll/settings/secrets/actions) 保存 `ENROLL_GITHUB_TOKEN`。它是有权在 `2026f-autotest` 创建仓库、设置 Actions 变量、分配协作者、触发配置检查及读取组织 Secret 元数据的维护者凭证。不要把它设成组织共享 Secret。
3. 确认三个课程模板已启用 Template repository，课程组织 Secret 的访问范围均为 Public repositories。
4. 用维护者自己的 GitHub 账号提交一份领取申请，确认 Actions 成功、机器人回复链接、`STUDENT_GITHUB` 正确以及学员配置检查成功，再发布领取入口。

默认 `GITHUB_TOKEN` 仅处理本仓库 Issue 回复和关闭；跨仓库操作使用 `ENROLL_GITHUB_TOKEN`。课程上传 Token 不会经过申请表或建仓脚本。

当前应急版使用维护者凭证，后续可以迁移到组织 GitHub App；当前并未实现 App 认证。维护者凭证失效时，在同一个仓库 Secret 更新后重试申请即可。

## 日常流程

`.github/ISSUE_TEMPLATE/enroll.yml` 是申请表，`.github/workflows/enroll.yml` 接收新 Issue 事件，`enroll.py` 读取申请人的 `issue.user.login` 并从 `courses.json` 选择固定模板。Issue 文本不会拼接进 shell，也不能指定其他人的 GitHub 账号。

脚本复制全部模板分支，设置 `STUDENT_GITHUB`，授予该学员单个仓库写权限，触发 `check-config.yml`，最后回复仓库和邀请链接。学员提交代码后，由其作业仓库自己的 CI 评分及上传 OpenCamp。

没有名单收集、重复领取统计、报名名单查询或后台接入。重复申请沿用同名、同模板、同学员仓库，保留已有代码；不增加额外仓库。异常同名仓库不会被覆盖。

## 处理失败申请

在本仓库 Actions 选择“领取作业仓库”，点击 Run workflow，输入原 Issue 编号。重试仍读取原申请人的账号，不使用执行重试的助教账号。不要让学员修改课程 Token。

入口首次启用时，历史 Issue 不会自动补跑；维护者通过以上重试功能补跑即可。课程配置错误或账号未在 OpenCamp 绑定时，分别检查配置工作流和成绩上传作业。

## 暂停入口

在 Actions 中停用“领取作业仓库”工作流，即可停止新申请的自动建仓；已有学员仓库的评测照常运行。

## 官方机制

- [新建 Issue 触发 Actions](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#issues)
- [默认 GITHUB_TOKEN 的仓库权限边界](https://docs.github.com/en/actions/concepts/security/github_token)
- [从模板创建仓库 API](https://docs.github.com/en/rest/repos/repos#create-a-repository-using-a-template)
