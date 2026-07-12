#!/usr/bin/env python3

import os
import unittest
import sys
import subprocess


class TestEnvironment(unittest.TestCase):
    def test_python_version(self): # Ensure Python version is 3.x
        major_version = sys.version_info.major
        print(f"\n[INFO] Running Python version: {major_version}.{sys.version_info.minor}")
        self.assertEqual(major_version, 3, "Python version is not 3.x")

    def test_pip_install(self):
        try:
            if os.name == 'nt':  # Windows
                print("[INFO] Windows detected. Running pip check...")
                subprocess.run(["pip", "--version"], check=True, shell=True)

            else:
                print("[INFO] Linux/Unix detected. Running apt-get...")
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[WARN] pip not found. Attempting installation...")

            try:
                if os.name == "nt":  # Windows
                    print("[INFO] Windows detected. Bootstrapping pip with ensurepip...")
                    subprocess.run(
                        [sys.executable, "-m", "ensurepip", "--upgrade"],
                        check=True
                    )
                    subprocess.run(
                        [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
                        check=True
                    )

                else:  # Linux/Unix
                    print("[INFO] Linux/Unix detected. Installing python3-pip...")
                    subprocess.run(["sudo", "apt-get", "update"], check=True)
                    subprocess.run(
                        ["sudo", "apt-get", "install", "-y", "python3-pip"],
                        check=True
                    )

                # Verify installation
                result = subprocess.run(
                    ["pip", "--version"],
                    capture_output=True,
                    text=True,
                    check=True,
                    shell=os.name == "nt"
                )
                print(f"[SUCCESS] pip installation completed ({result.stdout.strip()})")

            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                self.fail(f"pip was missing and auto-installation failed. Error: {e}")

    def test_matplotlib_installed(self): # Check if matplotlib is installed
        try:
            import matplotlib
            print(f"[INFO] Matplotlib is available (Version: {matplotlib.__version__})")
        except ImportError:
            self.fail("matplotlib is not installed in the current environment")

    def test_git_accessible(self): #Check if git is installed; if not, attempt to install it on Windows/Linux
        try: # Check if Git is already available
            result = subprocess.run(["git", "--version"], capture_output=True, text=True, check=True, shell=os.name == 'nt')  # nt Requires for some Windows environments to find CLI tools
            print(f"[INFO] Git is already available ({result.stdout.strip()})")
            
        except (subprocess.CalledProcessError, FileNotFoundError):
            print("[WARN] Git not found. Attempting auto-installation...")
            
            try:
                if os.name == 'nt':  # Windows
                    print("[INFO] Windows detected. Running winget install...")
                    # --silent and --accept-source-agreements ensure no GUI popups stall the script
                    subprocess.run(
                        ["winget", "install", "--id", "Git.Git", "-e", "--silent", "--accept-source-agreements"], 
                        check=True,
                        shell=True
                    )
                else:  # Linux/macOS fallback
                    print("[INFO] Linux/Unix detected. Running apt-get...")
                    subprocess.run(["sudo", "apt-get", "update"], check=True)
                    subprocess.run(["sudo", "apt-get", "install", "-y", "git"], check=True)
                
                print("[SUCCESS] Git installation completed successfully.")
                
            except (subprocess.CalledProcessError, FileNotFoundError) as e:
                self.fail(f"Git was missing and auto-installation failed. Error: {e}")


if __name__ == "__main__":
    unittest.main()