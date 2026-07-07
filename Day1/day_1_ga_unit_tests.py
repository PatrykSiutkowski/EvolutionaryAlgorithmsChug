#!/usr/bin/env python3

import unittest
import sys
import subprocess


class TestEnvironment(unittest.TestCase):

    def test_python_version(self):
        major_version = sys.version_info.major
        minor_version = sys.version_info.minor

        print(f"\n[INFO] Running Python version: {major_version}.{minor_version}")
        
        # Assert that we are using at least Python 3
        self.assertEqual(major_version, 3, "Python version is not 3.x")

    def test_matplotlib_installed(self):
        try:
            import matplotlib
            print(f"[INFO] Matplotlib is available (Version: {matplotlib.__version__})")
        except ImportError:
            self.fail("matplotlib is not installed in the current environment")

    def test_git_accessible(self):
        try:
            # Runs 'git --version' without popping up a console window
            result = subprocess.run(
                ["git", "--version"], 
                capture_output=True, 
                text=True, 
                check=True
            )
            # Strips the trailing newline from the output
            git_version = result.stdout.strip()
            print(f"[INFO] Git is available ({git_version})")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            self.fail("Git is either not installed or not added to your system's PATH")


if __name__ == "__main__":
    unittest.main()