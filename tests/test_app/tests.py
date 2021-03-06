# -*- coding: utf-8 -*-
import sys
from django.core import mail
from django.test import TestCase
from django.utils.unittest import skip, expectedFailure
from django.test import LiveServerTestCase


class SaintyChecks(TestCase):
    #@classmethod
    #def setUpClass(cls):
    #    raise Exception("Ups, should be disabled")

    def test_mailbox_stubs_not_broken(self):
        print("Testing mailbox django stubs")
        mail.send_mail('Test subject', 'Test message', 'nobody@kenkins.com',
                       ['somewhere@nowhere.com'])
        self.assertTrue(1, len(mail.outbox))

    @skip("Check skiped test")
    def test_is_skipped(self):
        print("This test should be skipped")

    def test_junit_xml_with_utf8_stdout_and_stderr(self):
        sys.stdout.write('\xc4\x85')
        sys.stderr.write('\xc4\x85')

    def test_junit_xml_with_invalid_stdout_and_stderr_encoding(self):
        sys.stdout.write('\xc4')
        sys.stderr.write('\xc4')

    @expectedFailure
    def test_error_with_unicode_msg(self):
        self.assertTrue(False, 'Привет, я ошибка')

    @expectedFailure
    def test_failure(self):
        raise Exception("Ups, should be disabled")


try:
    from selenium.webdriver.firefox.webdriver import WebDriver
except ImportError:
    use_selenium = False
    skip_msg = 'Selenium not installed'
else:
    use_selenium = sys.version_info[0] < 3
    if not use_selenium:
        skip_msg = 'Selenium not works on p3k yet'
    else:
        skip_msg = 'Selenium good'


class SeleniumTests(LiveServerTestCase):

    __unittest_skip__ = not use_selenium
    __unittest_skip_why__ = skip_msg

    fixtures = ['default_users.json']

    @classmethod
    def setUpClass(cls):
        cls.selenium = WebDriver()
        super(SeleniumTests, cls).setUpClass()

    @classmethod
    def tearDownClass(cls):
        super(SeleniumTests, cls).tearDownClass()
        cls.selenium.quit()

    def test_login(self):
        self.selenium.get('%s%s' % (self.live_server_url, '/test_click/'))
        self.selenium.find_element_by_id("wm_click").click()
        self.assertEqual('Button clicked', self.selenium.find_element_by_id("wm_target").text)
