#include <boost/serialization/vector.hpp>
#include <boost/serialization/nvp.hpp>
#include <boost/archive/xml_oarchive.hpp>
#include <boost/archive/xml_iarchive.hpp>
#include <boost/python.hpp>

#include "TestData.hpp"
#include "TrainingData.hpp"
#include "TemporaryReader.hpp"
#include "NaiveClassifier.hpp"
#include "TemporaryFactory.hpp"

using namespace boost::python;
using namespace reader;
using namespace std;

class TrainingDataWrapper
{
public:
	TrainingDataWrapper() {}

	TrainingDataWrapper(TrainingData &data)
	{
		for (auto it = data.begin(); it != data.end(); ++it)
			attr.append(*it);
		cat = data.getCategory();
	}

	template<class Archive> void serialize(Archive & ar, 
		const unsigned int version)
	{
		ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(TrainingData);
	}

public:
	boost::python::list attr;
	string cat;
};

class TrainingDataVector
{
public:
	string serialize()
	{
		ostringstream oss;
		boost::archive::xml_oarchive oa(oss);
		oa << BOOST_SERIALIZATION_NVP(data);
		return oss.str();
	}

	void deserialize(string s)
	{
		data.clear();

		istringstream iss(s);
		boost::archive::xml_iarchive ia(iss);
		ia >> BOOST_SERIALIZATION_NVP(data);
	}

	boost::python::list to_list()
	{
		boost::python::list result;
		for (auto &elem : data)
			result.append( TrainingDataWrapper(elem) );
		return result;
	}

public:
	vector<TrainingData> data;
};

class TestDataVector
{
public:
	vector<TestData> data;
};

class NaiveClassifierWrapper
{
public:
	void deserialize(string s)
	{
		cl.deserialize(s);
	}

	string getCategory(TestData &data)
	{
		return cl.getCategory(data);
	}

	TrainingDataVector getCategories(TestDataVector &v)
	{
		TrainingDataVector result;
		for (TestData &testData : v.data) {
			TrainingData example;
			example.setCategory( cl.getCategory(testData) );
			for (auto it = testData.begin(); it != testData.end(); ++it)
				example.insert(*it);
			result.data.push_back( example );
		}
		return result;
	}

	string serialize()
	{
		return cl.serialize();
	}

	void train(TrainingDataVector &v, int dCount)
	{
		cl.train(v.data, dCount);
	}

private:
	NaiveClassifier cl;
};

class TemporaryFactoryWrapper
{
public:
	boost::python::list attributes()
	{
		boost::python::list result;
		auto stringVector = _factory.attributes();
		for (string& s : stringVector)
			result.append( s );
		return result;
	}

	string category() 
	{
		return _factory.category();
	}

	TrainingDataVector readTraining(string path)
	{
		TrainingDataVector result;
		result.data = _factory.readTrainingData(path);
		return result;
	}

	TestDataVector readTest(string path)
	{
		TestDataVector result;
		result.data = _factory.readTestData(path);
		return result;
	}

private:
	TemporaryFactory _factory;
};

BOOST_PYTHON_MODULE(classifier)
{
	register_exception_translator<ReadingException>
		(&ReadingException::translate);

	class_<TestData>("TestData");

	class_<TrainingDataWrapper>("TrainingData", init<>())
		.def_readonly("attr", &TrainingDataWrapper::attr)
		.def_readonly("category", &TrainingDataWrapper::cat)
	;

	class_<TrainingDataVector>("TrainingDataVector")
		.def("serialize", &TrainingDataVector::serialize)
		.def("deserialize", &TrainingDataVector::deserialize)
		.def("to_list", &TrainingDataVector::to_list)
	;
	class_<TestDataVector>("TestDataVector");

	class_<NaiveClassifierWrapper>("NaiveClassifier", init<>())
		.def("deserialize", &NaiveClassifierWrapper::deserialize)
		.def("getCategory", &NaiveClassifierWrapper::getCategory)
		.def("getCategories", &NaiveClassifierWrapper::getCategories)
		.def("serialize", &NaiveClassifierWrapper::serialize)
		.def("train", &NaiveClassifierWrapper::train)
	;

	class_<TemporaryFactoryWrapper>("TemporaryFactory")
		.def_readonly("attributes", &TemporaryFactoryWrapper::attributes)
		.def_readonly("category", &TemporaryFactoryWrapper::category)
		.def("readTrainingData", &TemporaryFactoryWrapper::readTraining)
		.def("readTestData", &TemporaryFactoryWrapper::readTest)
	;
}
