#!/bin/bash
# quick self-identity check
ERROR='\033[0;31m'
WARN='\033[0;33m'
INFO='\033[0;32m'
EC='\033[0m'
[[ `grep -cm1 docker /proc/1/cgroup 2> /dev/null` ]] || \
   { echo -e "${ERROR}* Cannot execute outside Docker scope${EC}"; exit 1; }
NODE_MODULES_PATH="/tmp/node_modules"
cat /dev/null | tee .lint_out .test_out .test_err

echo -e "\t${INFO}+ Running tests...${EC}"
npm run test 2> .test_err 1> .test_out
[[ "$?" -le 0 ]] && cat /dev/null > .test_err

# echo -e "\t${INFO}+ Running coverage checks...${EC}"
# rm -rf .cov_temp
# $NODE_MODULES_PATH/babel-cli/bin/babel-node.js \
#    $NODE_MODULES_PATH/istanbul/lib/cli.js cover \
#    --config .istanbul-config.yml \
#    $NODE_MODULES_PATH/mocha/bin/_mocha -- --recursive &> /dev/null
# $NODE_MODULES_PATH/istanbul/lib/cli.js \
#    check-coverage --root .cov_temp \
#    --config .istanbul-config.yml &> \
#    .cov_temp/coverage-summary


if [ -e .eslintrc ]; then
   echo -e "\t${INFO}+ Running lint checks...${EC}"
   $NODE_MODULES_PATH/eslint/bin/eslint.js -f compact -o .lint_out
else
   echo -e "\t${WARN}+ Lint checks skipped, no .eslintrc present.${EC}"
fi
