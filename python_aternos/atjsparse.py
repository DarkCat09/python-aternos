import regex
import base64
import js2py
from typing import Any

# Thanks to http://regex.inginf.units.it/
arrowexp = regex.compile(r'\w[^\}]*+')

def to_ecma5_function(f:str) -> str:
	match = arrowexp.search(f)
	conv = '(function(){' + match.group(0) + '})()'
	return regex.sub(
		r'(?:s|\(s\)) => s.split\([\'"]{2}\).reverse\(\).join\([\'"]{2}\)',
		'function(s){return s.split(\'\').reverse().join(\'\')}',
		conv
	)

def atob(s:str) -> str:
	return base64.standard_b64decode(str(s)).decode('utf-8')

def exec(f:str) -> Any:
	ctx = js2py.EvalJs({'atob': atob})
	ctx.execute('window.document = { };')
	ctx.execute('window.Map = function(_i){ };')
	ctx.execute('window.setTimeout = function(_f,_t){ };')
	ctx.execute('window.setInterval = function(_f,_t){ };')
	ctx.execute('window.encodeURIComponent = function(_s){ };')
	ctx.execute(to_ecma5_function(f))
	return ctx
