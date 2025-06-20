import unittest
from lib import create_booking, response

class TestCreateUser(unittest.TestCase):
    def test_create_booking(self):
        response = create_booking('redangry73', 'umni', 'negr')
        self.assertEqual(response.status, 404)

if __name__ == '__main__':
    unittest.main()