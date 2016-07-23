import unittest


tcase = unittest.TestCase


class TestBare(tcase):

    def test(self):
        self.assertTrue(True)

if __name__ == '__main__':
    unittest.main()
