# coding=utf-8

from classifier import NaiveClassifier, TreeClassifier, KNNClassifier

class ClassifierHelper:
	classifier_type_mapping = {
		u'Naiwny Bayes': NaiveClassifier, 
		u'Drzewo decyzyjne': TreeClassifier, 
		u'Najbliższy sąsiad': KNNClassifier
	}

	@staticmethod
	def get_classifier_type(classifier_type_name):
		if not classifier_type_name in ClassifierHelper.get_type_names():
			raise Exception("Klasyfikator o nazwie " + classifier_type_name + " nie istnieje.")
		return ClassifierHelper.classifier_type_mapping[classifier_type_name]

	@staticmethod
	def get_type_names():
		return ClassifierHelper.classifier_type_mapping.keys()
