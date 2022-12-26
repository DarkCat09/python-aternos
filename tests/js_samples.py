#!/usr/bin/env python3

#           How to use
# *******************************
# 1. Open DevTools at aternos.org
# 2. Get AJAX_TOKEN variable value (without quotes)
#
# 3. Pass it to this script as an argument, e.g.:
#    python3 js_samples.py xKflIsKHxlv96fLc1tht
#
# 4. The script will request the token 100 times
#    and check it with different built-in interpreters
#    (now there are only js2py and nodejs)
# 5. Array "errored" which is printed at the end
#    contains indexes of incorrectly executed JS functions
# 6. Enter this index in the opened console
#    or enter "exit" to exit

import re
import sys

from python_aternos import AternosConnect
from python_aternos import Js2PyInterpreter
from python_aternos import NodeInterpreter

TIMES = 100

js = re.compile(r'\(\(\).*?\)\(\);')
conn = AternosConnect()
jsi1 = Js2PyInterpreter()
jsi2 = NodeInterpreter()

token = sys.argv[1]

samples = []
errored = []


def get_code() -> bool:

    r = conn.request_cloudflare(
        'https://aternos.org/go', 'GET'
    )
    if r.status_code != 200:
        print(r.status_code)

    code = js.search(r.text)
    if code is None:
        print('No match!')
        return False

    sample = code.group(0)
    samples.append(sample)

    print(sample)
    print('***')

    jsi1.exec_js(sample)
    jsi2.exec_js(sample)
    var1 = jsi1['AJAX_TOKEN']
    var2 = jsi2['AJAX_TOKEN']

    print(var1)
    print(var2)
    print('***')
    print()
    print()

    return var1 == var2 == token


def main() -> None:

    print()

    for i in range(TIMES):
        print(i)
        if not get_code():
            errored.append(i)

    print('Errored:', errored)

    print('Choose sample number:')
    while True:
        try:
            print('>', end=' ')
            cmd = input()
            if cmd.strip().lower() in ('exit', 'quit'):
                print('Quit')
                break
            print(samples[int(cmd)])
        except KeyboardInterrupt:
            print()
            print('Quit')
            break
        except Exception as err:
            print(err)


if __name__ == '__main__':
    main()
