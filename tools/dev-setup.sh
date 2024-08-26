#!/bin/bash

# Look for help in any parameters.
if [[ $* == *"help"* ]]; then
    echo Sets up the dev environment for tbp. Requires the virtual environment
    echo to be setup. The default is to do a --dry-run.
    echo Pass '--doit' as the first parameter to do the pip installs.
    exit 0
fi

if [[ -z "${VIRTUAL_ENV}" ]]; then
  echo A virtual environment is *NOT* active. Cannot continue.
  exit 1
fi


dryrun="--dry-run"

if [[ $1 == "--doit" ]]; then
    unset dryrun
fi

python -m pip install $dryrun --upgrade pip
python -m pip install $dryrun .\[dev\]
python -m pip install $dryrun --editable .
