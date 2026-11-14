"""
Запустите этот скрипт после скачивания git репозитория для его инициализации
"""

import os
import subprocess

def main():
    # ../.gitconfig - относительно ./.git/config
    subprocess.run(["git", "config", "--local", "include.path", "../.gitconfig"])
