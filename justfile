set shell := ["powershell.exe", "-c"]
set windows-shell := ["powershell.exe", "-c"]

# build library docs and open them in the browser to view
[working-directory: 'docs']
docs:
  make html
  _build/index.html

