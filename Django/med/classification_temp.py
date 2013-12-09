import classifier

class Classifier:
	classifier_object = classifier.NaiveClassifier()

	def __init__(self, attributes = 1):
		self.reader = classifier.TemporaryReader(attributes)

	def deserialize(self, state_str):
		self.classifier_object.deserialize(state_str)
		self.reader = classifier.TemporaryReader(
			self.classifier_object.attributes
		)

	def get_categories(self, filepath):
		example_data = self.reader.readTestData(filepath)
		return self.classifier_object.getCategories(example_data)

	def serialize(self):
		return self.classifier_object.serialize()

	def train(self, filepath, levels):
		data = self.reader.readTrainingData(filepath)
		self.classifier_object.set_levels(levels)
		self.classifier_object.train(data)
