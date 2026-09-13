# 领取入口验证记录（2026-09-14）

公开入口：[2026f-autotest/enroll](https://github.com/2026f-autotest/enroll)。

## 重试与最后发布正式名称（2026-09-14）

生产入口提交 `b49d3c3` 加入有界 API 重试、串行队列、精确等待本次配置 CI，以及先准备、最后改成正式仓库名。31 项定向测试在本地及 [GitHub 检查 34779020299](https://github.com/2026f-autotest/enroll/actions/runs/34779020299) 通过。限流、网络断开、响应丢失和超时为故障注入测试，不能当成真实 GitHub 故障恢复记录。

三门课用原申请在云端串行重试，均成功；核对了配置作业完成时间早于机器人成功回复时间，且申请已关闭：

| 申请 | 本轮领取运行 | 本次配置检查 |
| --- | --- | --- |
| [#1](https://github.com/2026f-autotest/enroll/issues/1) | [34779062268](https://github.com/2026f-autotest/enroll/actions/runs/34779062268) | [34779069699](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34779069699)，通过 |
| [#2](https://github.com/2026f-autotest/enroll/issues/2) | [34779064137](https://github.com/2026f-autotest/enroll/actions/runs/34779064137) | [34779092395](https://github.com/2026f-autotest/2026f-oscamp-base-Alayfolk64/actions/runs/34779092395)，通过 |
| [#3](https://github.com/2026f-autotest/enroll/issues/3) | [34779066307](https://github.com/2026f-autotest/enroll/actions/runs/34779066307) | [34779108198](https://github.com/2026f-autotest/2026f-arceos-Alayfolk64/actions/runs/34779108198)，通过 |

模板及已有维护者学员仓库共 6 个仓库、22 个分支完成同步；rCore 模板和学员仓库均包含 main、ch1 至 ch8。本次只修改两份工作流和维护文档，逐分支核对远端 SHA 及改动文件集合，实验源码、计分规则和已有成绩未修改。

## 全新仓库：失败保留准备状态，重试后最后发布

使用独立验证模板 `verify-preparation-20260914`，学员仍为维护者 `Alayfolk64`，直接执行同一份生产 `provision()`；该模板未加入课程领取目录。测试完成后，两份验证仓库已归档。

1. 验证模板故意引用一个不存在的 Secret。[真实配置运行 34779152195](https://github.com/2026f-autotest/verify-preparation-20260914-Alayfolk64/actions/runs/34779152195) 失败，原始错误为：

   ```text
   Missing organization course secret; contact the maintainer.
   Process completed with exit code 1.
   ```

   此时 API 确认正式仓库不存在，只有 `preparing-verify-preparation-20260914-Alayfolk64`。
2. 临时仓库已经绑定 `STUDENT_GITHUB`，手动触发[真实评测运行 34779166658](https://github.com/2026f-autotest/verify-preparation-20260914-Alayfolk64/actions/runs/34779166658)，两个作业均为 `skipped`，没有执行测试或成绩上传。
3. 仅在该验证仓库恢复正常配置工作流，再执行原生产建仓函数。[配置检查 34779220005](https://github.com/2026f-autotest/verify-preparation-20260914-Alayfolk64/actions/runs/34779220005) 通过后，最后发布正式名称 [2026f-autotest/verify-preparation-20260914-Alayfolk64](https://github.com/2026f-autotest/verify-preparation-20260914-Alayfolk64)。准备前后仓库 ID 均为 `1368819382`，证明重试继续使用原仓库。

准备测试时，尝试通过 Contents API 修改验证工作流得到 `HTTP 404`，响应为 `{"message":"Not Found","documentation_url":"https://docs.github.com/rest/repos/contents#create-or-update-file-contents","status":"404"}`，CLI 原始错误为 `gh: Not Found (HTTP 404)`。API 未给出更具体原因；改用现有 SSH Git 推送后完成测试准备，未扩大凭证权限。这是测试准备步骤的错误，生产领取不通过该接口写工作流。

上述真实测试证明新建、配置失败不发布、准备阶段不评分、修复后续跑和最后改名。没有调用 OpenCamp 上传接口，也没有用第二个外部账号验证接受邀请。

## 首次上线的真实 Issue 和 Actions

| 课程 | 真实申请 | 自动领取运行 | 学员配置检查 |
| --- | --- | --- | --- |
| 2073 rCore | [#1](https://github.com/2026f-autotest/enroll/issues/1) | [34777548104](https://github.com/2026f-autotest/enroll/actions/runs/34777548104)，维护者重试成功 | [34777555641](https://github.com/2026f-autotest/2026f-rcore-Alayfolk64/actions/runs/34777555641)，成功 |
| 2074 Rust 进阶 | [#2](https://github.com/2026f-autotest/enroll/issues/2) | [34777562329](https://github.com/2026f-autotest/enroll/actions/runs/34777562329)，新 Issue 自动触发成功 | [34777568466](https://github.com/2026f-autotest/2026f-oscamp-base-Alayfolk64/actions/runs/34777568466)，成功 |
| 2078 组件化操作系统 | [#3](https://github.com/2026f-autotest/enroll/issues/3) | [34777563223](https://github.com/2026f-autotest/enroll/actions/runs/34777563223)，新 Issue 自动触发成功 | [34777569845](https://github.com/2026f-autotest/2026f-arceos-Alayfolk64/actions/runs/34777569845)，成功 |

三份申请的真实作者都是 `Alayfolk64`。自动程序成功读取该账号、配置其课程仓库、触发配置检查、由 `github-actions` 回复仓库及邀请链接，并关闭申请。

这三次入口测试沿用了之前已创建的维护者课程仓库，证明自动申请、配置、回复和重试链路可用；没有声称本轮额外创建了三个仓库。首次从模板建仓的真实记录位于各课程的验证文档。普通组织外部学员接受邀请的步骤尚未用第二个账号实测。

## 一次性凭证

维护者明确授权后，`ENROLL_GITHUB_TOKEN` 仅保存为本入口仓库的 Actions Secret。API 元数据已确认：组织 Secrets 仍只有三个课程上传凭证，三个现有学员仓库的仓库级 Secret 列表均为空，未向学员分发建仓凭证。

首次申请 [34777399903](https://github.com/2026f-autotest/enroll/actions/runs/34777399903) 发生在凭证配置前，真实失败为：

```text
领取入口尚未配置 ENROLL_GITHUB_TOKEN，请维护者完成一次性建仓授权。
Process completed with exit code 1.
```

机器人正确回复失败提示。凭证配置后重试原 Issue 成功，见上表；失败证据保留。

## 代码校验与成绩核对

首次上线时，6 项本地测试和 [GitHub 检查 34777296793](https://github.com/2026f-autotest/enroll/actions/runs/34777296793) 通过，覆盖课程白名单、账号只取申请人、异常输入、全部章节复制及不覆盖无关仓库。API 模拟测试与上面的真实 GitHub 运行分别记录。

课程 2074 真实 CI 为 0/100，2078 为 0/600，均得到 OpenCamp `result=1` 响应；公开排行榜中该账号的分数一致。rCore 未完成章节按规则不上传，本轮未声称完成 rCore 正向分数上传。详见[OpenCamp 页面核对](OPENCAMP-CHECK.md)及三个课程仓库的验证记录。
