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

A JSON-based DSL for describing paths in your project.

Why is this?
~~~~~~~~~~~~

My etl/data analysis projects are littered with code like,

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
package and format lets you do create a ``.paths.json`` file like,

.. code:: json

    {
        "__ENV": {"VERSION": "0.0.1"},
        "DATA_DIR": ["data", "$$VERSION"],
        "CLEAN_DIR": ["$DATA_DIR", "clean"],
        "RAW_DIR": ["$DATA_DIR", "raw"],
        "SOMETHING_HTML": ["$RAW_DIR", "something.html"],
        "SOMETHING_CSV": ["$RAW_DIR", "something.csv"]
    }

Then, from your python scripts,

.. code:: python

    from pathsjson.automagic import PATHS

    print("Processing:", PATHS['SOMETHING_HTML'])
    with PATHS.resolve('SOMETHING_HTML').open() as fp:
        csv = process(fp)

    with PATHS.resolve('SOMETHING_CSV').open("w") as fp:
        write_csv(fp)

Installation
------------
.. code:: bash

    pip install pathsjson


Validation
----------

There is a ``.paths.json`` 
`schema <http://pathsjson.falsifiable.com/schema.json#>`_. 
It's validated with `JSON-Schema <http://json-schema.org/>`_.

More details
------------

Read the docs: `here <http://pathsjson.falsifiable.com>`_.
