#include <iostream>
#include <sstream>
#include <string>
#include <algorithm>
#include <limits>
#include <set>

#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>
#include <faif/learning/Validator.hpp>

#include <boost/serialization/nvp.hpp>
#include <boost/archive/xml_oarchive.hpp>
#include <boost/archive/xml_iarchive.hpp>

#include "NaiveClassifier.hpp"

using namespace std;
using namespace faif;
using namespace faif::ml;

const int NaiveClassifier::attrCount = 3;

NaiveClassifier::NaiveClassifier()
{
	_domainCount = 2;
	_classifier = shared_ptr<NB>(new NB());
}

NaiveClassifier::~NaiveClassifier()
{
}

void NaiveClassifier::deserialize(string s)
{
	_classifier->reset();

	istringstream iss(s);
	boost::archive::xml_iarchive ia(iss);
	ia >> boost::serialization::make_nvp("NBC", *_classifier);
	ia >> BOOST_SERIALIZATION_NVP(_ranges);
	ia >> BOOST_SERIALIZATION_NVP(_domainCount);
}

string NaiveClassifier::getCategory(TestData &data)
{
	auto example = createTestExample(data);
    return _classifier->getCategory(example)->get();
}

string NaiveClassifier::serialize()
{
	ostringstream oss;
	boost::archive::xml_oarchive oa(oss);
	oa << boost::serialization::make_nvp("NBC", *_classifier);
	oa << BOOST_SERIALIZATION_NVP(_ranges);
	oa << BOOST_SERIALIZATION_NVP(_domainCount);
	return oss.str();
}

void NaiveClassifier::train(TrainingSet &data)
{
	typedef NB::Domains Domains;
	typedef NB::AttrDomain AttrDomain;
	typedef NB::ExamplesTrain ExamplesTrain;

	// Calculate ranges for attributes and create a set of category names
	set<string> catSet;

	_ranges.clear();
	_ranges.resize(attrCount);

	for (auto &t : data) {
		for (int i = 0; i < attrCount; i++) {
			_ranges[i].start = min(_ranges[i].start, t[i]);
			_ranges[i].end = max(_ranges[i].end, t[i]);
		}
		catSet.insert(t.getCategory());
	}

	// Add a 'guard' to the range to eliminate special cases when start = end.
	for (int i = 0; i < attrCount; i++)
		if (_ranges[i].start == _ranges[i].end)
			_ranges[i].end += 1.0;

	// Create attributes array and categories array for creation of the 
	// classifier.
	string domainNames[_domainCount];
	for (int i = 0; i < _domainCount; i++)
		domainNames[i] = buildDomainName(i);

	Domains attribs;
	attribs.push_back( createDomain("attr0", domainNames, 
		domainNames + _domainCount) );
	attribs.push_back( createDomain("attr1", domainNames, 
		domainNames + _domainCount) );
	attribs.push_back( createDomain("attr2", domainNames, 
		domainNames + _domainCount) );

	string catArray[catSet.size()];
	int i = 0;
	for (auto it = catSet.begin(); it != catSet.end(); ++it) {
		catArray[i] = *it;
		i++;
	}

	AttrDomain cat = createDomain("", catArray, catArray + catSet.size());
	_classifier = shared_ptr<NB>(new NB(attribs, cat));

	// Create discrete training examples from floating point data and train
	// the classifier.
	ExamplesTrain ex;
	for (auto &t : data) {
		ex.push_back( createTrainingExample(t) );
	}
	_classifier->train(ex);
}

void NaiveClassifier::train(TrainingSet &data, int dCount)
{
	// Store domain count and replace it by argument value.
	int tmp = _domainCount;
	_domainCount = dCount;

	// Run training
	train(data);

	// Load back previous domain count
	_domainCount = tmp;
}

string NaiveClassifier::buildDomainName(int i)
{
	return to_string(i);
}

typename NaiveClassifier::ExampleTrain 
NaiveClassifier::createTrainingExample(TrainingData &data)
{
	vector<string> discrete;
	for (int i = 0; i < attrCount; i++) {
		double realData = max(data[i], 0.0);
		double domainLength = (double) (_ranges[i].end - _ranges[i].start) / _domainCount;

		int index = floor((realData - _ranges[i].start) / domainLength);
		int normalizedIndex = min(_domainCount - 1, index);

		discrete.push_back( buildDomainName(normalizedIndex) );
	}
	return faif::ml::createExample(discrete.begin(), discrete.end(), 
		data.getCategory(), *_classifier);
}

typename NaiveClassifier::ExampleTest 
NaiveClassifier::createTestExample(TestData &data)
{
	vector<string> discrete;
	for (int i = 0; i < attrCount; i++) {
		double realData = max(data[i], 0.0);
		double domainLength = (double) (_ranges[i].end - _ranges[i].start) / _domainCount;

		int index = floor((realData - _ranges[i].start) / domainLength);
		int normalizedIndex = min(_domainCount - 1, index);

		discrete.push_back( buildDomainName(normalizedIndex) );
	}
	return faif::ml::createExample(discrete.begin(), discrete.end(), 
		*_classifier);
}

NaiveClassifier::Range::Range() :
	start(numeric_limits<double>::max()), end(numeric_limits<double>::min())
{	
}

NaiveClassifier::Range::Range(double s, double e) :
	start(s), end(e)
{	
}
