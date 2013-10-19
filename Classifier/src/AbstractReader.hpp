#ifndef __ABSTRACTREADER_H__
#define __ABSTRACTREADER_H__

#include <exception>
#include "TrainingData.hpp"

using namespace std;

namespace reader
{
	class ReadingException : public exception
	{
	public:
		ReadingException(string msg);
		~ReadingException() throw() {}

		const char* what() const throw();
		static void translate(ReadingException const &e);

	private:
		string _msg;
	};

	class AbstractReader
	{
	public:
		typedef vector<TrainingData> TrainingSet;
		typedef vector<TestData> TestSet;

		virtual TrainingSet readTrainingData(string path) = 0;
		virtual TestSet readTestData(string path) = 0;

	protected:
		int _attrCount;
	};
};

#endif
