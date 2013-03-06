import unittest
from register import Session, Course, Term


class SessionTests(unittest.TestCase):
    def setUp(self):
        self.username = ''
        self.password = ''

    def test_login(self):
        session = Session()
        logged_in = session.login(self.username, self.password)
        self.assertEqual(logged_in, True)

if __name__ == '__main__':
    unittest.main()
