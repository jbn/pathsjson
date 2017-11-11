---
title: pathsjson
image: assets/pathsjson_card_image.png
---

# PATHSJSON

## Why is this?

My etl/data analysis scripts are littered with code like,

```python
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
```

It's fine for one file, but when you have a whole ELT pipeline tucked
into a `Makefile`, the duplication leads to fragility and violates DRY.
It's a **REALLY** common pattern in file-based processing. This package
and format lets you do create a `paths.json` file like,

```json
{
    "DATA_DIR": ["data"],
    "CLEAN_DIR": ["$DATA_DIR", "clean"],
    "RAW_DIR": ["$DATA_DIR", "raw"],
    "SOMETHING_HTML": ["$RAW_DIR", "something.html"],
    "SOMETHING_CSV": ["$RAW_DIR", "something.csv"]
}
```

Then, from your python script,

```python
from pathsjson.automagic import PATHS

with open(PATHS['SOMETHING_HTML']) as fp:
    csv = process(fp)

with open(PATHS['SOMETHING_CSV']) as fp:
    write_csv(fp)
```

## How does it work?

Say you are creating an ETL project that analyzes some tweets in the
directory `/tweet_research`. First you should create a `.paths.json` file. 
(If you are using the reference implementation, execute `pathsjson --init`
from your shell.) Next, imagine you filled in the file as,

```json
{
    "__ENV": {
        "VERSION": "0.0.1"
    },
    "data_dir": ["$$_IMPLICIT_ROOT", "data"],
    "raw_dir": ["$data_dir", "raw"],
    "log_dir": ["$data_dir", "logs"],
    "clean_dir": ["$data_dir", "clean"],
    
    "twitter_errors": ["$log_dir", "$$VERSION", "twitter.log"],
    "tweets": ["$raw_dir", "$$VERSION", "tweets.jsonl"],
    "extract": ["$clean_dir", "$$VERSION", "extract.jsonl"]
}
```

The `__ENV` object is special. It contains a simple mapping from key to 
string value that acts like a set of constants. In this example, I defined a 
`VERSION` string that I'll use in the paths.

The first path is the `data_dir`. This one is common. The first element in that path is a special constant variable reference, `$$_IMPLICIT_ROOT`. For example, if you used the code,

```python
from pathsjson.automagic import PATHS
```
from a file running with the `$PWD` of `/tweets_research/tests`, `pathsjson` will ascend the directory structure towards the root until it finds a `.paths.json`. (Think, like `git`). When it finds that file, the parent directory becomes the `$$_IMPLICIT_ROOT`. This is usually how we think about projects. So, in this case, it would be `/tweets_research`.

The next three paths establish (again, common) directories for storing raw, clean, and log data. They all reference the `$data_dir` path in their construction. By now the use of arrays of path elements should be clear: it doesn't matter what operation system your on. It's the responsibility of `pathsjson` to resolve it portably.

Now, look at the `twitter_errors` path. This references both the `$log_dir` path and the `$$VERSION` variable. This way, when you change the version, your directory paths will adjust automatically, but you can keep the old data. (Useful to prevent those, "OH SHIT!" moments.)

If you're using the reference implementation in python, your code to write to the logs may look like,

```python
with PATHS.resolve('twitter_errors').open("w") as fp:
    fp.write("cool")
```

This will automatically create the necessary directories (like `mkdir -p`) and then open the file for writing. If you want to debug, you can do something like, 

```python
with PATHS.resolve('twitter_errors', VERSION='debug').open("w") as fp:
    fp.write("cool")
```

## Useful commands in the reference implementation

When you install the reference implementation, it creates a console script 
`pathsjson` with the following usage:

```
usage: pathsjson [-h] [--print-global-path] [--shell-exports] [--make-exports]
                 [--init-globals] [--init]

optional arguments:
  -h, --help           show this help message and exit
  --print-global-path  Print global paths.json file path
  --shell-exports      Print exports for shell
  --make-exports       Print exports for Makefile eval
  --init-globals       Create the global paths.json file
  --init               Create a .paths.json file in the cwd
```

You'll notice the reference to a global `path.json` file. This file lets 
you define user-level defaults. It's useful when you do contract work or 
group related projects onto one disk. For example, I may define a 
`CONTRACT-99` directory in the global `paths.json` file. Then, all my 
data goes onto a portable harddrive for that contract. 

## Using with `Makefile`s

The `pathsjson` cli lets you export a file that your `Makefile` can `include`.
I'm sure there is a better way to do this -- and, if you know it, please 
open a PR! -- but the following allows you use `paths.json` variables as
variables in you `Makefile`.

```Makefile
include paths.mk

all: paths.mk target1 target2

###############################################################################
# This is a hack, but for now it's the best solution. If the paths.mk file
# needs a rebuild, the prior inclusion is wrong. The targets may depend on 
# paths which have changed. This builds it, then errs. On the next invocation, 
# it will run correctly.
###############################################################################

paths.mk: .paths.json
        pathsjson --make-exports > paths.mk
        @echo "paths.mk REBUILT\n\nRERUN MAKEFILE"
        exit 1

target1:
    bin/python load_data.py $(VARIABLE_IN_PATHSJSON)
```

(I'd prefer a solution that just included the output of the cli call so it's
always fresh and you don't need to liter your directory with build artifacts.
But, the few I tried didn't work well. I also want to figue out how to ignore
some variables on zsh Makefile completion.)

## Validation

There is a `.paths.json` 
[schema](http://pathsjson.falsifiable.com/schema.json#). 
It's validated with [JSON-Schema](http://json-schema.org/).

## Conventions

- I tend to use CAPITAL_CASE for all the pathsjson definitions. In you code, 
  they should look like constants. Or, at least, they should act as constants 
  in you code, and you outsource changes to the paths.json file. This also has 
  the added bonus of making `grep` or `sed` tasks easier. And, for an added,
  added bonus -- it's perceptually noticable as "non literal", giving 
  something akin to syntax highlighting without writing the highlighter
  definitions.

## Implementations

The [reference implementation](https://github.com/jbn/pathsjson) is in python.
Install it via, 

```sh
pip install pathsjson
```

However, I ***hope*** programmers who find it useful will implement it in 
their favorite languages. It's not a complicated package, and I purposely made
the implementation simple and readable. If you write your own implementation,
please feel free to add it to the list below.

- [pathsjson](https://github.com/jbn/pathsjson) (python)
