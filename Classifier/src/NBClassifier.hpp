#ifndef __NBCLASSIFIER_H__
#define __NBCLASSIFIER_H__

#include "AbstractClassifier.hpp"

class NBClassifier : public AbstractClassifier
{
public:
	typedef vector<TrainingData> TrainingSet;

	virtual void deserialize(string s);
	virtual string getCategory(TestData &data);
	virtual string serialize();
	virtual void train(TrainingSet &data);
};

#endif
