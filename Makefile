.PHONY: all guide clean

all:
	latexmk -xelatex main.tex

guide:
	cd manual && latexmk -xelatex guide.tex
	cp manual/guide.pdf USER-GUIDE.pdf

clean:
	latexmk -C
	cd manual && latexmk -C guide.tex
