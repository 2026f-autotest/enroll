# 自动化代码审查与修复（2026-09-14）

## 审查范围

本次检查领取入口及 rCore、Rust 进阶、ArceOS 三门课的全部自有自动化 Python 代码、回归测试、Actions 工作流、Issue 表单、课程配置和操作文档。核对已有学员仓库与模板的公共文件、rCore 的全部章节分支及部署差异。实验题目、学生待完成的内核代码和上游第三方依赖不属于此次自动化代码审查；没有修改实验答案、分值或 OpenCamp 后台。

## 已修复

| 问题 | 修复 |
| --- | --- |
| 仅重跑上传作业时，新的 run attempt 拼不出旧测试附件名 | 测试作业输出不可变 artifact ID，上传作业按该 ID 下载原始附件 |
| 重跑旧提交可能覆盖更新的当前分数 | Rust 进阶、ArceOS 上传前核对远端 main SHA，并拒绝比已记录 run ID 更旧的运行 |
| 新 push 的工作流级取消会打断正在上传的作业 | 只取消旧测试；上传作业独立排队，不被新测试自动取消 |
| 成绩 JSON 无法区分“已测量”和“OpenCamp 已接受” | 先保存真实分数及 pending 状态，仅在严格收到整数 result=1 后记录 accepted |
| HTTP 超时或响应中断提示不完整，布尔值 true 也可能误判为 result=1 | 明确区分 HTTP/业务失败与响应中断，脱敏错误，严格校验返回值类型 |
| 最终改名外层重试可能绕过 GitHub 的长时间限流提示 | 传递 Retry-After，改名重试遵守等待时间和总预算，不提前重发 |
| 仓库已完成但 Issue 通知失败时，统一报“领取未完成” | 失败通知保留已完成仓库及配置检查链接，准确区分交付与通知 |
| 三份备用建仓脚本仍采用旧流程，未等待配置检查 | 改用与领取入口逐字一致的 provision.py/github_api.py，统一最后发布正式名称 |
| 归档仓库及不合法成绩历史未明确拒绝 | 配置前拒绝归档/禁用仓库；校验结果类型及 rCore 历史总分和章节记录 |
| Actions 标签、rCore 容器标签可变化 | 所有直接 Actions 依赖固定完整 commit SHA，rCore 2024a 容器固定 registry digest |
| 课程自动化没有持续回归入口 | 三门课加入 Check course automation，代码改动及手动触发都可运行测试 |
| 课程页面需再次选课 | 三门课各有预选课程的领取链接，提供可直接放入课程的简明流程 |

## 本地验证

`python3 -m unittest discover -s tests -v`：领取入口 35 项通过。

各课程执行 `python3 -m unittest discover -s .github/tests -v`：Rust 进阶 19 项、ArceOS 19 项、rCore 13 项通过，总计 86 项。HTTP 限流、网络断开及接口异常为故障注入；测试中的分数数据不发送到 OpenCamp。真实进程测试核对了 stdout、stderr 和退出码 7。

所有工作流通过 YAML 解析；三份课程表单的默认选项通过实际申请解析器核对；全部直接 Actions 引用为 40 位 SHA；三份备用建仓公共模块与入口一致。逐分支部署时仅同步清单内公共文件，核对提交前后差异。

## 真实 GitHub 验证

部署后在此补充真实配置、评测和上传作业重跑结果。

## 维护者后续事项

组织课程 Secret 当前对公开仓库共享。拥有学员仓库写权限的用户可以修改工作流并使用这些 Secret；学员可写的评分代码和成绩历史也不是防篡改边界。仅靠身份变量、SHA 固定或重试不能解决这一点。需要防止人为伪造成绩时，应将可信评测及上传集中到维护者控制的仓库，并将课程凭证限定在那里使用。本次保持已授权的课程接入方式，没有把临时建仓凭证分发给学员。

`ENROLL_GITHUB_TOKEN` 仍是用户明确授权的维护者凭证，仅存放在领取入口。其权限较宽、有效性依赖该账号；后续可迁移为组织 GitHub App 的短期安装令牌。未声称本轮已迁移 GitHub App。

直接 Actions 与容器已固定版本，但基础系统软件源、复合 Action 内部依赖和工具链下载仍依赖外部服务。课程需保留版本更新和定期验证。评分结果附件保留 30 天，过期后须重新评测。

## 依据

- [GitHub 作业重跑保留原始提交](https://docs.github.com/en/actions/how-tos/manage-workflow-runs/re-run-workflows-and-jobs)
- [Actions 排队与取消规则](https://docs.github.com/en/actions/how-tos/write-workflows/choose-when-workflows-run/control-workflow-concurrency)
- [GitHub Secret 权限和固定依赖建议](https://docs.github.com/en/actions/reference/security/secure-use)
- [Issue 表单默认选项](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-githubs-form-schema)
