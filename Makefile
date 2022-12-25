build:
	python -m build

upload:
	python -m twine upload dist/*

clean:
	rm -rf dist python_aternos.egg-info
	rm -rf python_aternos/__pycache__
	rm -rf examples/__pycache__
	rm -rf tests/__pycache__
	rm -rf site .mypy_cache

test:
	python -m unittest discover -v ./tests

check:
	python -m mypy .
	python -m pylint ./python_aternos

fullcheck:
	chmod +x check.sh; bash check.sh

format:
	python -m autopep8 -r --in-place .
