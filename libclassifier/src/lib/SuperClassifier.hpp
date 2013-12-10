#ifndef __SUPERCLASSIFIER_H__
#define __SUPERCLASSIFIER_H__

#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>
#include <string>
#include <memory>

#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>

using namespace std;
using namespace faif;
using namespace faif::ml;

class SuperClassifier {
public:
	typedef NaiveBayesian< ValueNominal<string> > NB;
	typedef NB::AttrDomain AttrDomain;
	typedef NB::Domains Domains;

	SuperClassifier(boost::python::list rows);

	void train(boost::python::list trainingRows);
	string classify(boost::python::list testRow);

private:
	Domains createAttributeDomains(vector<vector<string>> &attributeRows);
	AttrDomain createCategoryDomain(vector<string> &categories);
	void translateTrainingData(boost::python::list &rows, 
		vector<vector<string>> &attributeRows, vector<string> &categories);
	void trainClassifier(
		vector<vector<string>> &attributeRows, vector<string> &categories);

private:
	shared_ptr<NB> _classifier;
};

#endif
