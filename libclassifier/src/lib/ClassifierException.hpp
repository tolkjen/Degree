#ifndef __CLASSIFIEREXCEPTION_H__
#define __CLASSIFIEREXCEPTION_H__

#include <exception>

using namespace std;

class ClassifierException : public exception {
public:
	ClassifierException(string msg);
	~ClassifierException() throw() {}

	const char* what() const throw();
	static void translate(ClassifierException const &e);

private:
	string _msg;
};

#endif
