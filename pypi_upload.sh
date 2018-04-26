#!/bin/bash
pip install pandoc twine wheel
pandoc --from=markdown --to=rst --output=README README.md
python setup.py bdist_wheel --universal
twine upload --repository-url https://test.pypi.org/legacy/ dist/*