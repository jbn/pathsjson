.. image:: https://travis-ci.org/jbn/pathsjson.svg?branch=master
    :target: https://travis-ci.org/jbn/pathsjson
.. image:: https://ci.appveyor.com/api/projects/status/xre5b722qk6ckqaf?svg=true
    :target: https://ci.appveyor.com/project/jbn/pathsjson/branch/master
.. image:: https://coveralls.io/repos/github/jbn/pathsjson/badge.svg?branch=master
    :target: https://coveralls.io/github/jbn/pathsjson?branch=master 
.. image:: https://img.shields.io/pypi/v/pathsjson.svg
    :target: https://pypi.python.org/pypi/pathsjson
.. image:: https://img.shields.io/badge/license-MIT-blue.svg
    :target: https://raw.githubusercontent.com/jbn/pathsjson/master/LICENSE
.. image:: https://img.shields.io/pypi/pyversions/pathsjson.svg
    :target: https://pypi.python.org/pypi/pathsjson


What is this?
=============

A JSON-based format for describing paths in your project.

Why is this?
------------

My etl/data analysis scripts are littered with code like,

.. code:: python

    import os

    DATA_DIR = "data"
    CLEAN_DIR = os.path.join(DATA_DIR, "clean")
    RAW_DIR = os.path.join(DATA_DIR, "raw")
    TARGET_HTML = os.path.join(RAW_DIR, "something.html")
    OUTPUT_FILE = os.path.join(CLEAN_DIR, "something.csv")

    with open(TARGET_HTML) as fp:
        csv = process(fp)

    with open(OUTPUT_FILE) as fp:
        write_csv(fp)

It's fine for one file, but when you have a whole ELT pipeline tucked
into a ``Makefile``, the duplication leads to fragility and violates
DRY. It's a **REALLY** common pattern in file-based processing. This
package and format lets you do create a ``paths.json`` file like,

.. code:: json

    {
        "DATA_DIR": ["data"],
        "CLEAN_DIR": ["$DATA_DIR", "clean"],
        "RAW_DIR": ["$DATA_DIR", "raw"],
        "SOMETHING_HTML": ["$RAW_DIR", "something.html"],
        "SOMETHING_CSV": ["$RAW_DIR", "something.csv"]
    }

Then, from your python script,

.. code:: python

    from pathsjson.automagic import PATHS

    with open(PATHS['SOMETHING_HTML']) as fp:
        csv = process(fp)

    with open(PATHS['SOMETHING_CSV']) as fp:
        write_csv(fp)

Installation
------------
.. code:: bash

    pip install pathsjson

More details
------------

Read the docs: `here <http://pathsjson.falsifiable.com>`_.
