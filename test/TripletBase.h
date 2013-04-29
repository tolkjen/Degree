#ifndef TRIPLET_BASE_H
#define TRIPLET_BASE_H

#include <string>
#include <map>

using namespace std;

class TripletBase {
public:
	static string get(string &triplet);
	
private:
	TripletBase();
	static TripletBase *_instance;
	map<string, string> _triplets;
};

#endif
