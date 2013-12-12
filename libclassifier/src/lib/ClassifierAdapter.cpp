#include "ClassifierAdapter.hpp"

#include <boost/python/stl_iterator.hpp>
#include <vector>
#include <list>

using namespace boost::python;
using namespace std;

void ClassifierAdapter::train(boost::python::list trainingRows) {
	vector<vector<string>> attributeRows;
	vector<string> categories;

	translateTrainingData(trainingRows, attributeRows, categories);
	trainClassifier(attributeRows, categories);
}

string ClassifierAdapter::classify(boost::python::list testRow) {
	boost::python::stl_input_iterator<string> attrBegin(testRow), attrEnd;
	vector<string> testVector(attrBegin, attrEnd);

	return classifyData(testVector);
}

void ClassifierAdapter::translateTrainingData(boost::python::list &rows, 
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
