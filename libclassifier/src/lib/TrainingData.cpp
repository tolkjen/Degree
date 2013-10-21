#include <boost/serialization/nvp.hpp>

#include "TrainingData.hpp"

string TrainingData::getCategory()
{
	return category;
}

void TrainingData::setCategory(string s)
{
	category = s;
}
