#!/usr/bin/env python3
import base64
import js2py

# Emulate 'atob' function
#print(base64.standard_b64decode('MmlYaDVXNXVFWXE1ZldKSWF6UTY='))

# Test cases
tests = [
    """(() => {window[("A" + "J" + "AX_T" + "OKE" + "N")]=("2iXh5W5u" + "EYq" + "5fWJIa" + "zQ6");})();""",
    """ (() => {window[["N","TOKE","AJAX_"].reverse().join('')]=["IazQ6","fWJ","h5W5uEYq5","2iX"].reverse().join('');})();""",
    """(() => {window["AJAX_TOKEN"] = atob("SGVsbG8sIHdvcmxk")})();""",
    """(() => {window[atob('QUpBWF9UT0tFTg==')]=atob('MmlYaDVXNXVFWXE1ZldKSWF6UTY=');})();""",
    """(() => {window["AJAX_TOKEN"] = "1234" })();""",
    """(() => {window[atob('QUpBWF9UT0tFTg==')]="2iXh5W5uEYq5fWJIazQ6";})();""",
]

# Array function to ECMAScript 5.1
def code(f):
    return "(function() { " + f[f.index("{")+1 : f.index("}")] + "})();"

# Emulation atob V8
def atob(arg):
    return base64.standard_b64decode(str(arg)).decode("utf-8")

presettings = """
let window = {};
"""

ctx = js2py.EvalJs({ 'atob': atob })

'''
ctx.execute(presettings + code(tests[3]))
print(ctx.window)
'''

for f in tests:
    try:
        c = code(f)
        ctx.execute(presettings + c)
        print(ctx.window['AJAX_TOKEN'])
    except Exception as e:
        print(c, '\n', e)

