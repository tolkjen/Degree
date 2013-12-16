#include <boost/python.hpp>

#include <faif/learning/NaiveBayesian.hpp>
#include <faif/learning/DecisionTree.hpp>
#include <faif/learning/KNearestNeighbor.hpp>

#include "FaifClassifierAdapter.hpp"
#include "ClassifierException.hpp"

using namespace boost::python;
using namespace faif;
using namespace faif::ml;

BOOST_PYTHON_MODULE(classifier)
{
	register_exception_translator<ClassifierException>
		(&ClassifierException::translate);

	typedef NaiveBayesian<ValueNominal<string>> NB;
	class_<FaifClassifierAdapter<NB>>("NaiveClassifier", init<boost::python::list>())
		.def("train", &FaifClassifierAdapter<NB>::train)
		.def("classify", &FaifClassifierAdapter<NB>::classify)
	;

	typedef DecisionTree<ValueNominal<string>> TR;
	class_<FaifClassifierAdapter<TR>>("TreeClassifier", init<boost::python::list>())
		.def("train", &FaifClassifierAdapter<TR>::train)
		.def("classify", &FaifClassifierAdapter<TR>::classify)
	;

	typedef KNearestNeighbor<ValueNominal<string>> KNN;
	class_<FaifClassifierAdapter<KNN>>("KNNClassifier", init<boost::python::list>())
		.def("train", &FaifClassifierAdapter<KNN>::train)
		.def("classify", &FaifClassifierAdapter<KNN>::classify)
	;
}
