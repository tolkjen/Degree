import unittest
from classifier import NaiveClassifier, TreeClassifier, KNNClassifier

class FaifClassifierTestCase(unittest.TestCase):
	ClassifierType = None

	def test_create_classifier(self):
		classifier = self.ClassifierType([ (['1'], '1') ])

	def test_create_on_empty_list(self):
		classifier = self.ClassifierType([])

	def test_create_on_no_attributes(self):
		classifier = self.ClassifierType([ ([], '1') ])

	def test_train_with_no_domains(self):
		classifier = self.ClassifierType([])
		self.assertRaises(Exception, classifier.train, [ (['1'], '1') ])

	def test_training_data_out_of_domain(self):
		classifier = self.ClassifierType([ (['a'], '1') ])
		self.assertRaises(Exception, classifier.train, [ (['b'], '1') ])
		self.assertRaises(Exception, classifier.train, [ (['a'], '2') ])

	def test_classify_known(self):
		test_data = ['a', 'a']
		training_data = [
			(['a', 'a'], '1'),
			(['a', 'b'], '2'),
			(['b', 'a'], '3'),
			(['b', 'b'], '4'),
		]

		classifier = self.ClassifierType(training_data)
		classifier.train(training_data)
		self.assertTrue(classifier.classify(test_data) in ['1', '2', '3', '4'])

	def test_classify_unknown(self):
		test_data = ['a', 'a']
		training_data = [
			(['a', 'b'], '1'),
			(['b', 'a'], '1'),
			(['b', 'b'], '1'),
		]

		classifier = self.ClassifierType(training_data)
		classifier.train(training_data)
		self.assertEqual('1', classifier.classify(test_data))

class NaiveClassifierTestCase(FaifClassifierTestCase):
	ClassifierType = NaiveClassifier

class TreeClassifierTestCase(FaifClassifierTestCase):
	ClassifierType = TreeClassifier

class KNNClassifierTestCase(FaifClassifierTestCase):
	ClassifierType = KNNClassifier

def suite():
	suites = map(unittest.TestLoader().loadTestsFromTestCase, 
		[NaiveClassifierTestCase, TreeClassifierTestCase, KNNClassifierTestCase])
	return unittest.TestSuite(suites)

if __name__ == "__main__":
	runner = unittest.TextTestRunner()
	test_suite = suite()
	runner.run(test_suite)
