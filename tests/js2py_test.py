#!/usr/bin/env python3
import re
import base64
import js2py

# Use tests from a file
tests = []
with open('../token.txt', 'rt') as f:
	lines = re.split(r'[\r\n]', f.read())
	del lines[len(lines)-1] # Remove empty string
	tests = lines

arrowre = re.compile(r'(\w+?|\(\w+?(?:,\s*\w+?)*\)|\(\))\s*=>\s*({\s*[\s\S]+\s*}|[^\r\n]+?(?:;|$))')

def to_ecma5_function(f):
	# return "(function() { " + f[f.index("{")+1 : f.index("}")] + "})();"
	fnstart = f.find('{')+1
	fnend = f.rfind('}')
	f = arrow_conv(f[fnstart:fnend])
	return f

def atob(s):
	return base64.standard_b64decode(str(s)).decode('utf-8')

def arrow_conv(f):
	m = arrowre.search(f)
	while m != None:
		print(f)
		params = m.group(1).strip('()')
		body = m.group(2)
		if body.startswith('{')\
		and body.endswith('}'):
			body = body.strip('{}')
		else:
			body = f'return {body}'
		f = arrowre.sub(f'function({params}){{{body}}}', f)
		m = arrowre.search(f)
		print(f)
	#print('function(' + m.group(1).strip("()") + '){return ' + m.group(2) + ';}')
	return f

ctx = js2py.EvalJs({'atob': atob})

for f in tests:
	c = to_ecma5_function(f)
	ctx.execute(c)
	print(ctx.window['AJAX_TOKEN'])

# Expected output:
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2rKOA1IFdBcHhEM616cb
# 2iXh5W5uEYq5fWJIazQ6
# CuUcmZ27Fb8bVBNw12Vj
# YPPe8Ph7vzYaZ9PF9oQP
# ...
# (Note: The last four 
# tokens are different)
