import contextlib
import io
import os
import subprocess
import unittest
from unittest.mock import patch

import github_api


def response(status, body='{}', headers=None):
    fields = {"Content-Type": "application/json", **(headers or {})}
    output = f"HTTP/2.0 {status} Status\n" + "".join(f"{key}: {value}\r\n" for key, value in fields.items())
    output += "\r\n" + body
    return subprocess.CompletedProcess(["gh"], 0 if 200 <= status < 300 else 1, output,
                                       "" if status < 400 else f"gh: request failed (HTTP {status})")


class GitHubRetryTests(unittest.TestCase):
    def setUp(self):
        self.clock = patch.object(github_api.time, "monotonic", return_value=0).start()
        self.sleep = patch.object(github_api.time, "sleep").start()
        self.addCleanup(patch.stopall)

    def test_temporary_server_error_retries_and_parses_real_header_format(self):
        with patch.object(github_api.subprocess, "run", side_effect=[response(502), response(200, '{"ok":true}')]) as run:
            self.assertEqual(github_api.api("GET", "repos/org/repo"), {"ok": True})
        self.sleep.assert_called_once_with(2)
        self.assertEqual(run.call_count, 2)
        self.assertIn("--include", run.call_args.args[0])

    def test_primary_rate_limit_waits_until_reset(self):
        limited = response(403, '{"message":"API rate limit exceeded"}',
                           {"X-RateLimit-Remaining": "0", "X-RateLimit-Reset": "1040"})
        with patch.object(github_api.time, "time", return_value=1000), \
                patch.object(github_api.subprocess, "run", side_effect=[limited, response(200)]):
            github_api.api("GET", "repos/org/repo")
        self.sleep.assert_called_once_with(41)

    def test_retry_after_is_respected_for_rate_limit_and_service_unavailable(self):
        for status in [429, 503]:
            self.sleep.reset_mock()
            with patch.object(github_api.subprocess, "run", side_effect=[
                    response(status, headers={"Retry-After": "15"}), response(200)]):
                github_api.api("GET", "repos/org/repo")
            self.sleep.assert_called_once_with(15)

    def test_secondary_limit_without_hint_waits_one_minute(self):
        with patch.object(github_api.subprocess, "run", side_effect=[
                response(403, '{"message":"You have exceeded a secondary rate limit."}'), response(200)]):
            github_api.api("GET", "repos/org/repo")
        self.sleep.assert_called_once_with(60)

    def test_long_rate_limit_fails_without_retrying_early(self):
        with patch.object(github_api.subprocess, "run", return_value=response(429, headers={"Retry-After": "3600"})) as run:
            with self.assertRaisesRegex(github_api.GitHubError, "no early retry"):
                github_api.api("GET", "repos/org/repo")
        self.sleep.assert_not_called()
        self.assertEqual(run.call_count, 1)

    def test_auth_permission_and_validation_errors_are_not_retried(self):
        for status in [401, 403, 404, 422]:
            with patch.object(github_api.subprocess, "run", return_value=response(status)) as run:
                with self.assertRaises(github_api.GitHubError) as raised:
                    github_api.api("GET", "repos/org/repo")
                self.assertEqual(raised.exception.status, status)
                self.assertEqual(run.call_count, 1)
        self.sleep.assert_not_called()

    def test_expected_404_returns_none(self):
        with patch.object(github_api.subprocess, "run", return_value=response(404)):
            self.assertIsNone(github_api.api("GET", "repos/org/repo", missing_ok=True))

    def test_read_timeout_retries(self):
        timeout = subprocess.TimeoutExpired(["gh"], 30, stderr=b"network stalled")
        with patch.object(github_api.subprocess, "run", side_effect=[timeout, response(200)]):
            self.assertEqual(github_api.api("GET", "repos/org/repo"), {})
        self.sleep.assert_called_once_with(2)

    def test_network_reset_retries_but_cli_configuration_error_does_not(self):
        reset = subprocess.CompletedProcess(["gh"], 1, "", "read: connection reset by peer")
        with patch.object(github_api.subprocess, "run", side_effect=[reset, response(200)]):
            github_api.api("GET", "repos/org/repo")
        self.sleep.assert_called_once_with(2)
        self.sleep.reset_mock()
        invalid = subprocess.CompletedProcess(["gh"], 1, "", "unknown flag: --invalid")
        with patch.object(github_api.subprocess, "run", return_value=invalid) as run:
            with self.assertRaises(github_api.GitHubError):
                github_api.api("GET", "repos/org/repo")
        self.assertEqual(run.call_count, 1)
        self.sleep.assert_not_called()

    def test_retries_stop_after_four_requests(self):
        with patch.object(github_api.subprocess, "run", return_value=response(502)) as run:
            with self.assertRaises(github_api.GitHubError):
                github_api.api("GET", "repos/org/repo")
        self.assertEqual(run.call_count, 4)
        self.assertEqual([call.args[0] for call in self.sleep.call_args_list], [2, 4, 8])

    def test_ambiguous_comment_post_is_not_duplicated(self):
        with patch.object(github_api.subprocess, "run", return_value=response(502)) as run:
            with self.assertRaises(github_api.GitHubError):
                github_api.api("POST", "repos/org/repo/issues/1/comments", {"body": "hello"})
        self.assertEqual(run.call_count, 1)
        self.sleep.assert_not_called()

    def test_explicit_safe_post_and_rejected_comment_can_retry(self):
        with patch.object(github_api.subprocess, "run", side_effect=[response(502), response(201)]):
            github_api.api("POST", "repos/org/template/generate", {}, retry=True)
        self.sleep.assert_called_once_with(2)
        self.sleep.reset_mock()
        with patch.object(github_api.subprocess, "run", side_effect=[
                response(429, headers={"Retry-After": "5"}), response(201)]):
            github_api.api("POST", "repos/org/repo/issues/1/comments", {"body": "hello"})
        self.sleep.assert_called_once_with(5)

    def test_credentials_are_redacted_from_retry_logs_and_errors(self):
        output = io.StringIO()
        with patch.dict(os.environ, {"GH_TOKEN": "secret-A", "ISSUE_TOKEN": "secret-B"}), \
                patch.object(github_api.subprocess, "run", return_value=response(502, 'secret-A secret-B')), \
                contextlib.redirect_stdout(output):
            with self.assertRaises(github_api.GitHubError) as raised:
                github_api.api("GET", "repos/org/repo")
        combined = output.getvalue() + str(raised.exception)
        self.assertNotIn("secret-A", combined)
        self.assertNotIn("secret-B", combined)
        self.assertIn("[REDACTED]", combined)


if __name__ == "__main__":
    unittest.main()
