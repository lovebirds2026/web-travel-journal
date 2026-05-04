#!/usr/bin/env python
import os
import subprocess
from functools import partial

REPO = '/home/aimebgl3/python/travel-dev'
VENV_BIN = '/home/aimebgl3/virtualenv/python/travel-dev/3.13/bin'

run = partial(subprocess.run, shell=True, check=True) # cwd=str

def rollback():
    run('git reset --hard HEAD@{1}')
    run(f'"{VENV_BIN}/pip" install -e .')

def main():
    os.chdir(REPO)
    run('git pull origin dev-deni')
    run(f'"{VENV_BIN}/pip" install -e .')

    try:
        run(f'"{VENV_BIN}/pytest"')
    except subprocess.CalledProcessError:
        rollback()
        raise SystemExit('Tests failed, reverted to previous commit.')

    run('touch tmp/restart.txt')
    run('echo "Project deployed!"')

if __name__ == '__main__':
    main()
