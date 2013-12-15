import unittest
from classifier import NaiveClassifier, TreeClassifier, KNNClassifier

class ClassifierTestCase(unittest.TestCase):

	def invoke_multiple(self, func):
		func(NaiveClassifier)
		func(TreeClassifier)
		func(KNNClassifier)

	def test_classify_known(self):
		def classify_known(ClassifierType):
			test_data = ['a', 'a']
			training_data = [
				(['a', 'a'], '1'),
				(['a', 'b'], '2'),
				(['b', 'a'], '3'),
				(['b', 'b'], '4'),
			]

			classifier = ClassifierType(training_data)
			classifier.train(training_data)
			self.assertTrue(classifier.classify(test_data) in ['1', '2', '3', '4'])

		self.invoke_multiple(classify_known)

	def test_classify_unknown(self):
		def classify_unknown(ClassifierType):
			test_data = ['a', 'a']
			training_data = [
				(['a', 'b'], '1'),
				(['b', 'a'], '1'),
				(['b', 'b'], '1'),
			]

			classifier = ClassifierType(training_data)
			classifier.train(training_data)
			self.assertEqual('1', classifier.classify(test_data))

		self.invoke_multiple(classify_unknown)

if __name__ == "__main__":
	unittest.main()
