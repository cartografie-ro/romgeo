rm -rf dist build *.egg-info
python -m build
twine check dist/*
twine upload --repository testpypi dist/*