#include <boost/python/detail/wrap_python.hpp>
#include <boost/python.hpp>
#include <exception>
#include <string>

#include "TripletBase.h"

using namespace boost::python;
using namespace std;

class WrongContentsException : public exception {
public:
	WrongContentsException(string s) : _triplet(s) {}
	~WrongContentsException() throw() {}
	
	const char *what() const throw() {
		string msg = "Nieprawidłowy kodon: \"" + _triplet + string("\"");
		return msg.c_str();
	}
	
	static void translate(WrongContentsException const &e) {
		PyErr_SetString(PyExc_RuntimeError, e.what());
	}
	
private:
	string _triplet;
};

string get_codons(string sequence) {
    string result;
    
    // go through argument sequence
    for (int i = 0; i < sequence.size(); i += 3) {
		string triplet = sequence.substr(i, 3);
		string protein = TripletBase::get(triplet);
		if (!protein.empty()) {
			result += protein + string(" ");
		} else {
			throw WrongContentsException(triplet);
		}
    }
    
    return result;
}

BOOST_PYTHON_MODULE(libcodon)
{
	register_exception_translator<WrongContentsException>(&WrongContentsException::translate);
    def("get_codons", get_codons);
}
