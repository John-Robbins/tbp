if [[ ! -z "${VIRTUAL_ENV}" ]]; then
      echo A virtual environment is active: ${VIRTUAL_ENV}
      echo Cannot continue. Use deactivate to turn it off.
      exit 1
fi

python3 -m venv .tbp-venv
source ./.tbp-venv/bin/activate

echo KILL THIS SHELL TO CONTINUE!
