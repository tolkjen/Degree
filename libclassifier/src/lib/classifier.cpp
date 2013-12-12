#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>

#include <faif/learning/Classifier.hpp>
#include <faif/learning/NaiveBayesian.hpp>
#include <faif/learning/DecisionTree.hpp>

#include "FaifClassifierAdapter.hpp"

using namespace boost::python;
using namespace faif;
using namespace faif::ml;

BOOST_PYTHON_MODULE(classifier)
{
	class_<FaifClassifierAdapter<NaiveBayesian>>("NaiveClassifier", init<boost::python::list>())
		.def("train", &FaifClassifierAdapter<NaiveBayesian>::train)
		.def("classify", &FaifClassifierAdapter<NaiveBayesian>::classify)
	;

	class_<FaifClassifierAdapter<DecisionTree>>("TreeClassifier", init<boost::python::list>())
		.def("train", &FaifClassifierAdapter<DecisionTree>::train)
		.def("classify", &FaifClassifierAdapter<DecisionTree>::classify)
	;
}
