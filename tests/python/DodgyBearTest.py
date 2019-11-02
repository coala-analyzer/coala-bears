import os
import unittest

from queue import Queue

from bears.python.DodgyBear import DodgyBear
from coalib.testing.BearTestHelper import generate_skip_decorator
from coalib.settings.Section import Section


def create_test_file(name, content):
    file = open(name, 'w')
    file.write(content)


@generate_skip_decorator(DodgyBear)
class DodgyBearTest(unittest.TestCase):

    def setUp(self):
        self.file_dict = {}
        self.queue = Queue()
        self.section = Section('dodgy')
        self.uut = DodgyBear(self.file_dict,
                             self.section,
                             self.queue)

    def get_results(self):
        return list(result.message for result in self.uut.run())

    def test_aws(self):
        create_test_file('amazon.py',
                         'AWS_SECRET_ACCESS_KEY = '
                         '"A8+6AN5XSUZ3vysJg68Rt\A9E7duMlfKODwb3ZD8"')
        self.assertEqual(self.get_results(), [
                         'Amazon Web Services secret key',
                         'Possible hardcoded secret key'])
        os.remove('amazon.py')

    def test_diff(self):
        create_test_file('diff.py',
                         '<<<<<<< HEAD'
                         '\nvar = "test"\n=======\nvar = "test"\n'
                         '>>>>>>> branch')
        self.assertEqual(self.get_results(), [
                         'Possible SCM diff in code',
                         'Possible SCM diff in code'])
        os.remove('diff.py')

    def test_password(self):
        create_test_file('passwords.py',
                         'FACEBOOK_PASSWORD = "random@123"\n'
                         'PASSWORD_TO_GITHUB = "random@123"\n'
                         'PASSWORD = "random@123"\n'
                         'PASSWORD = ""')
        self.assertEqual(self.get_results(), [
                         'Possible hardcoded password',
                         'Possible hardcoded password',
                         'Possible hardcoded password'])
        os.remove('passwords.py')

    def test_secret(self):
        create_test_file('secrets.py',
                         'SECRET = "random@123"\n'
                         'SECRET_KEY = "random@123"\n'
                         'THE_SUPER_SECRET = "random@123"')
        self.assertEqual(self.get_results(), [
                         'Possible hardcoded secret key',
                         'Possible hardcoded secret key',
                         'Possible hardcoded secret key'])
        os.remove('secrets.py')

    def test_ssh_private_key(self):
        create_test_file('ssh_private_key.py',
                         '-----BEGIN RSA PRIVATE KEY-----\n'
                         'RANDOM@123\n'
                         '-----END RSA PRIVATE KEY-----')
        self.assertEqual(self.get_results(), [
                         'Possible SSH private key',
                         'Possible SSH private key'])
        os.remove('ssh_private_key.py')

    def test_ssh_public_key(self):
        create_test_file('ssh_public_key.py',
                         'ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDMqZ2FO/Y'
                         'y+ci0+9y3xUeonX/4tmfYPiAkjsfUWWkykHkCYUlTVS92pr'
                         'aiTO256xy29osYk1xs7U0OpLztfHanHBuUhZz0pn/RvyYGe'
                         'q3i5H3Ne/Z21TldMakhaKMB42V1C2+OV0xnjoEtPYUVG8ici'
                         '7EzjLyDotRkYigRouI26PsmKPyyfqZ3TYVfMtkP21RdcI4/l'
                         'na6d1dBmrQ3ly0B6g+pEf8ObaBriu0Fest0yZhyF8hsgueGu'
                         'gZFXzjaAu68ib99nP17w111cbej9jUNnyfseykl5ngqrvsP3'
                         'mGKw739z+p0vIIchHYa3jn6xW8fim/PH4gtcWC8mUXlv6XT '
                         'random@123')
        self.assertEqual(self.get_results(), ['Possible SSH public key'])
        os.remove('ssh_public_key.py')

    def tearDown(self):
        current = os.listdir()
        test_files = ['amazon.py', 'diff.py', 'passwords.py',
                      'secrets.py', 'ssh_private_key.py', 'ssh_public_key.py']
        for f in test_files:
            if f in current:
                os.remove(f)
