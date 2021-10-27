#!/usr/bin/env python3

from py_mini_racer import MiniRacer
import base64

# Set function for manage global vars
presettings = """
let window = {1: null, 2: null, AJAX_TOKEN: null};
let i = 1;
function __log() { return {win_var: window["AJAX_TOKEN"], 1: window[1], 2: window[2]} };
function atob(arg) {window[i++] = arg;};
"""

# Test cases
tests = [
    """(() => {window[("A" + "J" + "AX_T" + "OKE" + "N")]=("2iXh5W5u" + "EYq" + "5fWJIa" + "zQ6");})();""",
    """ (() => {window[["N","TOKE","AJAX_"].reverse().join('')]=["IazQ6","fWJ","h5W5uEYq5","2iX"].reverse().join('');})();""",
    """(() => {window["AJAX_TOKEN"] = atob("SGVsbG8sIHdvcmxk")})();""",
    """(() => {window[atob('QUpBWF9UT0tFTg==')]=atob('MmlYaDVXNXVFWXE1ZldKSWF6UTY=');})();""",
    """(() => {window["AJAX_TOKEN"] = "1234" })();""",
    """(() => {window[atob('QUpBWF9UT0tFTg==')]="2iXh5W5uEYq5fWJIazQ6";})();""",
]

# Emulate 'atob' function
#print(base64.standard_b64decode('MmlYaDVXNXVFWXE1ZldKSWF6UTY='))

for js in tests:
    ctx = MiniRacer()
    result = ctx.eval(presettings + js)
    result = ctx.call('__log')

    print(result)
    '''
    if 'win_var' in result and result['win_var']:
        result = result['win_var']
    elif '1' in result and ('2' in result and not result['2']):
        result = base64.standard_b64decode(result['1'])
    else:
        result = base64.standard_b64decode(result['2'])
    '''
    print('Case:\n', js, '\n')
    print('Result: \n', result, '\n')
    print('-' * 30, '\n')
    

