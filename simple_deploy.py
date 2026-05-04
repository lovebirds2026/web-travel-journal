#!/usr/bin/env python
import subprocess
from functools import partial

run = partial(subprocess.run, shell=True, check=True)

def rollback():
    run('git reset --hard HEAD@{1}')
    run('pip install -e .')

def main():
    run('cd /home/aimebgl3/python/travel-dev')
    run('git pull origin dev-deni')
    run('source /home/aimebgl3/virtualenv/python/travel-dev/3.13/bin/activate')
    run('pip install -e .')

    try:
        run('pytest')
    except subprocess.CalledProcessError:
        rollback()
        raise SystemExit('Tests failed, reverted to previous commit.')

    run('touch tmp/restart.txt')
    run('echo "Project deployed!"')

if __name__ == '__main__':
    main()
