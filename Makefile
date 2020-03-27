#
# Makefile for mongodbshell
#
# joe@joedrumgoole.com
#

ATLAS_HOSTS="demodata-shard-0/demodata-shard-00-00-rgl39.mongodb.net:27017,demodata-shard-00-01-rgl39.mongodb.net:27017,demodata-shard-00-02-rgl39.mongodb.net:27017"
PYTHON=python

start_windows_server:
	@mkdir -p data
	@rm -rf mongod.log
	@if [ -f "mongod.pid" ]; then\
		echo "mongod is already running PID=`cat mongod.pid`";\
	else\
		echo "starting mongod";\
		"mongod --dbpath ./data --pidfilepath mongod.pid --logpath mongod.log" 2>&1 > /dev/null;\
		echo "Process ID=`cat mongod.pid`";\
	fi

stop_windows_server:
	@if [ -f "mongod.pid" ]; then\
		kill `cat mongod.pid`;\
		echo "killing mongod process `cat mongod.pid`";\
		rm mongod.pid;\
	fi;

start_server:
	@mkdir -p data
	@rm -rf mongod.log
	@if [ -f "mongod.pid" ]; then\
		echo "mongod is already running PID=`cat /tmp/mongod.pid`";\
	else\
		echo "starting mongod";\
		mongod --dbpath ./data --fork --pidfilepath mongod.pid --logpath mongod.log 2>&1 > /dev/null;\
		echo "Process ID=`cat /tmp/mongod.pid`";\
	fi;
#		echo "mongod is already running on port `cat /tmp/mongod.pid`"\
#	else\


#		echo "Process ID: `cat /tmp/mongod.pid`"\
#	fi;

stop_server:
	@if [ -f "mongod.pid" ]; then\
		kill `cat mongod.pid`;\
		echo "killing mongod process `cat mongod.pid`";\
		rm /tmp/mongod.pid;\
	fi;

test: start_server get_zipcode_data
	nosetests

prod_build:clean  sdist
	twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u jdrumgoole

test_build: clean sdist
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

sdist:
	${PYTHON} setup.py sdist

clean:
	rm -rf dist bdist sdist mongodbshell.egg-info zipcodes.mdp.gz
	${PYTHON} ./mongodbshell/drop_collection.py

get_zipcode_data:
	python ./mongodbshell/demo_exists.py

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

