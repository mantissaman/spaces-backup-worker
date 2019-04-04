#!/bin/bash
pushd `dirname $0` > /dev/null
SCRIPTPATH=`pwd -P`
popd > /dev/null

cd $SCRIPTPATH
echo $SCRIPTPATH
if [ ! -d "$SCRIPTPATH/env" ]
then
	echo "Creating Virtual Environment..."
	python3 -m venv env
    source env/bin/activate
fi
sort -um docker/worker/requirements.txt docker/api/requirements.txt requirements-dev.txt > requirements.txt
pip3 install -r  requirements.txt
