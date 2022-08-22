build:
	python -m build

upload:
	python -m twine upload dist/*

clean:
	rm -rf dist/ python_aternos.egg-info/
	rm -rf .mypy_cache/ python_aternos/__pycache__/

check:
	chmod +x test.sh
	bash test.sh
