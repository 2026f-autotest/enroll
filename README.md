# 2026f OpenCamp 作业仓库领取

**[点击领取作业仓库](https://github.com/2026f-autotest/enroll/issues/new?template=enroll.yml)**

登录 GitHub，选择课程，提交申请。系统从申请人账号读取你的 GitHub 登录名，自动创建组织内的公开作业仓库、绑定身份并发送邀请，然后在申请下回复仓库链接。

> 入口代码已部署，一次性建仓凭证待配置。启用与真实验证结果见[维护记录](docs/VALIDATION.md)。

| 课程 | 模板 | OpenCamp |
| --- | --- | --- |
| 2074 · 基础阶段 - Rust 进阶 & OS 入门 | [Rust 进阶实验](https://github.com/2026f-autotest/2026f-oscamp-base) | [基础阶段](https://opencamp.cn/os2edu/camp/2026fall/stage/4) |
| 2073 · 专业阶段 - rCore-Tutorial | [rCore](https://github.com/2026f-autotest/2026f-rcore) | [专业阶段](https://opencamp.cn/os2edu/camp/2026fall/stage/5) |
| 2078 · 项目先导阶段 - 组件化操作系统 | [ArceOS](https://github.com/2026f-autotest/2026f-arceos) | [项目先导阶段](https://opencamp.cn/os2edu/camp/2026fall/stage/6) |

## 学员操作

1. 在 OpenCamp 加入对应阶段，并绑定当前 GitHub 账号。
2. 点击上方“领取作业仓库”，选课程并提交 Issue。
3. 等待机器人回复，接受仓库邀请。
4. 克隆机器人给出的仓库，按仓库 README 完成实验并 push。
5. 在 Actions 查看测试和上传结果，在 OpenCamp 查看成绩。

学员无需 Fork、加入组织、安装 GitHub CLI 或复制 Token。普通组织外部协作者也能完成作业。领取成功只表示 GitHub 仓库准备完成，不代表已经在 OpenCamp 报名。

## 维护者

本仓库由维护者控制，不向学员授予写权限。应急版使用一个仅保存在本仓库 Actions Secrets 的建仓凭证；三个课程上传 Token 继续由组织 Secrets 共享。具体一次性配置、重试和关闭入口步骤见[维护流程](docs/MAINTAINER.md)。
