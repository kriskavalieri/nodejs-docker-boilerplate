#!/bin/bash
# quick self-identity check
[[ `grep -cm1 docker /proc/1/cgroup 2> /dev/null` ]] || { echo "* Cannot execute outside Docker scope"; exit 1; }
echo -e "\t+ Running coverage checks..."
rm -rf .cov_temp
cat /dev/null > .lint_out
NODE_MODULES_PATH="/tmp/node_modules"
$NODE_MODULES_PATH/babel-cli/bin/babel-node.js \
   $NODE_MODULES_PATH/istanbul/lib/cli.js cover \
   --config .istanbul-config.yml \
   $NODE_MODULES_PATH/mocha/bin/_mocha -- --recursive &> /dev/null

$NODE_MODULES_PATH/istanbul/lib/cli.js \
   check-coverage --root .cov_temp \
   --config .istanbul-config.yml &> \
   .cov_temp/coverage-summary

if [ -e .eslintrc ]; then
   echo -e "\t+ Running lint checks..."
   $NODE_MODULES_PATH/eslint/bin/eslint.js -f compact -o .lint_out .
fi
