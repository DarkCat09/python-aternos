import unittest

from python_aternos import atjsparse
from tests import files

CONV_TOKEN_ARROW = '''(() => {/*AJAX_TOKEN=123}*/window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})();'''
CONV_TOKEN_FUNC = '''(function(){window["AJAX_TOKEN"]=("2r" + "KO" + "A1" + "IFdBcHhEM" + "61" + "6cb");})()'''


class TestJs2Py(unittest.TestCase):

    def setUp(self) -> None:

        self.tests = files.read_sample('token_input.txt')
        self.results = files.read_sample('token_output.txt')

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

        ctx0 = atjsparse.exec_js(code)
        ctx1 = atjsparse.exec_js(part1)
        ctx2 = atjsparse.exec_js(part2)
        ctx3 = atjsparse.exec_js(part3)

        self.assertEqual(ctx0.window['t0'], False)
        self.assertEqual(ctx1.window['t1'], True)
        self.assertEqual(ctx2.window['t2'], False)
        self.assertEqual(ctx3.window['t3'], False)

    def test_exec(self) -> None:

        for i, f in enumerate(self.tests):
            ctx = atjsparse.exec_js(f)
            res = ctx.window['AJAX_TOKEN']
            self.assertEqual(res, self.results[i])


if __name__ == '__main__':
    unittest.main()
