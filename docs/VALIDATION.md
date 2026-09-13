# 领取入口验证记录（2026-09-14）

公开入口：[2026f-autotest/enroll](https://github.com/2026f-autotest/enroll)。

## 真实 Issue 和 Actions

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

6 项本地测试和 [GitHub 检查 34777296793](https://github.com/2026f-autotest/enroll/actions/runs/34777296793) 通过，覆盖课程白名单、账号只取申请人、异常输入、全部章节复制及不覆盖无关仓库。API 模拟测试与上面的真实 GitHub 运行分别记录。

课程 2074 真实 CI 为 0/100，2078 为 0/600，均得到 OpenCamp `result=1` 响应；公开排行榜中该账号的分数一致。rCore 未完成章节按规则不上传，本轮未声称完成 rCore 正向分数上传。详见[OpenCamp 页面核对](OPENCAMP-CHECK.md)及三个课程仓库的验证记录。
