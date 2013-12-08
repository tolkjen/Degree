import math

from sample import Sample

class FakeClassifier:
	rows = []

	def train(self, training_rows):
		self.rows = training_rows

	def classify(self, test_row):
		return '1.0'

class KCrossValidator:
	classifier = None
	k = 0

	def __init__(self, classifier, k):
		self.classifier = classifier
		self.k = k

	def validate(self, data_rows):
		score = 0.0
		range_length = int(math.ceil(len(data_rows) / self.k))
		classification_score = lambda (data, value): self.classifier.classify(data) == value

		for i in xrange(0, len(data_rows), range_length):
			is_for_test = lambda (index, row): index >= i and index <= i + range_length - 1
			is_for_training = lambda (index, row): not is_for_test((index, row))

			enumerated_data =  [(index, row) for (index, row) in enumerate(data_rows)]
			test_rows = map(lambda (index, row): row, filter(is_for_test, enumerated_data))
			training_rows = map(lambda (index, row): row, filter(is_for_training, enumerated_data))

			self.classifier.train(training_rows)
			score = score + sum(map(classification_score, test_rows))

		return score / len(data_rows)

if __name__ == "__main__":
	data_sample = Sample.fromFile('data.xls')
	validator = KCrossValidator(FakeClassifier(), 4)
	print validator.validate(data_sample.rows())
