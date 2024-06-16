# log.py

from datetime import datetime
import os
basedir = os.path.dirname(os.path.abspath(__file__))


def log_execution_time(path):
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    with open(path, 'a') as f:
        f.write(f'GitHub Actions workflow executed at: {current_time}\n')

if __name__ == "__main__":
    log_execution_time(os.path.join(basedir, 'execution_log.txt'))
