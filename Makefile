test:
	python setup.py test

prod_build:clean test build
	twine upload --verbose --repository-url https://upload.pypi.org/legacy/ dist/* -u jdrumgoole

test_build:test build
	twine upload --verbose --repository-url https://test.pypi.org/legacy/ dist/* -u jdrumgoole

build:
	python setup.py sdist

clean:
	rm -rf dist bdist sdist mongodbshell.egg-info

test_data:
	(cd data;sh restore.sh)

init:
	keyring set https://test.pypi.org/legacy/ jdrumgoole
	keyring set https://upload.pypi.org/legacy/ jdrumgoole

