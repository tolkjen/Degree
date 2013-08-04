#ifndef __NAIVECLASSIFIER_H__
#define __NAIVECLASSIFIER_H__

#include <memory>
#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>

#include "AbstractClassifier.hpp"

using namespace std;
using namespace faif;
using namespace faif::ml;

class NaiveClassifier : public AbstractClassifier
{
public:
	typedef NaiveBayesian< ValueNominal<string> > NB;

	NaiveClassifier();
	~NaiveClassifier();

	virtual void deserialize(string s);
	virtual string getCategory(TestData &data);
	virtual string serialize();
	virtual void train(TrainingSet &data);

private:
	shared_ptr<NB> _classifier;
};

#endif
