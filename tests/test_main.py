import unittest
import main
import importlib
from io import StringIO
from unittest.mock import patch


class TestApp(unittest.TestCase):

    def setUp(self):
       pass

    def test_verify_command(self):
        with patch('app.input', return_value='q'):
            return_val1 = main.verify_command('z')
            return_val2 = main.verify_command('l')
        self.assertFalse(return_val1)
        self.assertTrue(return_val2)

    def test_check_empty_input(self):
        return_val1 = main.check_empty_input('')
        return_val2 = main.check_empty_input('l')
        self.assertFalse(return_val1)
        self.assertTrue(return_val2)

    def test_show_commands(self):
        test_str = 'p - l - s - a - d - m - as - h - q -'
        with patch('sys.stdout', new=StringIO()) as printOutput:
            main.show_commands()
            output = printOutput.getvalue().strip()
        self.assertEqual(output, test_str)