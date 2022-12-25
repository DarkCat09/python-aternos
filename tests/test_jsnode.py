#!/usr/bin/env python3

import unittest

from python_aternos import atjsparse
from tests import files


class TestJsNode(unittest.TestCase):

    def setUp(self) -> None:

        self.tests = files.read_sample('token_input.txt')
        self.results = files.read_sample('token_output.txt')
        self.js = atjsparse.NodeInterpreter()

    def test_exec(self) -> None:

        for func, exp in zip(self.tests, self.results):
            self.js.exec_js(func)
            res = self.js['AJAX_TOKEN']
            self.assertEqual(res, exp)


if __name__ == '__main__':
    unittest.main()
