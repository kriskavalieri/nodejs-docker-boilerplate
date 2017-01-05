#!/usr/bin/env python
import atexit
import glob
import json
import os
import re
import subprocess
import sys

stable_branch_re = re.compile(r'master|stable|prod|production')

COLOR_CODES = {
    'WARN': '\033[0;33m',
    'INFO': '\033[0;32m',
    'EC': '\033[0m'
}

def exe(cmd):
    out = subprocess.check_output(cmd.strip().split(" "))
    return out.decode().strip()

def get_tracking_branch(local_branch):
    try:
        cmd = 'git rev-parse --abbrev-ref {}@{{upstream}}'.format(local_branch)
        return exe(cmd)
    except subprocess.CalledProcessError:
        return ""

def set_mode_prefixes():
    cov_34_mode = ''
    current_branch = exe('git rev-parse --abbrev-ref HEAD')
    tracking_branch = get_tracking_branch(current_branch)

    if not stable_branch_re.search(tracking_branch):
        prefix = ("{INFO}* On branch `{}` which is not production-bound, "
                  "executing nondiscriminatory checks...{EC}").format(current_branch, **COLOR_CODES)
        cov_34_mode = "_light"
    else:
        prefix = "* Push to production branch detected, executing full-scale checks..."
    print(prefix + "\n* Running pre-flight checks, please hold...")
    return cov_34_mode

def lint_consumer(fn):
    def wrap(complaints, GIT_ROOT, **kwargs):
        complaints = fn(complaints, GIT_ROOT, **kwargs)
        devmode = kwargs.get('devmode', False)
        LINT_OUT = os.path.join(GIT_ROOT, ".lint_out")
        if os.path.getsize(LINT_OUT):
            # file not empty, errors/warnings present, interrupt and print
            complaints += "\n* Lint returned some errors/warnings: \n{}\n\n".format(
                open(LINT_OUT).read().strip() if not devmode else \
                subprocess.check_output(['tail', '-1', LINT_OUT])
            )
        return complaints
    return wrap

def coverage_consumer(fn):
    def wrap(complaints, GIT_ROOT, **kwargs):
        complaints = fn(complaints, GIT_ROOT, **kwargs)
        COV_SUMMARY = os.path.join(GIT_ROOT, ".cov_temp/coverage-summary")
        if os.path.isfile(COV_SUMMARY) and os.path.getsize(COV_SUMMARY):
            with open(COV_SUMMARY) as cov_summary:
                total_covs = cov_summary.read()
                if total_covs:
                    istanbul_rates = json.dumps(
                        re.findall(r'ERROR: (.*)', total_covs), indent=2)
                    complaints += "* Istanbul complained about too low coverage rates: \n{}".format(istanbul_rates)
        return complaints
    return wrap

def test_consumer(fn):
    def wrap(complaints, GIT_ROOT, **kwargs):
        complaints = fn(complaints, GIT_ROOT, **kwargs)
        TEST_OUT = os.path.join(GIT_ROOT, ".test_out")
        TEST_ERR = os.path.join(GIT_ROOT, ".test_err")
        if os.path.getsize(TEST_ERR):
            complaints += "\n* Tests failed. Error output was: \n{}\n".format(
                open(TEST_OUT).read().strip()
            )
        return complaints
    return wrap

@lint_consumer
@coverage_consumer
@test_consumer
def _run_checks(complaints, GIT_ROOT, verbose=False, devmode=False):
    test_dir = glob.glob(GIT_ROOT + "/test*")
    assert test_dir and os.path.isdir(test_dir[0]), \
           "Package's test directory not found"

    os.chdir(GIT_ROOT)
    args = " -v" if verbose else ""
    os.system("bash {}/run_checks_in_docker.sh {}".format(GIT_ROOT, args))
    return ""

def run_checks(*args, **kwargs):
    complaints = _run_checks("", *args, **kwargs)
    separator = "\n{:#^70}\n".format(" Summary ")
    print(separator)
    if complaints and not kwargs.get('devmode'):
        print(complaints)
        sys.exit(1)
    print("* All clear")

if __name__ == "__main__":
    cov_34_mode = set_mode_prefixes()
    HOOKS_PATH = os.path.dirname(os.path.abspath(__file__))
    GIT_ROOT = os.path.join(HOOKS_PATH, "../..")
    COV_34_CONFIG = os.path.join(GIT_ROOT, ".istanbul", ".istanbul-config{}.yml".format(cov_34_mode))
    os.system("cp {} ../.istanbul-config.yml".format(COV_34_CONFIG))
    @atexit.register
    def restore_default_34_config():
        os.system("cp {} ../.istanbul-config.yml".format(
            COV_34_CONFIG.replace(cov_34_mode, "")))
    run_checks(GIT_ROOT, devmode=bool(cov_34_mode))
