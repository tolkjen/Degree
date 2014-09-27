#ifndef __SUPERCLASSIFIER_H__
#define __SUPERCLASSIFIER_H__

#include <boost/python.hpp>
#include <string>
#include <vector>

using namespace std;

class ClassifierAdapter {
public:
	void train(boost::python::list trainingRows);
	string classify(boost::python::list testRow);

protected:
	string virtual classifyData(vector<string> &testRow) = 0;
	void virtual trainClassifier(
		vector<vector<string>> &attributeRows, vector<string> &categories) = 0;
	void static translateTrainingData(boost::python::list &rows, 
		vector<vector<string>> &attributeRows, vector<string> &categories);
};

#endif
