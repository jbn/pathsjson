Tips
====

Naming Schemes
--------------

I tend to use CAPITAL_CASE for all the pathsjson definitions. In you code, 
they should look like constants. Or, at least, they should act as constants 
in you code, and you outsource changes to the paths.json file. This also has 
the added bonus of making `grep` or `sed` tasks easier. And, for an added,
added bonus -- it's perceptually noticable as "non literal", giving 
something akin to syntax highlighting without writing the highlighter
definitions.

Environmental Overriding
------------------------

The `paths.automagic` module does will override `.paths.json` definitions.
This lets you call your script as,

```sh
VERSION=tmp bin/extract.py
```
