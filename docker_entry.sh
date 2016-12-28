#!/bin/bash
# quick self-identity check
grep -cm1 docker /proc/1/cgroup 2> /dev/null || echo "* Cannot execute outside Docker" && exit 1
echo "* Running coverage checks..."
rm -rf .cov_temp
istanbul cover --config .istanbul-config.yml test/test.js
istanbul check-coverage --root .cov_temp --config .istanbul-config.yml &> .cov_temp/coverage-summary

echo "* Running lint checks..."
cat /dev/null > .lint_out
eslint -f compact -o .lint_out .
