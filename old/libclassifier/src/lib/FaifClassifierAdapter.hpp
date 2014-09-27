#ifndef __SUPERNAIVECLASSIFIER_H__
#define __SUPERNAIVECLASSIFIER_H__

#include <faif/learning/Classifier.hpp>
#include "ClassifierAdapter.hpp"
#include "ClassifierException.hpp"

#include <list>
#include <set>
#include <memory>

using namespace std;
using namespace faif;
using namespace faif::ml;
using namespace boost::python;

template<typename TClassifier>
class FaifClassifierAdapter : public ClassifierAdapter {
public:
	typedef TClassifier CLS;
	typedef typename CLS::AttrDomain AttrDomain;
	typedef typename CLS::Domains Domains;

	FaifClassifierAdapter(boost::python::list rows) 
		: _domainsCreated(false), _trained(false)
	{
		vector<vector<string>> attributeRows;
		vector<string> categories;

		translateTrainingData(rows, attributeRows, categories);

		if (attributeRows.size() > 0 && categories.size() > 0) {
			Domains attributeDomains = createAttributeDomains(attributeRows);
			AttrDomain categoryDomain = createCategoryDomain(categories);
			_classifier = shared_ptr<CLS>(new CLS(attributeDomains, categoryDomain));
			_domainsCreated = true;
		}
	}

protected:
	string classifyData(vector<string> &testRow) {
		if (_trained) {
			auto example = faif::ml::createExample(
				testRow.begin(), testRow.end(), *_classifier);
			return _classifier->getCategory(example)->get();		
		} else {
			throw ClassifierException("Klasyfikator nie zostal nauczony.");
		}
	}

	void trainClassifier(
		vector<vector<string>> &attributeRows, vector<string> &categories) {

		if (!_domainsCreated) {
			throw ClassifierException("Klasyfikator nie posiada wiedzy o dziedzinach atrybutow.");
		}

		typename CLS::ExamplesTrain ex;
		try {
			for (int i = 0; i < attributeRows.size(); i++) {
				auto example = faif::ml::createExample(
					attributeRows[i].begin(), attributeRows[i].end(), categories[i], 
					*_classifier);
				ex.push_back(example);
			}
		}
		catch (exception &e) {
			throw ClassifierException("Dziedziny danych trenujacych nie odpowiadaja poznanym dziedzinom.");
		}

		_classifier->reset();
		_classifier->train(ex);
		
		_trained = true;
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
	bool _trained, _domainsCreated;
};

#endif
