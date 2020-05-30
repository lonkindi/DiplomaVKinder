import unittest
import datetime

import main
import db_actions
from io import StringIO
from unittest.mock import patch


class TestMain(unittest.TestCase):

    def test_get_etoken(self):
        test_str = 'f9c7f37dc361ad97888e979d4be8143d4e6bc1c2466a4722c1f3fefc185e107719ebaa66a8ff92cdf3'
        return_val = main.get_etoken('https://oauth.vk.com/blank.html#access_token'
                                     '=f9c7f37dc361ad97888e979d4be8143d4e6bc1c2466a'
                                     '4722c1f3fefc185e107719ebaa66a8ff92cdf3&expires'
                                     '_in=0&user_id=24863449&state=123456')
        self.assertEqual(return_val, test_str)

    def test_parse_text(self):
        test_str = {'one', 'two', 'five six', 'seven 7'}
        return_val = main.parse_text('one, two, five six; seven 7')
        self.assertEqual(return_val, test_str)

    def test_get_age(self):
        now = datetime.datetime.now().date()
        now_str = now.strftime('%d.%m.%Y')
        return_val = main.get_age(now_str)
        self.assertEqual(return_val, 0)
        self.assertRaises(ValueError, main.get_age, '00.00.0000')

    def test_get_photos(self):
        return_val = main.get_photos(1)
        self.assertEqual(len(return_val), 3)

    def test_output_data(self):
        test_str = 'Результаты поиска записаны в файл output.json'
        with patch('sys.stdout', new=StringIO()) as printOutput:
            main.output_data({})
            output = printOutput.getvalue().strip()
        self.assertEqual(output, test_str)

    def test_add_candidate(self):
        self.assertRaises(TypeError, db_actions.add_candidate)
        self.assertRaises(TypeError, db_actions.add_candidate, vk_id=0)
        self.assertRaises(TypeError, db_actions.add_candidate, user_id=0)
        self.assertRaises(TypeError, db_actions.add_candidate, 'a, b')

    def test_get_used(self):
        self.assertEqual(db_actions.get_used(0), [0])
        self.assertEqual(len(db_actions.get_used(0)), 1)
