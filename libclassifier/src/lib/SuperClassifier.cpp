#include "SuperClassifier.hpp"

#include <vector>
#include <list>
#include <set>

#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>
#include <faif/learning/Validator.hpp>

using namespace boost::python;
using namespace std;

SuperClassifier::SuperClassifier(boost::python::list rows) {
	vector<vector<string>> attributeRows;
	vector<string> categories;

	translateTrainingData(rows, attributeRows, categories);

	Domains attributeDomains = createAttributeDomains(attributeRows);
	AttrDomain categoryDomain = createCategoryDomain(categories);
	_classifier = shared_ptr<NB>(new NB(attributeDomains, categoryDomain));
}

void SuperClassifier::train(boost::python::list trainingRows) {
	vector<vector<string>> attributeRows;
	vector<string> categories;

	translateTrainingData(trainingRows, attributeRows, categories);
	trainClassifier(attributeRows, categories);
}

string SuperClassifier::classify(boost::python::list testRow) {
	boost::python::stl_input_iterator<string> attrBegin(testRow), attrEnd;
	vector<string> testVector(attrBegin, attrEnd);

	auto example = faif::ml::createExample(
		testVector.begin(), testVector.end(), *_classifier);
	return _classifier->getCategory(example)->get();
}

SuperClassifier::Domains SuperClassifier::createAttributeDomains(
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

SuperClassifier::AttrDomain SuperClassifier::createCategoryDomain(
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

void SuperClassifier::translateTrainingData(boost::python::list &rows, 
		vector<vector<string>> &attributeRows, vector<string> &categories) {

	boost::python::stl_input_iterator<boost::python::tuple> 
		rowsBegin(rows), rowsEnd;
	std::list<boost::python::tuple> rowsList(rowsBegin, rowsEnd);

	for (auto it = rowsList.begin(); it != rowsList.end(); ++it) {
		auto attrList = boost::python::extract<boost::python::list>( (*it)[0] );
		boost::python::stl_input_iterator<string> attrBegin(attrList), attrEnd;
		vector<string> attributes(attrBegin, attrEnd);
		attributeRows.push_back(attributes);

		auto value = boost::python::extract<string>( (*it)[1] );
		categories.push_back(value);
	}
}

void SuperClassifier::trainClassifier(
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