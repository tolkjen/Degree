import math
import subsetgenerator

class KCrossValidator:
	
	GROUP_SELECTION_RANGE = 0
	GROUP_SELECTION_RANDOM = 1

	def __init__(self, classifier_type, k, group_selection_type=GROUP_SELECTION_RANGE):
		self.classifier_type = classifier_type

		if not group_selection_type in [KCrossValidator.GROUP_SELECTION_RANGE, KCrossValidator.GROUP_SELECTION_RANDOM]:
			raise Exception('Nieprawidlowy rodzaj wyboru grup uczacych i testowych.')
		
		subset_generator_types = {
			KCrossValidator.GROUP_SELECTION_RANGE: subsetgenerator.RangeSubsetGenerator,
			KCrossValidator.GROUP_SELECTION_RANDOM: subsetgenerator.RandomSubsetGenerator
		}
		self.group_selection_type = group_selection_type
		self.subset_generator_type = subset_generator_types[self.group_selection_type]

		if k <= 0:
			raise Exception('Liczba podgrup musi byc wieksza od zera.')
		self.k = k

	def validate(self, data_rows):
		if len(data_rows) == 0:
			raise Exception('Dane wejsciowe nie moga byc puste.')

		score = 0.0
		classifier = self.classifier_type(data_rows)
		classification_score = lambda (data, value): classifier.classify(data) == value

		subset_generator = self.subset_generator_type(data_rows, self.k)
		for data_subsets in subset_generator.generate():
			classifier.train(data_subsets['training'])
			score = score + sum(map(classification_score, data_subsets['test']))

		return score / len(data_rows)
