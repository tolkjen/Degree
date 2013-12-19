# coding=utf-8

from datetime import datetime, tzinfo, timedelta
from os.path import dirname, realpath

from django.test import TestCase
from django.core.urlresolvers import reverse

from med.models import CrossValidation

def make_filepath(filename):
	directory = dirname(realpath(__file__))
	return directory + "/" + filename

class ValidationViewTests(TestCase):

	class WarsawTimeZone(tzinfo):
		def utcoffset(self, dt):
			return timedelta(hours=+1)

		def dst(self, dt):
			return timedelta(0)

	def test_new(self):
		response = self.client.get(reverse('med:validate_new'))
		self.assertEqual(response.status_code, 200)

	def test_post(self):
		fp = open(make_filepath('data.xls'), 'rb')
		args = {
			'name': 'test name', 
			'classifier': 'bayes', 
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
			date=datetime(2013, 12, 16, tzinfo=self.WarsawTimeZone()),
			classifier='bayes'
		)

		response = self.client.get(reverse('med:validate_list'))
		self.assertContains(response, 'test name')

	def test_delete(self):
		CrossValidation.objects.create(
			name='test name',
			k_groups=1,
			result=1.0,
			date=datetime(2013, 12, 16, tzinfo=self.WarsawTimeZone()),
			classifier='bayes'
		)

		response = self.client.get(reverse('med:validate_delete', args=(1,)), follow=True)
		message = 'Nie przeprowadzono do tej pory żadnej walidacji krzyżowej'
		self.assertContains(response, message)
		
