#######

.. image:: https://travis-ci.org/bootandy/imps.png?branch=master
    :target: https://travis-ci.org/bootandy/imps
    :alt: Build Status


To Install:
===========
python setup.py install


Why?
====

It sorts your imports and is designed to work with this
`flake8-import-order plugin <https://github.com/PyCQA/flake8-import-order>`
It differs from `Isort <https://github.com/timothycrosley/isort>` as it is more opinionated and
does not require config as it works out what to do by reading your setup.cfg


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
Mostly.


To Run Tox locally:
===================
Tests:
tox -e tests
Flake8:
tox -e flake8
