#include <iostream>
#include <sstream>
#include <string>

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
	typedef NB::Domains Domains;
	typedef NB::AttrDomain AttrDomain;

	Domains attribs;
	string numAttr[] = {"0", "1", "2", "3"};
	attribs.push_back( createDomain("str", numAttr, numAttr + 4) );
	attribs.push_back( createDomain("dex", numAttr, numAttr + 4) );
	attribs.push_back( createDomain("int", numAttr, numAttr + 4) );

	string C[] = {"warrior", "archer", "mage"};
	AttrDomain cat = createDomain("", C, C + 3);

	_classifier = shared_ptr<NB>(new NB(attribs, cat));
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
}

string NaiveClassifier::getCategory(TestData &data)
{
	auto example = createExample(data.begin(), data.end(), *_classifier);
    return _classifier->getCategory(example)->get();
}

string NaiveClassifier::serialize()
{
	ostringstream oss;
	boost::archive::xml_oarchive oa(oss);
	oa << boost::serialization::make_nvp("NBC", *_classifier);
	return oss.str();
}

void NaiveClassifier::train(TrainingSet &data)
{
	typedef NB::ExamplesTrain ExamplesTrain;

	_classifier->reset();

	ExamplesTrain ex;
	for (auto &t : data) {
		auto example = createExample(t.begin(), t.end(), t.getCategory(), 
			*_classifier);
		ex.push_back(example);
	}

	_classifier->train(ex);
}
