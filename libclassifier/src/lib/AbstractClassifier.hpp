#ifndef __ABSTRACTCLASSIFIER_H__
#define __ABSTRACTCLASSIFIER_H__

#include "TrainingData.hpp"

class AbstractClassifier
{
public:
	typedef vector<TrainingData> TrainingSet;

	virtual void deserialize(string s) = 0;
	virtual string getCategory(TestData &data) = 0;
	virtual string serialize() = 0;
	virtual void train(TrainingSet &data) = 0;
};

#endif
