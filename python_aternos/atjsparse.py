"""Parsing and executing JavaScript code"""

import base64

from typing import Any

import regex
import js2py

# Thanks to http://regex.inginf.units.it/
arrowexp = regex.compile(r'\w[^\}]*+')


def to_ecma5_function(f: str) -> str:

    """Converts a ECMA6 function to ECMA5 format (without arrow expressions)

    :param f: ECMA6 function
    :type f: str
    :return: ECMA5 function
    :rtype: str
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

    :param s: Encoded data
    :type s: str
    :return: Decoded string
    :rtype: str
    """

    return base64.standard_b64decode(str(s)).decode('utf-8')


def exec_js(f: str) -> Any:

    """Executes a JavaScript function

    :param f: ECMA6 function
    :type f: str
    :return: JavaScript interpreter context
    :rtype: Any
    """

    ctx = js2py.EvalJs({'atob': atob})
    ctx.execute('window.document = { };')
    ctx.execute('window.Map = function(_i){ };')
    ctx.execute('window.setTimeout = function(_f,_t){ };')
    ctx.execute('window.setInterval = function(_f,_t){ };')
    ctx.execute('window.encodeURIComponent = function(_s){ };')
    ctx.execute(to_ecma5_function(f))
    return ctx
