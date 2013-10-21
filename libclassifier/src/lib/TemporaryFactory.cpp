#include "TemporaryFactory.hpp"

TemporaryFactory::TemporaryFactory()
{
	string attr[] = {"Str", "Dex", "Int"};
	int count = sizeof(attr) / sizeof(string);

	_attributes = StringVector(attr, attr + count);
	_category = "Class";

	_reader = shared_ptr<TemporaryReader>(new TemporaryReader(count));
}

TemporaryFactory::TrainingSet
TemporaryFactory::readTrainingData(string path)
{
	return _reader->readTrainingData(path);
}

TemporaryFactory::TestSet
TemporaryFactory::readTestData(string path)
{
	return _reader->readTestData(path);
}
