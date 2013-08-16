#ifndef __TEMPORARYREADER_H__
#define __TEMPORARYREADER_H__

#include "AbstractReader.hpp"

using namespace std;

namespace reader
{
	class TemporaryReader : public AbstractReader
	{
	public:
		typedef vector<TrainingData> TrainingSet;
		typedef vector<TestData> TestSet;

		TemporaryReader();
		TemporaryReader(int attrCount);

		virtual TrainingSet readTrainingData(string path);
		virtual TestSet readTestData(string path);

	protected:
		int _attrCount;
	};
}

#endif
