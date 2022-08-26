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

check:
	chmod +x test.sh
	bash test.sh
