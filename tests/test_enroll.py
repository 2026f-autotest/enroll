import unittest
from unittest.mock import patch

import enroll


def application(body=None):
    return {"number": 1, "user": {"login": "Student-123", "type": "User"},
            "body": body or "### 课程\n\n2073 · 专业阶段 - rCore-Tutorial\n"}


class EnrollmentTests(unittest.TestCase):
    def test_all_form_choices_map_to_fixed_catalog(self):
        for course_id, course in enroll.COURSES.items():
            issue = application(f"### 课程\n\n{course_id} · {course['title']}\n")
            login, selected, config = enroll.parse_request(issue)
            self.assertEqual((login, selected), ("Student-123", course_id))
            self.assertEqual(config, course)

    def test_student_identity_only_comes_from_issue_author(self):
        issue = application("### 课程\n\n2073 · 专业阶段 - rCore-Tutorial\n"
                            "\n### GitHub 登录名\n\nMaintainer\n$(touch unwanted)\n")
        self.assertEqual(enroll.parse_request(issue)[0], "Student-123")

    def test_unknown_or_ambiguous_course_rejected(self):
        for body in ["### 课程\n\n9999 · Other", "hello",
                     "### 课程\n\n2073 · 专业阶段 - rCore-Tutorial; echo unsafe",
                     application()["body"] * 2]:
            with self.assertRaises(ValueError):
                enroll.parse_request(application(body))

    def test_bot_and_pull_request_rejected(self):
        issue = application()
        issue["user"]["type"] = "Bot"
        with self.assertRaises(ValueError):
            enroll.parse_request(issue)
        issue = application()
        issue["pull_request"] = {}
        with self.assertRaises(ValueError):
            enroll.parse_request(issue)

    def test_new_repository_copies_all_chapters_and_binds_author(self):
        course = enroll.COURSES["2073"]
        calls = []

        def fake_api(method, path, data=None, missing_ok=False):
            calls.append((method, path, data))
            if path == "repos/2026f-autotest/2026f-rcore":
                return {"is_template": True, "private": False}
            if "/actions/secrets/" in path:
                return {"visibility": "all"}
            if "/branches?" in path:
                return [{"name": branch} for branch in course["branches"]]
            return None

        with patch.object(enroll, "api", side_effect=fake_api):
            url = enroll.provision("Student-123", "2073", course)
        self.assertEqual(url, "https://github.com/2026f-autotest/2026f-rcore-Student-123")
        generated = next(data for method, path, data in calls if path.endswith("/generate"))
        self.assertEqual(generated["include_all_branches"], True)
        self.assertEqual(generated["private"], False)
        self.assertIn(("POST", "repos/2026f-autotest/2026f-rcore-Student-123/actions/variables",
                       {"name": "STUDENT_GITHUB", "value": "Student-123"}), calls)
        self.assertIn(("PUT", "repos/2026f-autotest/2026f-rcore-Student-123/collaborators/Student-123",
                       {"permission": "push"}), calls)
        self.assertEqual(calls[-1][1].split("/")[-2:], ["check-config.yml", "dispatches"])

    def test_existing_different_repository_is_not_modified(self):
        def fake_api(method, path, data=None, missing_ok=False):
            self.assertEqual(method, "GET")
            if path.endswith("/2026f-rcore"):
                return {"is_template": True, "private": False}
            if "/actions/secrets/" in path:
                return {"visibility": "all"}
            return {"template_repository": {"full_name": "someone/else"}}

        with patch.object(enroll, "api", side_effect=fake_api):
            with self.assertRaisesRegex(ValueError, "left untouched"):
                enroll.provision("Student-123", "2073", enroll.COURSES["2073"])


if __name__ == "__main__":
    unittest.main()
