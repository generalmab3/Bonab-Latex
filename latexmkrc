# Compile the project with XeLaTeX. latexmk detects biblatex and runs Biber.
$pdf_mode = 5;
$xelatex = 'xelatex -interaction=nonstopmode -file-line-error -synctex=1 %O %S';
$bibtex = 'biber %O %B';
$clean_ext .= ' %R.bbl %R.bcf %R.blg %R.run.xml %R.synctex.gz %R.lol';
