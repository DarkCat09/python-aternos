failed=()

title () {

	RESET='\033[0m'
	COLOR='\033[1;36m'

	echo
	echo -e "$COLOR[#] $1$RESET"
}

error_msg () {

	RESET='\033[0m'
	OK='\033[1;32m'
	ERR='\033[1;31m'

	if (( $1 )); then
	failed+=$2
	echo -e "$ERR[X] Found errors$RESET"
	else
	echo -e "$OK[V] Passed successfully$RESET"
	fi
}

display_failed() {

	RESET='\033[0m'
	FAILED='\033[1;33m'
	SUCCESS='\033[1;32m'

	local IFS=', '
	if [[ ${#failed[@]} > 0 ]]; then
	echo -e "$FAILED[!] View output for: ${failed[*]}$RESET"
	else
	echo -e "$SUCCESS[V] All tests are passed successfully$RESET"
	fi
}

title 'Checking needed modules...'
pip install pycodestyle mypy pylint

title 'Running unit tests...'
python -m unittest discover -v ./tests
error_msg $? 'unittest'

title 'Running pep8 checker...'
python -m pycodestyle .
error_msg $? 'pep8'

title 'Running mypy checker...'
python -m mypy .
error_msg $? 'mypy'

title 'Running pylint checker...'
python -m pylint ./python_aternos
error_msg $? 'pylint'

display_failed
echo
