#include <boost/python/detail/wrap_python.hpp>
#include <boost/python.hpp>

#include "AbstractReader.hpp"

using namespace reader;

ReadingException::ReadingException(string msg) 
{
	_msg = msg;
}

const char* ReadingException::what() const throw()
{
	return _msg.c_str();
}

void ReadingException::translate(ReadingException const &e)
{
	PyErr_SetString(PyExc_RuntimeError, e.what());
}
