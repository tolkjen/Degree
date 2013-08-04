#include <boost/serialization/nvp.hpp>

#include "TestData.hpp"

typename TestData::Iterator TestData::begin()
{
	return values.begin();
}

bool TestData::empty()
{
	return values.empty();
}

typename TestData::Iterator TestData::end()
{
	return values.end();
}

void TestData::insert(string s)
{
	values.push_back(s);
}

string& TestData::operator[](int index)
{
	return values[index];
}
