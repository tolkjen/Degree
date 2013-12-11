#include "SuperNaiveClassifier.hpp"

#include <vector>
#include <list>
#include <set>

#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>
#include <faif/learning/Validator.hpp>

using namespace boost::python;
using namespace std;

SuperNaiveClassifier::SuperNaiveClassifier(boost::python::list rows) {
	vector<vector<string>> attributeRows;
	vector<string> categories;

	translateTrainingData(rows, attributeRows, categories);

	Domains attributeDomains = createAttributeDomains(attributeRows);
	AttrDomain categoryDomain = createCategoryDomain(categories);
	_classifier = shared_ptr<NB>(new NB(attributeDomains, categoryDomain));
}

string SuperNaiveClassifier::classifyData(vector<string> &testRow) {
	auto example = faif::ml::createExample(
		testRow.begin(), testRow.end(), *_classifier);
	return _classifier->getCategory(example)->get();
}

SuperNaiveClassifier::Domains SuperNaiveClassifier::createAttributeDomains(
	vector<vector<string>> &attributeRows) {

	Domains attributeDomains;

	int attributeRowLength = attributeRows[0].size();
	for (int i = 0; i < attributeRowLength; i++) {
		set<string> unique;
		for (auto attributeRow : attributeRows)
			unique.insert(attributeRow[i]);

		string* domain = new string[unique.size()];
		string* writePtr = domain;
		for (auto str : unique)
			*writePtr++ = str;

		attributeDomains.push_back(
			createDomain("", domain, domain + unique.size()));
		delete [] domain;
	}

	return attributeDomains;
}

SuperNaiveClassifier::AttrDomain SuperNaiveClassifier::createCategoryDomain(
	vector<string> &categories) {

	set<string> unique;
	for (auto category : categories)
		unique.insert(category);

	string* domain = new string[unique.size()];
	string* writePtr = domain;
	for (auto str : unique)
		*writePtr++ = str;

	NB::AttrDomain categoryDomain = 
		createDomain("", domain, domain + unique.size());
	delete [] domain;

	return categoryDomain;
}

void SuperNaiveClassifier::trainClassifier(
	vector<vector<string>> &attributeRows, vector<string> &categories) {

	NB::ExamplesTrain ex;
	for (int i = 0; i < attributeRows.size(); i++) {
		auto example = faif::ml::createExample(
			attributeRows[i].begin(), attributeRows[i].end(), categories[i], 
			*_classifier);
		ex.push_back(example);
	}

	_classifier->reset();
	_classifier->train(ex);
}
