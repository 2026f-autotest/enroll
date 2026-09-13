"""Create a course repository for the author of a GitHub Issue."""

import json
import os
from pathlib import Path
import re
import sys
import time

from github_api import GitHubError, api, redact

ROOT = Path(__file__).resolve().parent
ORGANIZATION = "2026f-autotest"
HUB = ORGANIZATION + "/enroll"
COURSES = json.loads((ROOT / "courses.json").read_text())
CONFIGURATION_TIMEOUT = 600
POLL_INTERVAL = 10


class ConfigurationError(RuntimeError):
    def __init__(self, message, url):
        super().__init__(f"{message}: {url}")
        self.url = url


def check_configuration(repository):
    endpoint = "repos/" + repository
    # Dispatch metadata identifies this exact run, even if other runs exist.
    dispatched = api("POST", endpoint + "/actions/workflows/check-config.yml/dispatches",
                     {"ref": "main", "return_run_details": True}, retry=True)
    run_id = (dispatched or {}).get("workflow_run_id")
    if type(run_id) is not int or run_id <= 0:
        raise RuntimeError("GitHub did not return a configuration run ID; enrollment was not confirmed.")
    url = f"https://github.com/{repository}/actions/runs/{run_id}"
    deadline = time.monotonic() + CONFIGURATION_TIMEOUT
    while time.monotonic() < deadline:
        run = api("GET", endpoint + f"/actions/runs/{run_id}", missing_ok=True)
        if run is not None and run["status"] == "completed":
            if run["conclusion"] != "success":
                raise ConfigurationError(f"Configuration check ended with {run['conclusion']}", url)
            jobs = api("GET", endpoint + f"/actions/runs/{run_id}/jobs")
            if not any(job["name"] == "configuration" and job["conclusion"] == "success"
                       for job in jobs["jobs"]):
                raise ConfigurationError("Configuration job did not actually pass (missing or skipped)", url)
            print("Configuration check passed: " + url, flush=True)
            return url
        status = run["status"] if run is not None else "not yet visible"
        print(f"Waiting for configuration check ({status}): {url}", flush=True)
        time.sleep(POLL_INTERVAL)
    raise ConfigurationError("Configuration check was not completed within 10 minutes", url)


def parse_request(issue):
    if issue.get("pull_request") is not None:
        raise ValueError("Pull requests are not enrollment applications.")
    user = issue["user"]
    login = user["login"]
    if user.get("type") != "User" or not re.fullmatch(
            r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", login):
        raise ValueError("The applicant must be a personal GitHub account.")
    # Parse only the form's fixed course field. Never use a supplied account,
    # template, repository path or command from the issue body.
    matches = re.findall(r"^### 课程\s*\n+([^\n]+)", issue.get("body") or "", re.MULTILINE)
    if len(matches) != 1:
        raise ValueError("请使用“领取作业仓库”申请表，选择一门课程。")
    choice = matches[0].strip()
    for course_id, course in COURSES.items():
        if choice == f"{course_id} · {course['title']}":
            return login, course_id, course
    raise ValueError("课程不在本期领取列表中，请重新选择课程。")


def validate_source(repo, template):
    source_name = (repo.get("template_repository") or {}).get("full_name", "")
    if source_name.lower() != template.lower() or repo.get("private"):
        raise ValueError(repo.get("full_name", "Repository") +
                         " already exists with a different source; left untouched.")


def prepare_repository(repository, template, course, login, course_id):
    endpoint = "repos/" + repository
    repo = api("GET", endpoint, missing_ok=True)
    if repo is not None:
        validate_source(repo, template)
    else:
        try:
            api("POST", "repos/" + template + "/generate", {
                "owner": ORGANIZATION, "name": repository.split("/", 1)[1],
                "private": False, "include_all_branches": True,
                "description": f"Preparing OpenCamp {course_id} coursework for {login}",
            }, retry=True)
        except GitHubError as error:
            if not error.temporary and error.status != 422:
                raise
            print(str(error), flush=True)
            repo = api("GET", endpoint, missing_ok=True)
            if repo is None:
                raise
            validate_source(repo, template)
            print("Preparation repository exists after create error; continuing configuration.")

    for attempt in range(30):
        repo = api("GET", endpoint, missing_ok=True)
        branches = api("GET", endpoint + "/branches?per_page=100", missing_ok=True) if repo else None
        if repo and branches is not None and set(course["branches"]).issubset(
                {item["name"] for item in branches}):
            validate_source(repo, template)
            return repo
        if attempt == 29:
            raise ValueError("Repository generation is incomplete; preparation was not published.")
        time.sleep(2)


def publish_repository(preparing, final_repository, repository_id):
    # Rename is the final configuration write. All setup and the exact CI
    # check have passed, and repository invitations follow the repository ID.
    for attempt in range(1, 5):
        existing = api("GET", "repos/" + final_repository, missing_ok=True)
        if existing is not None:
            if existing["id"] != repository_id:
                raise ValueError("The final repository name is already occupied; nothing was overwritten.")
            return
        current = api("GET", "repos/" + preparing)
        if current["id"] != repository_id:
            raise ValueError("Preparation repository identity changed; nothing was renamed.")
        try:
            api("PATCH", "repos/" + preparing, {
                "name": final_repository.split("/", 1)[1],
                "description": "OpenCamp coursework; enrollment configuration verified",
            }, retry=False)
        except GitHubError as error:
            # A lost rename response can still mean success. Check the exact
            # repository ID before retrying, never another student's repo.
            if not error.temporary and error.status not in {404, 422}:
                raise
            print(str(error), flush=True)
            existing = api("GET", "repos/" + final_repository, missing_ok=True)
            if existing is not None and existing["id"] == repository_id:
                return
            if attempt == 4:
                raise
        else:
            existing = api("GET", "repos/" + final_repository, missing_ok=True)
            if existing is not None and existing["id"] == repository_id:
                return
            if attempt == 4:
                raise RuntimeError("Cannot verify the published repository ID.")
        time.sleep(2 ** attempt)


def provision(login, course_id, course):
    # Finish all checks that do not need a repository before creating one.
    student = api("GET", "users/" + login)
    if student["type"] != "User" or student["login"].lower() != login.lower():
        raise ValueError("The applicant is not the expected personal GitHub account.")
    template = ORGANIZATION + "/" + course["template"]
    source = api("GET", "repos/" + template)
    if not source.get("is_template") or source.get("private"):
        raise ValueError(template + " must be a public template repository.")
    branches = api("GET", "repos/" + template + "/branches?per_page=100")
    if not set(course["branches"]).issubset({item["name"] for item in branches}):
        raise ValueError("Course template is missing required branches; no repository was created.")
    secret = api("GET", f"orgs/{ORGANIZATION}/actions/secrets/{course['secret']}")
    if secret.get("visibility") != "all":
        raise ValueError("The course organization secret must allow public repositories.")

    final_repository = template + "-" + login
    repo = api("GET", "repos/" + final_repository, missing_ok=True)
    if repo is None:
        repository = ORGANIZATION + "/preparing-" + course["template"] + "-" + login
        repo = prepare_repository(repository, template, course, login, course_id)
    else:
        validate_source(repo, template)
        repository = final_repository
        print("Checking existing course repository; student code is preserved: " + repository)
    endpoint = "repos/" + repository

    variable_path = endpoint + "/actions/variables/STUDENT_GITHUB"
    variable = api("GET", variable_path, missing_ok=True)
    if variable is None:
        try:
            api("POST", endpoint + "/actions/variables", {"name": "STUDENT_GITHUB", "value": login},
                retry=True)
        except GitHubError as error:
            if not error.temporary and error.status != 422:
                raise
            print(str(error), flush=True)
            variable = api("GET", variable_path, missing_ok=True)
            if variable is None:
                raise
        if variable is None:
            variable = api("GET", variable_path)
    if variable["value"].lower() != login.lower():
        raise ValueError("Repository belongs to another student; identity was not overwritten.")

    api("PUT", endpoint + "/actions/workflows/check-config.yml/enable")
    check_url = check_configuration(repository)
    api("PUT", endpoint + "/actions/workflows/build.yml/enable")
    api("PUT", endpoint + "/collaborators/" + login, {"permission": "push"})
    if repository != final_repository:
        publish_repository(repository, final_repository, repo["id"])
        check_url = check_url.replace(repository, final_repository, 1)
        print("Preparation passed; formal repository published: " + final_repository, flush=True)
    return "https://github.com/" + final_repository, check_url


def main():
    os.chdir(ROOT)
    (ROOT / "tmp").mkdir(exist_ok=True)
    os.environ["TMPDIR"] = str(ROOT / "tmp")
    if os.environ.get("GITHUB_REPOSITORY") != HUB:
        raise ValueError("Run this workflow only in " + HUB)
    event = json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text())
    event_name = os.environ["GITHUB_EVENT_NAME"]
    if event_name == "issues" and event.get("action") == "opened":
        issue = event["issue"]
    elif event_name == "workflow_dispatch":
        number = os.environ.get("RETRY_ISSUE_NUMBER", "")
        if not re.fullmatch(r"[1-9][0-9]*", number):
            raise ValueError("Enter the numeric application issue number.")
        issue = api("GET", f"repos/{HUB}/issues/{number}", issue=True)
    else:
        raise ValueError("Only new applications or maintainer retries are supported.")

    run_url = f"https://github.com/{HUB}/actions/runs/{os.environ['GITHUB_RUN_ID']}"
    process_application(issue, run_url)


def process_application(issue, run_url):
    number = issue["number"]
    try:
        login, course_id, course = parse_request(issue)
        if not os.environ.get("GH_TOKEN"):
            raise ValueError("领取入口尚未配置 ENROLL_GITHUB_TOKEN，请维护者完成一次性建仓授权。")
        url, check_url = provision(login, course_id, course)
        body = (
            f"@{login}，你的 **{course['title']}（{course_id}）** 作业仓库已配置。\n\n"
            f"1. [接受仓库邀请]({url}/invitations)（已有访问权限时可直接进入仓库）。\n"
            f"2. [打开作业仓库]({url})，按 README 克隆、完成实验并 push。\n"
            f"3. 在 [Actions]({url}/actions) 查看评测和成绩上传结果。\n\n"
            f"请在 [OpenCamp 本阶段](https://opencamp.cn/os2edu/camp/2026fall/stage/{course['stage']}) "
            f"加入课程并绑定 **{login}**。无需配置 Token，也无需安装 GitHub CLI。\n\n"
            f"[本次配置检查已通过]({check_url})，确认身份映射和课程凭证已配置。"
            "配置检查不会提交成绩，实际成绩由之后的实验 push 触发评测上传。"
        )
        api("POST", f"repos/{HUB}/issues/{number}/comments", {"body": body}, issue=True)
        api("PATCH", f"repos/{HUB}/issues/{number}", {"state": "closed"}, issue=True)
    except (ValueError, RuntimeError, OSError) as error:
        print(redact(str(error)), flush=True)
        message = f"本次领取未完成，请维护者查看[运行日志]({run_url})后重试该申请。学员无需填写 Token。"
        if isinstance(error, ConfigurationError):
            message += f"\n\n[本次配置检查]({error.url})尚未通过，因此保留申请供排查和重试。"
        try:
            api("PATCH", f"repos/{HUB}/issues/{number}", {"state": "open"}, issue=True)
            api("POST", f"repos/{HUB}/issues/{number}/comments", {"body": message}, issue=True)
        except (ValueError, RuntimeError, OSError) as notification_error:
            print("Could not report failure to the issue: " + redact(str(notification_error)), flush=True)
        raise
    print(f"Enrolled {login}: course={course_id}, repository={url}")


if __name__ == "__main__":
    try:
        main()
    except (ValueError, RuntimeError, OSError, KeyError) as error:
        sys.exit(redact(str(error)))
