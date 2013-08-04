#ifndef __TRAININGDATA_H__
#define __TRAININGDATA_H__

#include <boost/serialization/base_object.hpp>

#include "TestData.hpp"

using namespace std;

class TrainingData : public TestData
{
public:
	friend class boost::serialization::access;

public:
	string getCategory();
	void setCategory(string s);

	template<class Archive> void serialize(Archive & ar, 
		const unsigned int version)
	{
		ar & BOOST_SERIALIZATION_BASE_OBJECT_NVP(TestData);
		ar & BOOST_SERIALIZATION_NVP(category);
	}

private:
	string category;
};

#endif
