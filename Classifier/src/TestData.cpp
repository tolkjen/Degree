#include <boost/serialization/nvp.hpp>

#include "TestData.hpp"

TestData::Iterator TestData::begin()
{
	return values.begin();
}

bool TestData::empty()
{
	return values.empty();
}

TestData::Iterator TestData::end()
{
	return values.end();
}

void TestData::insert(double s)
{
	values.push_back(s);
}

double& TestData::operator[](int index)
{
	return values[index];
}

int TestData::size()
{
	return values.size();
}