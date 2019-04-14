#
# Makefile for mongodbshell
#
# joe@joedrumgoole.com
#

ATLAS_HOSTS="demodata-shard-0/demodata-shard-00-00-rgl39.mongodb.net:27017,demodata-shard-00-01-rgl39.mongodb.net:27017,demodata-shard-00-02-rgl39.mongodb.net:27017"

start_server:
	@mkdir -p data
	@rm -rf mongod.log
	@if [ -f "/tmp/mongod.pid" ]; then\
		echo "mongod is already running PID=`cat /tmp/mongod.pid`";\
	else\
		echo "starting mongod";\
		mongod --dbpath ./data --fork --pidfilepath /tmp/mongod.pid --logpath mongod.log 2>&1 > /dev/null;\
		echo "Process ID=`cat /tmp/mongod.pid`";\
	fi;
#		echo "mongod is already running on port `cat /tmp/mongod.pid`"\
#	else\


#		echo "Process ID: `cat /tmp/mongod.pid`"\
#	fi;

stop_server:
	@if [ -f "/tmp/mongod.pid" ]; then\
		kill `cat /tmp/mongod.pid`;\
		echo "killing mongod process `cat /tmp/mongod.pid`";\
		rm /tmp/mongod.pid;\
	fi;

test: start_server get_zipcode_data
	nosetests

prod_build:clean test build
	twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u jdrumgoole

test_build:test build
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

sdist:
	python setup.py sdist

clean:
	rm -rf dist bdist sdist mongodbshell.egg-info zipcodes.mdp.gz
	python3 ./mongodbshell/drop_collection.py

get_zipcode_data:
	@if ! `./mongodbshell/demo_exists.py`; then\
		if [ ! -f "zipcodes.mdp.gz" ]; then\
			wget https://s3-eu-west-1.amazonaws.com/developer-advocacy-public/zipcodes.mdp.gz;\
		fi;\
		mongorestore --drop --gzip --archive=zipcodes.mdp.gz;\
	fi

push:
	git add -u
	git commit -m"WIP"
	git push

release: test tox push
	git add -u
	git commit -m"Checkin for release to pypi"
	git push
	python3 setup.py upload

tox:
	tox

init:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole

