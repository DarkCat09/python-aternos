#!/usr/bin/env python3
import re
import base64
import js2py

# Emulate 'atob' function
# print(base64.standard_b64decode('MmlYaDVXNXVFWXE1ZldKSWF6UTY='))

# Test cases
# tests = [
#     """(() => {window[("A" + "J" + "AX_T" + "OKE" + "N")]=("2iXh5W5u" + "EYq" + "5fWJIa" + "zQ6");})();""",
#     """(() => {window[["N","TOKE","AJAX_"].reverse().join('')]=["IazQ6","fWJ","h5W5uEYq5","2iX"].reverse().join('');})();""",
#     """(() => {window["AJAX_TOKEN"] = atob("SGVsbG8sIHdvcmxk")})();""",
#     """(() => {window[atob('QUpBWF9UT0tFTg==')]=atob('MmlYaDVXNXVFWXE1ZldKSWF6UTY=');})();""",
#     """(() => {window["AJAX_TOKEN"] = "1234" })();""",
#     """(() => {window[atob('QUpBWF9UT0tFTg==')]="2iXh5W5uEYq5fWJIazQ6";})();""",
# ]

# Use tests from a file
tests = []
with open('../token.txt', 'rt') as f:
	lines = re.split(r'[\r\n]', f.read())
	del lines[len(lines)-1] # Remove empty string
	tests = lines

brkregex = re.compile(r'\((?!\)|[\'\"])(.+?)(?<!\(|[\'\"])\)')

def parse_brackets(f):
	return brkregex.search(f)[1]

def to_ecma5_function(f):
	# return "(function() { " + f[f.index("{")+1 : f.index("}")] + "})();"
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

ctx = js2py.EvalJs({'atob': atob})

for f in tests:
	try:
		c = to_ecma5_function(f)
		ctx.execute(c)
		print(ctx.window['AJAX_TOKEN'])
	except Exception as e:
		print(c, '\n', e)

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
# (Note: The last three 
# tokens are different)
