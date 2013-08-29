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

NaiveClassifier::NaiveClassifier()
{
	_levels = 2;
	_attrCount = 1;
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
	ia >> BOOST_SERIALIZATION_NVP(_levels);
	ia >> BOOST_SERIALIZATION_NVP(_attrCount);
}

int NaiveClassifier::getAttributeCount()
{
	return _attrCount;
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
	oa << BOOST_SERIALIZATION_NVP(_levels);
	oa << BOOST_SERIALIZATION_NVP(_attrCount);
	return oss.str();
}

void NaiveClassifier::setDescreteLevels(int lvls)
{
	_levels = lvls;
}

void NaiveClassifier::train(TrainingSet &data)
{
	typedef NB::Domains Domains;
	typedef NB::AttrDomain AttrDomain;
	typedef NB::ExamplesTrain ExamplesTrain;

	// Learn about the number of attributes in the data.
	_attrCount = data[0].size();

	// Calculate ranges for attributes and create a set of category names
	set<string> catSet;

	_ranges.clear();
	_ranges.resize(_attrCount);

	for (auto &t : data) {
		for (int i = 0; i < _attrCount; i++) {
			_ranges[i].start = min(_ranges[i].start, t[i]);
			_ranges[i].end = max(_ranges[i].end, t[i]);
		}
		catSet.insert(t.getCategory());
	}

	// Add a 'guard' to the range to eliminate special cases when start = end.
	for (int i = 0; i < _attrCount; i++)
		if (_ranges[i].start == _ranges[i].end)
			_ranges[i].end += 1.0;

	// Create attributes array and categories array for creation of the 
	// classifier.
	string* domainNames = new string[_levels];
	for (int i = 0; i < _levels; i++)
		domainNames[i] = buildDomainName(i);

	Domains attribs;
	for (int i = 0; i < _attrCount; i++)
		attribs.push_back( createDomain("", domainNames, 
			domainNames + _levels) );

	string* catArray = new string[catSet.size()];
	int i = 0;
	for (auto it = catSet.begin(); it != catSet.end(); ++it) {
		catArray[i] = *it;
		i++;
	}

	AttrDomain cat = createDomain("", catArray, catArray + catSet.size());
	_classifier = shared_ptr<NB>(new NB(attribs, cat));

	delete [] catArray;
	delete [] domainNames;

	// Create discrete training examples from floating point data and train
	// the classifier.
	ExamplesTrain ex;
	for (auto &t : data) {
		ex.push_back( createTrainingExample(t) );
	}
	_classifier->train(ex);
}

string NaiveClassifier::buildDomainName(int i)
{
	return to_string(i);
}

NaiveClassifier::ExampleTrain 
NaiveClassifier::createTrainingExample(TrainingData &data)
{
	vector<string> discrete;
	for (int i = 0; i < _attrCount; i++) {
		double realData = max(data[i], 0.0);
		double domainLength = (double) (_ranges[i].end - _ranges[i].start) / _levels;

		int index = floor((realData - _ranges[i].start) / domainLength);
		int normalizedIndex = min(_levels - 1, index);

		discrete.push_back( buildDomainName(normalizedIndex) );
	}
	return faif::ml::createExample(discrete.begin(), discrete.end(), 
		data.getCategory(), *_classifier);
}

#include <iostream>

NaiveClassifier::ExampleTest 
NaiveClassifier::createTestExample(TestData &data)
{
	vector<string> discrete;
	for (int i = 0; i < _attrCount; i++) {
		double realData = max(data[i], 0.0);
		double domainLength = (double) (_ranges[i].end - _ranges[i].start) / _levels;

		int index = floor((realData - _ranges[i].start) / domainLength);
		int normalizedIndex = min(_levels - 1, index);

		discrete.push_back( buildDomainName(normalizedIndex) );
	}

	cout << "(";
	for (int i = 0; i < data.size(); i++)
		cout << data[i] << ", ";
	cout << ") --> (";
	for (int i = 0; i < discrete.size(); i++)
		cout << discrete[i] << ", ";
	cout << ")" << endl;

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
