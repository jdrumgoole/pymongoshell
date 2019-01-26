#
# Makefile for mongodbshell
#
# joe@joedrumgoole.com
#

ATLAS_HOSTS="demodata-shard-0/demodata-shard-00-00-rgl39.mongodb.net:27017,demodata-shard-00-01-rgl39.mongodb.net:27017,demodata-shard-00-02-rgl39.mongodb.net:27017"
test: get_zipcode_data
	nosetests

prod_build:clean test build
	git tag -t 
	twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u jdrumgoole

test_build:test build
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

build:
	python setup.py sdist

clean:
	rm -rf dist bdist sdist mongodbshell.egg-info

get_zipcode_data:
	@if ! `./mongodbshell/demo_exists.py`; then\
		mongodump --host ${ATLAS_HOSTS} --ssl --username readonly --password readonly --authenticationDatabase admin --db demo --collection zipcodes;\
		mongorestore --drop;\
	fi

tox:
	tox

init:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole

