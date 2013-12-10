import math

class FakeClassifier:
	def __init__(self, data_rows):
		pass

	def train(self, training_rows):
		pass

	def classify(self, test_row):
		return '1.0'

class KCrossValidator:
	def __init__(self, classifier_type, k):
		self.classifier_type = classifier_type
		self.k = k

	def validate(self, data_rows):
		classifier = self.classifier_type(data_rows)

		score = 0.0
		range_length = int(math.ceil(float(len(data_rows)) / self.k))
		classification_score = lambda (data, value): classifier.classify(data) == value

		for i in xrange(0, len(data_rows), range_length):
			is_for_test = lambda (index, row): index >= i and index <= i + range_length - 1
			is_for_training = lambda (index, row): not is_for_test((index, row))

			enumerated_data =  [(index, row) for (index, row) in enumerate(data_rows)]
			test_rows = map(lambda (index, row): row, filter(is_for_test, enumerated_data))
			training_rows = map(lambda (index, row): row, filter(is_for_training, enumerated_data))

			classifier.train(training_rows)
			score = score + sum(map(classification_score, test_rows))

		return score / len(data_rows)