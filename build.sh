#!/usr/bin/env sh
set -eu

# Clean stale auxiliary files before a full reproducible build.
find . -name '*.aux' -type f -delete
rm -f main.bbl main.bcf main.blg main.fdb_latexmk main.fls main.lof main.log \
      main.lol main.lot main.out main.run.xml main.synctex.gz main.toc main.xdv main.pdf

xelatex -interaction=nonstopmode -halt-on-error main.tex
biber main
xelatex -interaction=nonstopmode -halt-on-error main.tex
xelatex -interaction=nonstopmode -halt-on-error main.tex

printf '\nBuild completed successfully: main.pdf\n'
