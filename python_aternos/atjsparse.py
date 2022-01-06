import re
import js2py
import base64

brkregex = re.compile(r'\((?!\)|[\'\"])(.+?)(?<!\(|[\'\"])\)')

def parse_brackets(f):
	return brkregex.search(f)[1]

def to_ecma5_function(f):
	fnstart = f.find('{')+1
	fnend = f.rfind('}')
	f = arrow_conv(f[fnstart:fnend])
	return f

def atob(s):
	return base64.standard_b64decode(str(s)).decode('utf-8')

def arrow_conv(f):
	if '=>' in f:
		inner = parse_brackets(f)
		while brkregex.match(inner) != None:
			inner = parse_brackets(inner)

		func = re.sub(
			r'(\w+)\s*=>\s*(.+)',
			r'function(\1){return \2}', inner
		)
		start = f.find(inner)
		end = start + len(inner)
		f = f[:start] + func + f[end:]
	return f

def exec(f):
	ctx = js2py.EvalJs({'atob': atob})
	ctx.execute(to_ecma5_function(f))
	return ctx
