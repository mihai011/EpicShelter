# build package 
python -m build
# upload package
python -m twine upload --repository testpypi dist/* --verbose