#######

.. image:: https://travis-ci.org/bootandy/imps.png?branch=master
    :target: https://travis-ci.org/bootandy/imps
    :alt: Build Status


To Install:
===========
python setup.py install


Usage:
======
imps <file_name or path>

imps <file_name or path> - s style

where style is smarkets / crypto / google


To Run Tests:
=============
pytest

Note if you run tests in Pycharm: Specify test as type: py.test

Is it ready:
============
Nope, Still work in progress


To Run Tox locally:
===================
Tests:
tox -e tests
Flake8:
tox -e flake8
