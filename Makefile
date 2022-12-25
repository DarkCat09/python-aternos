build:
	python3 -m build

upload:
	python3 -m twine upload dist/*

clean:
	rm -rf dist python_aternos.egg-info
	rm -rf python_aternos/__pycache__
	rm -rf examples/__pycache__
	rm -rf tests/__pycache__
	rm -rf site .mypy_cache

test:
	python3 -m unittest discover -v ./tests

check:
	python3 -m mypy .
	python3 -m pylint ./python_aternos

fullcheck:
	chmod +x check.sh; bash check.sh

format:
	python3 -m autopep8 -r --in-place .
