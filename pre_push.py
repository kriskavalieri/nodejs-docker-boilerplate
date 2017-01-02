#!/usr/bin/env python
import atexit
import glob
import json
import os
import re
import subprocess
import sys

stable_branch_re = re.compile(r'master|stable|prod|production')

def chain_cmds(cmds, stdin=None):
    for cmd in cmds:
        p = subprocess.Popen(cmd, stdin=stdin, stdout=subprocess.PIPE)
        stdin = p.stdout
    return p.stdout.read().strip().decode()

def get_current_branch():
    branch_cmd = "git rev-parse HEAD | git branch -a --contains | grep remotes | sed s/.*remotes.origin.//"
    return os.environ.get(
        "GIT_BRANCH",
        chain_cmds(
            [pipe_cmd.split(" ") for pipe_cmd in branch_cmd.split(" | ")]
        )
    )

def set_mode_prefixes():
    cov_34_mode = ''
    current_branch = get_current_branch()
    if not stable_branch_re.search(current_branch):
        prefix = "* On branch {} which is likely not production-bound, so executing low-threshold checks...".format(current_branch)
        cov_34_mode = "_light"
    else:
        prefix = "* Push to production branch detected, executing full-scale checks..."
    print(prefix + "\n* Running pre-flight checks, please hold...")
    return cov_34_mode

def run_checks(GIT_ROOT):
    test_dir = glob.glob(GIT_ROOT + "/test*")
    assert test_dir and os.path.isdir(test_dir[0]), \
           "Package's test directory not found"
    COV_SUMMARY = os.path.join(GIT_ROOT, ".cov_temp/coverage-summary")
    LINT_OUT = os.path.join(GIT_ROOT, ".lint_out")
    os.chdir(GIT_ROOT)
    os.system("bash {}/run_checks_in_docker.sh".format(GIT_ROOT))
    out = ""
    with open(COV_SUMMARY) as cov_summary, open(LINT_OUT) as lint:
        # on account of insignificantly low no of lines of .lint_out,
        # let's just read the whole thing at once
        if os.path.getsize(LINT_OUT):
            # file not empty, errors/warnings present, interrupt and print
            out += "\n* Lint returned some errors/warnings: \n{}\n\n".format(lint.read().strip())
        total_covs = cov_summary.read()
        if total_covs:
            istanbul_rates = json.dumps(
                re.findall(r'ERROR: (.*)', total_covs), indent=2)
            out += "* Istanbul complained about too low coverage rates: \n{}".format(istanbul_rates)
    separator = "\n{:#^70}\n".format(" Summary ")
    print(separator)
    if out:
        print(out)
        sys.exit(1)
    print("* All checked out good")

if __name__ == "__main__":
    cov_34_mode = set_mode_prefixes()
    HOOKS_PATH = os.path.dirname(os.path.abspath(__file__))
    GIT_ROOT = os.path.join(HOOKS_PATH, "../..")
    COV_34_CONFIG = os.path.join(GIT_ROOT, ".istanbul", ".istanbul-config.yml" + cov_34_mode)
    os.system("cp {} ../.istanbul-config.yml".format(COV_34_CONFIG))
    @atexit.register
    def restore_default_34_config():
        os.system("cp {} ../.istanbul-config.yml".format(
            COV_34_CONFIG.replace(cov_34_mode, "")))
    run_checks(GIT_ROOT)
