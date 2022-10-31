"""Parsing and executing JavaScript code"""

import base64
import regex
import js2py

# Thanks to http://regex.inginf.units.it/
arrowexp = regex.compile(r'\w[^\}]*+')


def to_ecma5_function(f: str) -> str:
    """Converts a ECMA6 function
    to ECMA5 format (without arrow expressions)

    Args:
        f (str): ECMA6 function

    Returns:
        ECMA5 function
    """

    f = regex.sub(r'/\*.+?\*/', '', f)
    match = arrowexp.search(f)
    conv = '(function(){' + match.group(0) + '})()'
    return regex.sub(
        r'(?:s|\(s\)) => s.split\([\'"]{2}\).reverse\(\).join\([\'"]{2}\)',
        'function(s){return s.split(\'\').reverse().join(\'\')}',
        conv
    )


def atob(s: str) -> str:
    """Decodes base64 string

    Args:
        s (str): Encoded data

    Returns:
        Decoded string
    """

    return base64.standard_b64decode(str(s)).decode('utf-8')


def exec_js(f: str) -> js2py.EvalJs:
    """Executes a JavaScript function

    Args:
        f (str): ECMA6 function

    Returns:
        JavaScript interpreter context
    """

    ctx = js2py.EvalJs({'atob': atob})
    ctx.execute('window.document = { };')
    ctx.execute('window.Map = function(_i){ };')
    ctx.execute('window.setTimeout = function(_f,_t){ };')
    ctx.execute('window.setInterval = function(_f,_t){ };')
    ctx.execute('window.encodeURIComponent = function(_s){ };')
    ctx.execute(to_ecma5_function(f))
    return ctx
