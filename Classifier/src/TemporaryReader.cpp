#include <iostream>
#include <fstream>

using namespace std;

#include "TemporaryReader.hpp"

using namespace reader;

vector<TrainingData> TemporaryReader::readTrainingData(string path)
{
	vector<TrainingData> results;
	ifstream file(path);

	if (file.is_open()) {
		int nRows;
		file >> nRows;

		double str, dex, intel;
		char cat[64];
		for (int i = 0; i < nRows; i++) {
			file >> str >> dex >> intel >> cat;
			if (!file.good())
				throw ReadingException("Nieprawidłowy format pliku");

			TrainingData data;
			data.insert(str);
			data.insert(dex);
			data.insert(intel);
			data.setCategory(cat);

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
	ifstream file(path);

	if (file.is_open()) {
		int nRows;
		file >> nRows;

		double str, dex, intel;
		for (int i = 0; i < nRows; i++) {
			file >> str >> dex >> intel;
			if (!file.good())
				throw ReadingException("Nieprawidłowy format pliku");

			TestData data;
			data.insert(str);
			data.insert(dex);
			data.insert(intel);

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
