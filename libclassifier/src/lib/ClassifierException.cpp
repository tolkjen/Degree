#include <boost/python/detail/wrap_python.hpp>
#include <boost/python.hpp>

#include "ClassifierException.hpp"

ClassifierException::ClassifierException(string msg)
	: _msg(msg)
{
}

const char* ClassifierException::what() const throw() {
	return _msg.c_str();
}

void ClassifierException::translate(ClassifierException const &e) {
	PyErr_SetString(PyExc_RuntimeError, e.what());
}
