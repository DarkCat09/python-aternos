import re
import base64
import js2py
from typing import Optional, Union, List, Any

# regexr.com/6el10
arrowexp = re.compile(r'(\(?(\w+(?:,\s*\w+)*)\)?|\(\))\s*=>\s*(({\s*.+\s*})|(.+;|.+$))')

# Thanks to https://stackoverflow.com/a/1651562/17901968
def brackets(s:str, search:Optional[str]=None) -> List[Union[int]]:
	result = []
	content = [s]
	repeated = False
	for expr in content:
		if expr.find('(') == -1: continue
		count = -1
		indexes = []
		cont = False
		for i, ch in enumerate(expr):
			if ch == '(':
				indexes.append(i)
				if count == -1:
					count = 1
				else:
					count += 1
			if ch == ')':
				if len(indexes) > 1:
					indexes.pop()
				else:
					indexes.append(i)
					if expr.find('(', i) != -1:
						cont = True
				count -= 1
			if count == 0: break
		if count != 0:
			raise ValueError('Unmatched parenthesis')
		else:
			inner = expr[indexes[0]+1:indexes[1]]
			if repeated:
				content.pop()
				repeated = False
			content.append(inner)
			if search == None \
			or search in inner:
				result.append(indexes)
			if cont:
				content.append(content[len(content)-2])
				repeated = True
	return result

def to_ecma5_function(f:str) -> str:
	pass

def atob(s):
	return base64.standard_b64decode(str(s)).decode('utf-8')

def exec(f:str) -> Any:
	ctx = js2py.EvalJs({'atob': atob})
	ctx.execute(to_ecma5_function(f))
	return ctx
