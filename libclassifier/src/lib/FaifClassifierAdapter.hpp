#ifndef __SUPERNAIVECLASSIFIER_H__
#define __SUPERNAIVECLASSIFIER_H__

#include "ClassifierAdapter.hpp"

#include <vector>
#include <list>
#include <set>
#include <memory>

using namespace std;
using namespace boost::python;

#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>
#include <faif/learning/Validator.hpp>

using namespace faif;
using namespace faif::ml;

template<template<class> class TClassifier>
class FaifClassifierAdapter : public ClassifierAdapter {
public:
	typedef TClassifier<ValueNominal<string>> CLS;
	typedef typename CLS::AttrDomain AttrDomain;
	typedef typename CLS::Domains Domains;

	FaifClassifierAdapter(boost::python::list rows) {
		vector<vector<string>> attributeRows;
		vector<string> categories;

		translateTrainingData(rows, attributeRows, categories);

		Domains attributeDomains = createAttributeDomains(attributeRows);
		AttrDomain categoryDomain = createCategoryDomain(categories);
		_classifier = shared_ptr<CLS>(new CLS(attributeDomains, categoryDomain));
	}

protected:
	string classifyData(vector<string> &testRow) {
		auto example = faif::ml::createExample(
			testRow.begin(), testRow.end(), *_classifier);
		return _classifier->getCategory(example)->get();
	}

	void trainClassifier(
		vector<vector<string>> &attributeRows, vector<string> &categories) {

		CLS::ExamplesTrain ex;
		for (int i = 0; i < attributeRows.size(); i++) {
			auto example = faif::ml::createExample(
				attributeRows[i].begin(), attributeRows[i].end(), categories[i], 
				*_classifier);
			ex.push_back(example);
		}

		_classifier->reset();
		_classifier->train(ex);
	}

private:
	typename FaifClassifierAdapter::Domains createAttributeDomains(
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

	typename FaifClassifierAdapter::AttrDomain createCategoryDomain(
		vector<string> &categories) {

		set<string> unique;
		for (auto category : categories)
			unique.insert(category);

		string* domain = new string[unique.size()];
		string* writePtr = domain;
		for (auto str : unique)
			*writePtr++ = str;

		AttrDomain categoryDomain = 
			createDomain("", domain, domain + unique.size());
		delete [] domain;

		return categoryDomain;
	}

private:
	shared_ptr<CLS> _classifier;
};

#endif
