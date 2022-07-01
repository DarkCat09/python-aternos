import os
import re
import unittest

from python_aternos import atjsparse

CONV_TOKEN_ARROW = '''(() => {window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})();'''
CONV_TOKEN_FUNC = '(function(){window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})()'


class TestJs2Py(unittest.TestCase):

    def setUp(self) -> None:

        self.path = os.path.abspath(os.path.dirname(__file__))
        self.samples = os.path.join(self.path, 'samples')
        self.input = os.path.join(self.samples, 'token_input.txt')
        self.output = os.path.join(self.samples, 'token_output.txt')

        self.tests = []
        with open(self.input, 'rt') as f:
            lines = re.split(r'[\r\n]', f.read())
            del lines[-1]  # remove empty line at the end
            self.tests = lines

        self.results = []
        with open(self.output, 'rt') as f:
            lines = re.split(r'[\r\n]', f.read())
            del lines[-1]  # remove empty line at the end
            self.results = lines

    def test_base64(self) -> None:

        encoded = 'QEhlbGxvIFdvcmxkIQ=='
        decoded = atjsparse.atob(encoded)
        self.assertEqual(decoded, '@Hello World!')

    def test_conv(self) -> None:

        token = CONV_TOKEN_ARROW
        f = atjsparse.to_ecma5_function(token)
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

        ctx0 = atjsparse.exec(code)
        ctx1 = atjsparse.exec(part1)
        ctx2 = atjsparse.exec(part2)
        ctx3 = atjsparse.exec(part3)

        self.assertEqual(ctx0.window['t0'], False)
        self.assertEqual(ctx1.window['t1'], True)
        self.assertEqual(ctx2.window['t2'], False)
        self.assertEqual(ctx3.window['t3'], False)

    def test_exec(self) -> None:

        for i, f in enumerate(self.tests):
            ctx = atjsparse.exec(f)
            res = ctx.window['AJAX_TOKEN']
            self.assertEqual(res, self.results[i])

    def tearDown(self) -> None:
        del self.tests
        del self.results
