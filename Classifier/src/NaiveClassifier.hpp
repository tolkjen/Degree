#ifndef __NAIVECLASSIFIER_H__
#define __NAIVECLASSIFIER_H__

#include <memory>
#include <vector>

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
	typedef NB::ExampleTrain ExampleTrain;
	typedef NB::ExampleTest ExampleTest;

	NaiveClassifier();
	~NaiveClassifier();

	virtual void deserialize(string s);
	virtual string getCategory(TestData &data);
	virtual string serialize();
	virtual void train(TrainingSet &data);
	void train(TrainingSet &data, int dCount);

public:
	static const int attrCount;

private:
	class Range
	{
	public:
		friend class boost::serialization::access;

	public:
		Range();
		Range(double s, double e);

		template<class Archive> void serialize(Archive &ar, 
		const unsigned int version)
		{
			ar & BOOST_SERIALIZATION_NVP(start);
			ar & BOOST_SERIALIZATION_NVP(end);
		}

		double start;
		double end;
	};

private:
	string buildDomainName(int i);
	ExampleTrain createTrainingExample(TrainingData &data);
	ExampleTest createTestExample(TestData &data);

private:
	shared_ptr<NB> _classifier;
	vector<Range> _ranges;
	int _domainCount;
};

#endif
