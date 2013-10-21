#include "DataFactory.hpp"

DataFactory::DataFactory()
{
	_attributes = vector<string>();
	_category = "";
}

DataFactory::StringVector
DataFactory::attributes()
{
	return _attributes;
}

string DataFactory::category()
{
	return _category;
}
