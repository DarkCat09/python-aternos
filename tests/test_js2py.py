import unittest

from python_aternos import atjsparse
from tests import files

CONV_TOKEN_ARROW = '''(() => {/*AJAX_TOKEN=123}*/window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})();'''
CONV_TOKEN_FUNC = '''(function(){window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})()'''


class TestJs2Py(unittest.TestCase):

    def setUp(self) -> None:

        self.tests = files.read_sample('token_input.txt')
        self.results = files.read_sample('token_output.txt')
        self.js = atjsparse.Js2PyInterpreter()

    def test_base64(self) -> None:

        encoded = 'QEhlbGxvIFdvcmxkIQ=='
        decoded = atjsparse.atob(encoded)
        self.assertEqual(decoded, '@Hello World!')

    def test_conv(self) -> None:

        token = CONV_TOKEN_ARROW
        f = self.js.to_ecma5(token)
        self.assertEqual(f, CONV_TOKEN_FUNC)

    def test_ecma6parse(self) -> None:

        code = '''
        window.t0 =
            window['document']&&
            !window[["p","Ma"].reverse().join('')]||
            !window[["ut","meo","i","etT","s"].reverse().join('')];'''

        part1 = '''window.t1 = Boolean(window['document']);'''
        part2 = '''window.t2 = Boolean(!window[["p","Ma"].reverse().join('')]);'''
        part3 = '''window.t3 = Boolean(!window[["ut","meo","i","etT","s"].reverse().join('')]);'''

        self.js.exec_js(code)
        self.js.exec_js(part1)
        self.js.exec_js(part2)
        self.js.exec_js(part3)

        self.assertEqual(self.js['t0'], False)
        self.assertEqual(self.js['t1'], True)
        self.assertEqual(self.js['t2'], False)
        self.assertEqual(self.js['t3'], False)

    def test_exec(self) -> None:

        for func, exp in zip(self.tests, self.results):
            self.js.exec_js(func)
            res = self.js['AJAX_TOKEN']
            self.assertEqual(res, exp)


if __name__ == '__main__':
    unittest.main()
