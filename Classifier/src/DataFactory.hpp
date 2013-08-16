#ifndef __DATA_FACTORY_H__
#define __DATA_FACTORY_H__

#include <vector>

#include "TrainingData.hpp"

using namespace std;

class DataFactory
{
public:
	typedef vector<string> StringVector;
	typedef vector<TrainingData> TrainingSet;
	typedef vector<TestData> TestSet;

	DataFactory();

	StringVector attributes();
	string category();
	virtual TrainingSet readTrainingData(string path) = 0;
	virtual TestSet readTestData(string path) = 0;

protected:
	StringVector _attributes;
	string _category;
};

#endif
