#include <iostream>
#include <fstream>

using namespace std;

#include "TemporaryReader.hpp"

using namespace reader;

TemporaryReader::TemporaryReader(int attrCount)
{
	_attrCount = attrCount;
}

vector<TrainingData> TemporaryReader::readTrainingData(string path)
{
	vector<TrainingData> results;
	vector<double> attrValues;
	string category;

	attrValues.resize(_attrCount);

	ifstream file(path);
	if (file.is_open()) {
		int nRows;
		file >> nRows;

		for (int i = 0; i < nRows; i++) {
			for (int j = 0; j < _attrCount; j++)
				file >> attrValues[j];
			file >> category;

			if (!file.good())
				throw ReadingException("Nieprawidłowy format pliku");

			TrainingData data;
			for (double& value : attrValues)
				data.insert(value);
			data.setCategory(category);

			results.push_back(data);
		}
	} else {
		throw ReadingException("Nieprawidłowy format pliku");
	}

	char error_buffer[128];
	file >> error_buffer;
	if (file.good())
		throw ReadingException("Nieprawidłowy format pliku");

	file.close();
	return results;
}

vector<TestData> TemporaryReader::readTestData(string path)
{
	vector<TestData> results;
	vector<double> attrValues;

	attrValues.resize(_attrCount);

	ifstream file(path);
	if (file.is_open()) {
		int nRows;
		file >> nRows;

		for (int i = 0; i < nRows; i++) {
			for (int j = 0; j < _attrCount; j++)
				file >> attrValues[j];

			if (!file.good())
				throw ReadingException("Nieprawidłowy format pliku");

			TestData data;
			for (double& value : attrValues)
				data.insert(value);

			results.push_back(data);
		}
	} else {
		throw ReadingException("Nieprawidłowy format pliku");
	}

	char error_buffer[128];
	file >> error_buffer;
	if (file.good())
		throw ReadingException("Nieprawidłowy format pliku");

	file.close();
	return results;
}
