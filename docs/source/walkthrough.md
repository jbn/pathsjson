# Quick Start

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

The `__ENV` object is a special scope. It contains a simple mapping from key to
string value that acts like a set of constants. In this example, I defined a 
`VERSION` string that I'll use in the paths. You access the `__ENV` variables
by prefixing a name with `$$`.

The first path definition in this example is the `data_dir`. This one is 
common. The first element in that path is a special constant variable 
reference, `$$_IMPLICIT_ROOT`. For example, if you used the code,

```python
from pathsjson.automagic import PATHS
```
from a file running with the `$PWD` of `/tweets_research/tests`, `pathsjson` will ascend the directory structure towards the root until it finds a `.paths.json`. (Think: like `git`). When it finds that file, the parent directory becomes the `$$_IMPLICIT_ROOT`. This is usually how we think about projects. So, in this case, it would be `/tweets_research`.

The next three paths establish (again, common) directories for storing raw, clean, and log data. They all reference the `$data_dir` path in their construction. By now the use of arrays of path elements should be clear: it doesn't matter what operation system you're on. It's the responsibility of `pathsjson` to resolve it portably.

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

