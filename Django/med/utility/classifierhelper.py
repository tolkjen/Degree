# coding=utf-8
from classifier import NaiveClassifier, TreeClassifier, KNNClassifier

classifier_type_mapping = {
    u'Naiwny Bayes': NaiveClassifier,
    u'Drzewo decyzyjne': TreeClassifier,
    u'Najbliższy sąsiad': KNNClassifier
}


def get_classifier_type(classifier_type_name):
    if not classifier_type_name in get_type_names():
        raise Exception("Klasyfikator o nazwie " + classifier_type_name + " nie istnieje.")
    return classifier_type_mapping[classifier_type_name]


def get_type_names():
    return classifier_type_mapping.keys()
