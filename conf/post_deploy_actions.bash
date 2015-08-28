#!/bin/bash

# abort on any errors
set -e

# check that we are in the expected directory
cd `dirname $0`/..

# create/update the virtual environment
virtualenv_dir='../virtualenv'
virtualenv_activate="$virtualenv_dir/bin/activate"
if [ ! -f "$virtualenv_activate" ]
then
    virtualenv $virtualenv_dir
fi
source $virtualenv_activate

# Upgrade pip to a secure version
pip_version="$(pip --version)"
if [ "$(echo -e 'pip 1.4\n'"$pip_version" | sort -V | head -1)" = "$pip_version" ]; then
    curl -L -s https://raw.github.com/mysociety/commonlib/master/bin/get_pip.bash | bash
fi

pip install --requirement requirements.txt

# make sure that there is no old code (the .py files may have been git deleted)
find . -name '*.pyc' -delete
