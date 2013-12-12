#include <boost/python.hpp>
#include <boost/python/stl_iterator.hpp>

#include "SuperNaiveClassifier.hpp"

using namespace boost::python;

BOOST_PYTHON_MODULE(classifier)
{
	class_<SuperNaiveClassifier>("SuperClassifier", init<boost::python::list>())
		.def("train", &SuperNaiveClassifier::train)
		.def("classify", &SuperNaiveClassifier::classify)
	;
}
