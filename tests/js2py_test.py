import re
import unittest

from python_aternos import atjsparse

class TestJs2Py(unittest.TestCase):

	def setUp(self) -> None:

		self.tests = []
		with open('../token.txt', 'rt') as f:
			lines = re.split(r'[\r\n]', f.read())
			del lines[len(lines)-1] # Remove empty string
			self.tests = lines
		
		self.results = [
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2rKOA1IFdBcHhEM616cb'
			'2iXh5W5uEYq5fWJIazQ6'
			'CuUcmZ27Fb8bVBNw12Vj'
			'YPPe8Ph7vzYaZ9PF9oQP'
			'UfLlemvKEE16ltk0hZNM'
			'q6pYdP6r7xiVHhbotvlN'
			'q6pYdP6r7xiVHhbotvlN'
			'XAIbksgkVX9JYboMDI7D'
		]
	
	def test_base64(self) -> None:

		encoded = 'QEhlbGxvIFdvcmxkIQ=='
		decoded = atjsparse.atob(encoded)
		self.assertEqual(decoded, '@Hello World!')
	
	def test_conv(self) -> None:

		token = '(() => {window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})();'
		f = atjsparse.to_ecma5_function(token)
		self.assertEqual(f, '(function(){window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})()')
	
	def test_exec(self) -> None:

		for i, f in enumerate(self.tests):
			ctx = atjsparse.exec(f)
			res = ctx.window['AJAX_TOKEN']
			self.assertEqual(res, self.results[i])
	
	def tearDown(self) -> None:
		del self.tests
		del self.results
