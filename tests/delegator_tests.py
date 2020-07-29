import unittest
from oop_utils.delegator import Delegator

class TestDelegator(unittest.TestCase):
    def setUp(self):
        self.widget = Widget('The widget')
    def test_upper(self):
        self.assertEqual('foo'.upper(), 'FOO')

    def test_isupper(self):
        self.assertTrue('FOO'.isupper())
        self.assertFalse('Foo'.isupper())

    def test_split(self):
        s = 'hello world'
        self.assertEqual(s.split(), ['hello', 'world'])
        # check that s.split fails when the separator is not a string
        with self.assertRaises(TypeError):
            s.split(2)


def suite():
    test_suite = unittest.TestSuite()
    test_suite.addTest(WidgetTestCase('test_default_widget_size'))
    test_suite.addTest(WidgetTestCase('test_widget_resize'))
    return suite

if __name__ == '__main__':
    unittest.main()