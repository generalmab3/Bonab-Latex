@echo off
setlocal

rem Clean old auxiliary files so stale references cannot enter the PDF.
for /r %%F in (*.aux) do @del /q "%%F" >nul 2>&1
del /q main.bbl main.bcf main.blg main.fdb_latexmk main.fls main.lof main.log main.lol main.lot main.out main.run.xml main.synctex.gz main.toc main.xdv main.pdf >nul 2>&1

echo [1/4] Running XeLaTeX...
call xelatex -interaction=nonstopmode -halt-on-error main.tex || goto :error

echo [2/4] Running Biber...
call biber main || goto :error

echo [3/4] Running XeLaTeX...
call xelatex -interaction=nonstopmode -halt-on-error main.tex || goto :error

echo [4/4] Running XeLaTeX...
call xelatex -interaction=nonstopmode -halt-on-error main.tex || goto :error

echo.
echo Build completed successfully: main.pdf
exit /b 0

:error
echo.
echo Build failed. Read the error messages above.
pause
exit /b 1
