# coding=utf-8

from datetime import datetime, tzinfo, timedelta
from os.path import dirname, realpath
import pytz

from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

from django.test import LiveServerTestCase
from django.test import TestCase
from django.core.urlresolvers import reverse

from med.models import CrossValidation

def make_filepath(filename):
	directory = dirname(realpath(__file__))
	return directory + "/" + filename

class WarsawTimeZone(tzinfo):
	def utcoffset(self, dt):
		return timedelta(hours=+1)

	def dst(self, dt):
		return timedelta(0)

class ValidationViewTests(TestCase):

	def test_new(self):
		response = self.client.get(reverse('med:validate_new'))
		self.assertEqual(response.status_code, 200)

	def test_post(self):
		fp = open(make_filepath('data.xls'), 'rb')
		args = {
			'name': 'test name', 
			'classifier': 'bayes', 
			'domain_subgroups': 10,
			'k_groups': 5,
			'uploaded_file': fp
		}
		response = self.client.post(reverse('med:validate_post'), args, 
			follow=True)
		fp.close()
		self.assertContains(response, 'test name')

	def test_post_wo_arguments(self):
		def test_post_response_contains_error(args):
			response = self.client.post(reverse('med:validate_post'), args, 
				follow=True)
			self.assertContains(response, '<div class="error">')

		test_post_response_contains_error({
			'name': 'test name', 
			'classifier': 'bayes', 
			'k_groups': 5,
		})
		with open(make_filepath('data.xls'), 'rb') as fp:
			test_post_response_contains_error({
				'classifier': 'bayes', 
				'k_groups': 5,
				'uploaded_file': fp
			})
		with open(make_filepath('data.xls'), 'rb') as fp:
			test_post_response_contains_error({
				'name': 'test name',
				'k_groups': 5,
				'uploaded_file': fp
			})
		with open(make_filepath('data.xls'), 'rb') as fp:
			test_post_response_contains_error({
				'name': 'test name',
				'classifier': 'bayes', 
				'uploaded_file': fp
			})

	def test_list_empty(self):
		response = self.client.get(reverse('med:validate_list'))
		message = 'Nie przeprowadzono do tej pory żadnej walidacji krzyżowej'
		self.assertContains(response, message)

	def test_list_one_element(self):
		CrossValidation.objects.create(
			name='test name',
			k_groups=1,
			result=1.0,
			domain_subgroups=10,
			date=datetime.utcnow().replace(tzinfo = pytz.utc),
			classifier='bayes'
		)

		response = self.client.get(reverse('med:validate_list'))
		self.assertContains(response, 'test name')

	def test_delete(self):
		CrossValidation.objects.create(
			name='test name',
			k_groups=1,
			result=1.0,
			domain_subgroups=10,
			date=datetime.utcnow().replace(tzinfo = pytz.utc),
			classifier='bayes'
		)

		response = self.client.get(reverse('med:validate_delete', args=(1,)), follow=True)
		message = 'Nie przeprowadzono do tej pory żadnej walidacji krzyżowej'
		self.assertContains(response, message)
		
class SeleniumTests(LiveServerTestCase):

	def get_test_url(self, reverse_name):
		return "%s%s" % (self.live_server_url, reverse(reverse_name))

	@classmethod
	def setUpClass(cls):
		cls.driver = WebDriver()
		cls.driver.implicitly_wait(5) 
		super(SeleniumTests, cls).setUpClass()

	@classmethod
	def tearDownClass(cls):
		cls.driver.quit()
		super(SeleniumTests, cls).tearDownClass()

	def test_validate_post_wo_args(self):
		self.driver.get(self.get_test_url('med:validate_new'))
		self.driver.find_element_by_id('submit').click()
		self.driver.find_element_by_class_name('error')

	def test_validate_post_with_args(self):
		self.driver.get(self.get_test_url('med:validate_new'))

		input_name = self.driver.find_element_by_name('name')
		input_name.send_keys('Test name')

		select_cls = Select(self.driver.find_element_by_tag_name("select"))
		select_cls.select_by_visible_text('Naiwny Bayesowski')

		input_groups = self.driver.find_element_by_name('k_groups')
		input_groups.send_keys('5')

		input_file = self.driver.find_element_by_name('uploaded_file')
		input_file.send_keys(make_filepath('unittests/sample2.xlsx'))

		self.driver.find_element_by_id('submit').click()

		h1 = self.driver.find_element_by_xpath('//div[@class="content"]/h1')
		self.assertEqual(h1.text, 'Wyniki walidacji')

	def test_validate_delete(self):
		CrossValidation.objects.create(
			name='test name',
			k_groups=1,
			result=1.0,
			domain_subgroups=10,
			date=datetime.utcnow().replace(tzinfo = pytz.utc),
			classifier='bayes'
		)

		self.driver.get(self.get_test_url('med:validate_list'))
		link_delete = self.driver.find_element_by_link_text('Usuń')
		link_delete.click()

		p_descr = self.driver.find_element_by_xpath('//div[@class="content"]/p')
		self.assertEqual(p_descr.text[:3], "Nie")
