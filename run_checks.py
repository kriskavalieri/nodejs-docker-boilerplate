import os
from pre_push import run_checks

filepath = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.join(filepath, "..")

if __name__ == "__main__":
    run_checks(project_root)
