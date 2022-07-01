title () {
	echo
	echo "***"
	echo "$1"
	echo "***"
	echo
}

title 'Checking needed modules...'
pip install pycodestyle mypy pylint

title 'Running unit tests...'
python -m unittest discover -v ./tests

title 'Running pep8 checker...'
python -m pycodestyle .

title 'Running mypy checker...'
python -m mypy .
