#ifndef __SUPERNAIVECLASSIFIER_H__
#define __SUPERNAIVECLASSIFIER_H__

#include "SuperClassifier.hpp"

#include <memory>
#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>

using namespace std;
using namespace faif;
using namespace faif::ml;

class SuperNaiveClassifier : public SuperClassifier {
public:
	typedef NaiveBayesian< ValueNominal<string> > NB;
	typedef NB::AttrDomain AttrDomain;
	typedef NB::Domains Domains;

	SuperNaiveClassifier(boost::python::list rows);

protected:
	string virtual classifyData(vector<string> &testRow);
	void virtual trainClassifier(
		vector<vector<string>> &attributeRows, vector<string> &categories);

private:
	Domains static createAttributeDomains(vector<vector<string>> &attributeRows);
	AttrDomain static createCategoryDomain(vector<string> &categories);

private:
	shared_ptr<NB> _classifier;
};

#endif
