import unittest
import main
import importlib
from io import StringIO
from unittest.mock import patch


class TestApp(unittest.TestCase):

    def setUp(self):
       pass

    def test_get_etoken(self):
        test_str = 'f9c7f37dc361ad97888e979d4be8143d4e6bc1c2466a4722c1f3fefc185e107719ebaa66a8ff92cdf3d'
        return_val = main.get_etoken('https://oauth.vk.com/blank.html#access_token'
                                            '=f9c7f37dc361ad97888e979d4be8143d4e6bc1c2466a'
                                            '4722c1f3fefc185e107719ebaa66a8ff92cdf3d&expires'
                                            '_in=0&user_id=24863449&state=123456')
        self.assertEqual(return_val, test_str)

    def test_check_empty_input(self):
        pass

    def test_show_commands(self):
        pass