CLI
===

When you install the reference implementation, it creates a console script 
`pathsjson` with the following usage:

```
optional arguments:
  -h, --help           show this help message and exit
  --init               Create a .paths.json file in the cwd
  --init-globals       Create the global paths.json file
  --make-exports       Print exports for Makefile eval
  --print-global-path  Print global paths.json file path
  --shell-exports      Print exports for shell
```

You'll notice the reference to a global `path.json` file. This file lets 
you define user-level defaults. It's useful when you do contract work or 
group related projects onto one disk. For example, I may define a 
`CONTRACT-99` directory in the global `paths.json` file. Then, all my 
data goes onto a portable harddrive for that contract. 

The `--shell-exports` switch prints the resolved paths to the console with
with `export` and quoting. This lets you use the paths in your shell
session, via,

```sh
eval $(pathsjson --shell-exports)
```
