#
# Makefile for pymongoshell
#
# joe@joedrumgoole.com
#

ATLAS_HOSTS="demodata-shard-0/demodata-shard-00-00-rgl39.mongodb.net:27017,demodata-shard-00-01-rgl39.mongodb.net:27017,demodata-shard-00-02-rgl39.mongodb.net:27017"
PYTHON=python3

start_server:
	@mkdir -p data
	@rm -rf mongod.log
	@if [ -f "mongod.pid" ]; then\
		echo "mongod is already running PID=`cat mongod.pid`";\
	else\
		echo "starting mongod";\
		mongod --dbpath ./data --fork --pidfilepath `pwd`/mongod.pid --logpath `pwd`/mongod.log 2>&1 > /dev/null;\
		echo "Process ID=`cat mongod.pid`";\
	fi;

stop_server:
	@if [ -f "mongod.pid" ]; then\
		echo "killing mongod process: "`cat "mongod.pid"`;\
		kill `cat "mongod.pid"`;\
		rm "mongod.pid";\
		rm "mongod.log";\
		echo "done";\
	fi;

delay:
	sleep 5

test: start_server get_zipcode_data
	nosetests

prod_build:clean  sdist
	python setup.py upload
	#twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u jdrumgoole

test_start_stop: start_server delay stop_server
	@echo "Testing start/stop server"

test_build: clean sdist
	python setup.py testupload
	#twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

sdist:
	${PYTHON} setup.py sdist bdist_wheel

clean:
	rm -rf dist bdist sdist mongodbshell.egg-info zipcodes.mdp.gz
	${PYTHON} ./pymongoshell/drop_collection.py

get_zipcode_data:
	python ./pymongoshell/demo_exists.py

push:
	git add -u
	git commit -m"WIP"
	git push

release: test tox push
	git add -u
	git commit -m"Checkin for release to pypi"
	git push
	${PYTHON} setup.py upload

tox:
	tox

init:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole

