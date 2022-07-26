build:
	sudo python -m build

upload:
	python -m twine upload dist/*

clean:
	sudo rm -rf dist/ python_aternos.egg-info/
