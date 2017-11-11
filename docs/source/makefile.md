Using with `Makefile`s
======================

The `pathsjson` cli lets you export a file that your `Makefile` can `include`.
I'm sure there is a better way to do this -- and, if you know it, please 
open a PR! -- but the following allows you use `.paths.json` variables as
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

I'd prefer a solution that just included the output of the cli call so it's
always fresh and you don't need to liter your directory with build artifacts.
But, the few I tried didn't work well. I also want to figue out how to ignore
some variables on `zsh` Makefile completion.
