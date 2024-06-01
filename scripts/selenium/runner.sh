#/bin/bash
#
current_dir="$PWD"
pushd $current_dir >/dev/null 2>&1
source env/bin/activate
python main.py
deactivate
popd >/dev/null 2>&1
