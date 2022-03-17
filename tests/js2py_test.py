import re
from python_aternos import atjsparse

# Use tests from a file
tests = []
with open('../token.txt', 'rt') as f:
	lines = re.split(r'[\r\n]', f.read())
	del lines[len(lines)-1] # Remove empty string
	tests = lines

for f in tests:
	ctx = atjsparse.exec(f)
	print(ctx.window['AJAX_TOKEN'])

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
# UfLlemvKEE16ltk0hZNM
# q6pYdP6r7xiVHhbotvlN
# q6pYdP6r7xiVHhbotvlN
# XAIbksgkVX9JYboMDI7D
