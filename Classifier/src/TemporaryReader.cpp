#include <cstdio>

#include "TemporaryReader.hpp"

using namespace reader;

vector<TrainingData> TemporaryReader::readTrainingData(string path)
{
	vector<TrainingData> results;

	FILE *fin = fopen(path.c_str(), "r");
	if (!fin)
		throw ReadingException("Nie można otworzyć pliku");

	int nRows;
	int ret;
	ret = fscanf(fin, "%d", &nRows);
	if (ret != 1)
		throw ReadingException("Nieprawidłowy format pliku");

	char str[8], dex[8], intel[8], cat[16];
	for (int i = 0; i < nRows; i++) {
		ret = fscanf(fin, "%s %s %s %s", &str, &dex, &intel, &cat);
		if (ret != 4)
			throw ReadingException("Nieprawidłowy format pliku");

		TrainingData data;
		data.insert(str);
		data.insert(dex);
		data.insert(intel);
		data.setCategory(cat);

		results.push_back(data);
	}
	fclose(fin);

	return results;
}

vector<TestData> TemporaryReader::readTestData(string path)
{
	vector<TestData> results;

	FILE *fin = fopen(path.c_str(), "r");
	if (!fin)
		throw ReadingException("Nie można otworzyć pliku");

	int nRows;
	int ret;
	ret = fscanf(fin, "%d", &nRows);
	if (ret != 1)
		throw ReadingException("Nieprawidłowy format pliku");

	char str[8], dex[8], intel[8];
	for (int i = 0; i < nRows; i++) {
		ret = fscanf(fin, "%s %s %s", &str, &dex, &intel);
		if (ret != 3)
			throw ReadingException("Nieprawidłowy format pliku");

		TestData data;
		data.insert(str);
		data.insert(dex);
		data.insert(intel);

		results.push_back(data);
	}
	fclose(fin);

	return results;
}
