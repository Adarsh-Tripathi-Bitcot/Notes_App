#!/usr/bin/env python3
"""
Test Isolation Validation Script

This script validates that tests don't have external dependencies and
ensures complete isolation from external services, files, and network calls.
"""

import re
import subprocess
import sys
from pathlib import Path
from typing import List, Tuple


class TestIsolationValidator:
    """Validator for test isolation requirements."""

    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.test_dir = project_root / "tests"
        self.src_dir = project_root / "src"

        # Forbidden imports that indicate external dependencies
        self.forbidden_imports = [
            "redis",
            "openai",
            "boto3",
            "requests",
            "aiohttp",
            "urllib3",
            "httpx",  # Only allowed in source, not tests
            "cloudinary",
            "stripe",
            "twilio",
            "sendgrid",
            "mailgun",
            "smtplib",  # Email sending
            "smtpd",
            "ftplib",
            "telnetlib",
            "xmlrpc",
            "subprocess",  # Can be used to call external processes
            "os.system",
            "os.popen",
            "socket",  # Network operations
            "urllib.request",
            "urllib.parse",
            "http.client",
            "ftplib",
            "poplib",
            "imaplib",
            "nntplib",
        ]

        # Forbidden patterns that indicate external service usage
        self.forbidden_patterns = [
            r"requests\.",
            r"httpx\.",
            r"aiohttp\.",
            r"redis\.",
            r"openai\.",
            r"boto3\.",
            r"aws\.",
            r"gcp\.",
            r"azure\.",
            r"\.connect\(",
            r"\.send\(",
            r"\.upload\(",
            r"\.download\(",
            r"api_key\s*=",  # Only catch assignments, not usage
            r"secret_key\s*=",  # Only catch assignments, not usage
            r"access_token\s*=",  # Only catch assignments, not usage
            r"bearer_token\s*=",  # Only catch assignments, not usage
            r"\.env\b",  # Only catch .env file references, not environment variables
            r"os\.environ\[",  # Direct environment access
            r"os\.getenv\(",  # Direct environment access
            r"os\.environ\.get\(",  # Direct environment access
        ]

        # Allowed patterns (exceptions to the rules)
        self.allowed_patterns = [
            r"from unittest\.mock import",
            r"import unittest\.mock",
            r"@patch\(",
            r"mock_",
            r"Mock\(",
            r"MagicMock\(",
            r"AsyncMock\(",
            r"# Mock",
            r"# TODO:",
            r"# FIXME:",
            r"# NOTE:",
            r"# HACK:",
            r"# ALLOWED:",
            r"# EXTERNAL:",
            r"client\.get\(",  # TestClient HTTP methods are allowed
            r"client\.post\(",
            r"client\.put\(",
            r"client\.delete\(",
            r"TestClient",
            r"patch\.dict\(os\.environ",  # Environment variable patching is allowed
            r"os\.environ\.copy\(\)",  # Environment copying is allowed
            r"os\.environ\.update\(",  # Environment updating is allowed
            r"os\.environ\.clear\(\)",  # Environment clearing is allowed
            r"assert.*access_token",  # Assertions about access tokens are allowed
            r"assert.*secret_key",  # Assertions about secret keys are allowed
            r"def.*access_token",  # Function definitions with access_token are allowed
            r"def.*secret_key",  # Function definitions with secret_key are allowed
            r"hasattr.*secret_key",  # hasattr checks are allowed
            r"hasattr.*access_token",  # hasattr checks are allowed
        ]

    def find_test_files(self) -> List[Path]:
        """Find all test files in the project."""
        test_files = []

        if not self.test_dir.exists():
            print(f"❌ Test directory not found: {self.test_dir}")
            return test_files

        for pattern in ["test_*.py", "*_test.py"]:
            test_files.extend(self.test_dir.rglob(pattern))

        return sorted(test_files)

    def check_file_for_external_dependencies(self, file_path: Path) -> List[str]:
        """Check a single file for external dependencies."""
        issues = []

        try:
            content = file_path.read_text(encoding="utf-8")
            lines = content.split("\n")

            for line_num, line in enumerate(lines, 1):
                line_stripped = line.strip()

                # Skip comments and docstrings
                if (
                    line_stripped.startswith("#")
                    or line_stripped.startswith('"""')
                    or line_stripped.startswith("'''")
                ):
                    continue

                # Check for forbidden imports
                for forbidden in self.forbidden_imports:
                    if f"import {forbidden}" in line or f"from {forbidden}" in line:
                        # Check if it's in an allowed context
                        if not any(
                            re.search(pattern, line, re.IGNORECASE)
                            for pattern in self.allowed_patterns
                        ):
                            issues.append(
                                f"Line {line_num}: imports {forbidden} - {line.strip()}"
                            )

                # Check for forbidden patterns
                for pattern in self.forbidden_patterns:
                    if re.search(pattern, line, re.IGNORECASE):
                        # Check if it's in an allowed context
                        if not any(
                            re.search(allowed, line, re.IGNORECASE)
                            for allowed in self.allowed_patterns
                        ):
                            issues.append(
                                f"Line {line_num}: uses {pattern} - {line.strip()}"
                            )

        except Exception as e:
            issues.append(f"Error reading file: {e}")

        return issues

    def validate_test_isolation(self) -> Tuple[bool, List[str]]:
        """Validate that all tests are properly isolated."""
        test_files = self.find_test_files()

        if not test_files:
            return False, ["No test files found"]

        all_issues = []

        print(f"🔍 Checking {len(test_files)} test files for external dependencies...")

        for test_file in test_files:
            issues = self.check_file_for_external_dependencies(test_file)
            if issues:
                all_issues.append(f"\n📁 {test_file.relative_to(self.project_root)}:")
                all_issues.extend([f"  ❌ {issue}" for issue in issues])

        return len(all_issues) == 0, all_issues

    def check_conftest_isolation(self) -> Tuple[bool, List[str]]:
        """Check that conftest.py has proper isolation fixtures."""
        conftest_file = self.test_dir / "conftest.py"
        issues = []

        if not conftest_file.exists():
            return False, ["conftest.py not found"]

        content = conftest_file.read_text(encoding="utf-8")

        # Check for required isolation fixtures
        required_fixtures = [
            "test_environment",
            "mock_external_services",
            "mock_file_operations",
            "prevent_network_calls",
        ]

        for fixture in required_fixtures:
            if f"def {fixture}" not in content:
                issues.append(f"Missing required fixture: {fixture}")

        # Check for autouse=True on isolation fixtures
        autouse_fixtures = [
            "mock_external_services",
            "mock_file_operations",
            "prevent_network_calls",
        ]
        for fixture in autouse_fixtures:
            if (
                "@pytest.fixture(autouse=True)" not in content
                or f"def {fixture}" not in content
            ):
                issues.append("Fixture {} should have autouse=True".format(fixture))

        return len(issues) == 0, issues

    def run_tests_with_isolation_check(self) -> Tuple[bool, str]:
        """Run tests to ensure they work with isolation."""
        try:
            result = subprocess.run(
                [
                    "python3",
                    "-m",
                    "pytest",
                    "tests/",
                    "-v",
                    "--tb=short",
                    "--maxfail=1",
                ],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
            )

            if result.returncode == 0:
                return True, "All tests passed with isolation"
            else:
                return False, f"Tests failed:\n{result.stdout}\n{result.stderr}"

        except subprocess.TimeoutExpired:
            return False, "Tests timed out (possible external dependency issue)"
        except Exception as e:
            return False, f"Error running tests: {e}"

    def validate_all(self) -> bool:
        """Run all validation checks."""
        print("🧪 Test Isolation Validation")
        print("=" * 50)

        success = True

        # Check test files for external dependencies
        print("\n1. Checking test files for external dependencies...")
        isolation_ok, isolation_issues = self.validate_test_isolation()
        if not isolation_ok:
            print("❌ External dependency issues found:")
            for issue in isolation_issues:
                print(issue)
            success = False
        else:
            print("✅ No external dependencies found in tests")

        # Check conftest.py isolation setup
        print("\n2. Checking conftest.py isolation setup...")
        conftest_ok, conftest_issues = self.check_conftest_isolation()
        if not conftest_ok:
            print("❌ conftest.py isolation issues:")
            for issue in conftest_issues:
                print(f"  ❌ {issue}")
            success = False
        else:
            print("✅ conftest.py has proper isolation fixtures")

        # Run tests to ensure they work
        print("\n3. Running tests with isolation...")
        tests_ok, tests_message = self.run_tests_with_isolation_check()
        if not tests_ok:
            print(f"❌ {tests_message}")
            success = False
        else:
            print("✅ All tests passed with isolation")

        print("\n" + "=" * 50)
        if success:
            print("🎉 All validation checks passed! Tests are properly isolated.")
        else:
            print("💥 Validation failed! Please fix the issues above.")

        return success


def main():
    """Main entry point."""
    project_root = Path(__file__).parent.parent
    validator = TestIsolationValidator(project_root)

    success = validator.validate_all()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
