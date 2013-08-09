#define BOOST_TEST_MAIN
#define BOOST_TEST_MODULE TestModule
#define BOOST_TEST_DYN_LINK

#include <boost/test/unit_test.hpp>

#include "TestData.hpp"
#include "TrainingData.hpp"
#include "TemporaryReader.hpp"
#include "NaiveClassifier.hpp"

using namespace reader;

/*
 * Tests for TestData
 */

BOOST_AUTO_TEST_CASE( TestDataEmpty )
{
	TestData data;
	BOOST_CHECK_EQUAL(data.empty(), true);
}

BOOST_AUTO_TEST_CASE( TestDataEmptyAfterInsert )
{
	TestData data;
	data.insert("kitty");
	BOOST_CHECK_EQUAL(data.empty(), false);
}

BOOST_AUTO_TEST_CASE( TestDataGetAfterInsert )
{
	TestData data;
	data.insert("kitty");
	string obj = data[0];
	BOOST_CHECK_EQUAL(obj, "kitty");
}

/*
 * Tests for TrainingData
 */

BOOST_AUTO_TEST_CASE( TrainingDataGetEmptyCategory )
{
	TrainingData data;
	BOOST_CHECK_EQUAL(data.getCategory(), "");
}

BOOST_AUTO_TEST_CASE( TrainingDataSetCategory )
{
	TrainingData data;
	data.setCategory("doggy");
	BOOST_CHECK_EQUAL(data.getCategory(), "doggy");
}

/*
 * Tests for TemporaryReader
 */

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTestNoFile )
{
	TemporaryReader reader;
	BOOST_REQUIRE_THROW(reader.readTestData("NO-FILE"), ReadingException);
}

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTestWrongFormat )
{
	TemporaryReader reader;
	BOOST_REQUIRE_THROW(reader.readTestData("test_input_00.txt"), 
		ReadingException);
}

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTestCorrectFormat )
{
	TemporaryReader reader;
	vector<TestData> data = reader.readTestData("test_input_01.txt");
	BOOST_CHECK_EQUAL(data.size(), 2);
}

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTestSimilarFormat )
{
	TemporaryReader reader;
	BOOST_REQUIRE_THROW(reader.readTestData("training_input_01.txt"),
		ReadingException);
}

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTrainingNoFile )
{
	TemporaryReader reader;
	BOOST_REQUIRE_THROW(reader.readTrainingData("NO-FILE"), 
		ReadingException);
}

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTrainingWrongFormat )
{
	TemporaryReader reader;
	BOOST_REQUIRE_THROW(reader.readTrainingData("training_input_00.txt"), 
		ReadingException);
}

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTrainingCorrectFormat )
{
	TemporaryReader reader;
	vector<TrainingData> data = reader.readTrainingData("training_input_01.txt");
	BOOST_CHECK_EQUAL(data.size(), 3);
	BOOST_CHECK_EQUAL(data[0].getCategory(), "warrior");
}

BOOST_AUTO_TEST_CASE( TemporaryReaderReadTrainingSimilarFormat )
{
	TemporaryReader reader;
	BOOST_REQUIRE_THROW(reader.readTrainingData("test_input_01.txt"),
		ReadingException);
}

/*
 * Tests for NaiveClassifier
 */

static TrainingData createTrainingData(string *d, int count, string &cat)
{
	TrainingData t;
	for (int i = 0; i < count; i++)
		t.insert(d[i]);
	t.setCategory(cat);
	return t;
}

static TestData createTestData(string *d, int count)
{
	TestData t;
	for (int i = 0; i < count; i++)
		t.insert(d[i]);
	return t;
}

template <int length>
static NaiveClassifier trainClassifier(string attr[][length], string cat[], 
	int count)
{
	NaiveClassifier::TrainingSet trainingSet;
	for (int i = 0; i < count; i++) {
		TrainingData example = createTrainingData(attr[i], length, cat[i]);
		trainingSet.push_back( example );
	}

	NaiveClassifier cl;
	cl.train(trainingSet);
	return cl;
}

BOOST_AUTO_TEST_CASE( NaiveClassifierMajorCategory )
{
	const int exampleCount = 3;
	const int exampleLength = 3;

	string trainAttr[exampleCount][exampleLength] = {
		{"3", "1", "1"},
		{"1", "3", "1"},
		{"1", "1", "3"},
	};
	string trainCat[exampleCount] = {
		"warrior",
		"archer",
		"mage",
	};

	NaiveClassifier cl = trainClassifier(trainAttr, trainCat, exampleCount);

	for (int i = 0; i < exampleCount; i++) {
		TestData test = createTestData(trainAttr[i], exampleLength);
		BOOST_CHECK_EQUAL(cl.getCategory(test), trainCat[i]);
	}
}

BOOST_AUTO_TEST_CASE( NaiveClassifierSerialization )
{
	const int exampleCount = 3;
	const int exampleLength = 3;

	string trainAttr[exampleCount][exampleLength] = {
		{"3", "1", "1"},
		{"1", "3", "1"},
		{"1", "1", "3"},
	};
	string trainCat[exampleCount] = {
		"warrior",
		"archer",
		"mage",
	};

	NaiveClassifier clFirst = trainClassifier(trainAttr, trainCat, exampleCount);
	string serialized = clFirst.serialize();

	NaiveClassifier clSecond;
	clSecond.deserialize(serialized);

	for (int i = 0; i < exampleCount; i++) {
		TestData test = createTestData(trainAttr[i], exampleLength);
		BOOST_CHECK_EQUAL(clSecond.getCategory(test), trainCat[i]);
	}
}