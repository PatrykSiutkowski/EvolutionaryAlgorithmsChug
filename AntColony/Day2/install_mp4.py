#!/usr/bin/env python3

import subprocess

def install_mp4():
    subprocess.run(
        ["winget", "install", "Gyan.FFmpeg"],
        check=True
    )

if __name__ == "__main__":
    install_mp4()