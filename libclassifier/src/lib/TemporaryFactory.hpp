#ifndef _TEMPORARYFACTORY_H__
#define _TEMPORARYFACTORY_H__

#include <memory>

#include "DataFactory.hpp"
#include "TemporaryReader.hpp"

using namespace std;
using namespace reader;

class TemporaryFactory : public DataFactory
{
public:
	TemporaryFactory();

	virtual TrainingSet readTrainingData(string path);
	virtual TestSet readTestData(string path);

private:
	shared_ptr<TemporaryReader> _reader;
};

#endif
