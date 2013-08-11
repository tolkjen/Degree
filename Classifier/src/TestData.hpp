#ifndef __TESTDATA_H__
#define __TESTDATA_H__

#include <boost/serialization/vector.hpp>

#include <vector>
#include <string>

using namespace std;

class TestData
{
public:
	friend class boost::serialization::access;
	typedef vector<double>::iterator Iterator;

public:
	Iterator begin();
	bool empty();
	Iterator end();
	void insert(double s);
	double& operator[] (int index);

	template<class Archive> void serialize(Archive &ar, 
		const unsigned int version)
	{
		ar & BOOST_SERIALIZATION_NVP(values);
	}

private:
	vector<double> values;
};

#endif
