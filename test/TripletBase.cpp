#include "TripletBase.h"

TripletBase *TripletBase::_instance = 0;

TripletBase::TripletBase() {
	_triplets["uuu"] = "fenyloalanina";
	_triplets["uuc"] = "fenyloalanina";
	_triplets["uua"] = "leucyna";
	_triplets["uug"] = "leucyna";
	_triplets["cuu"] = "leucyna";
	_triplets["cuc"] = "leucyna";
	_triplets["cua"] = "leucyna";
	_triplets["cug"] = "leucyna";
	_triplets["auu"] = "izoleucyna";
	_triplets["auc"] = "izoleucyna";
	_triplets["aua"] = "izoleucyna";
	_triplets["aug"] = "metionina";
	_triplets["guu"] = "walina";
	_triplets["guc"] = "walina";
	_triplets["gua"] = "walina";
	_triplets["gug"] = "walina";
	
	_triplets["ucu"] = "seryna";
	_triplets["ucc"] = "seryna";
	_triplets["uca"] = "seryna";
	_triplets["ucg"] = "seryna";
	_triplets["ccu"] = "prolina";
	_triplets["ccc"] = "prolina";
	_triplets["cca"] = "prolina";
	_triplets["ccg"] = "prolina";
	_triplets["acu"] = "treonina";
	_triplets["acc"] = "treonina";
	_triplets["aca"] = "treonina";
	_triplets["acg"] = "treonina";
	_triplets["gcu"] = "alanina";
	_triplets["gcc"] = "alanina";
	_triplets["gca"] = "alanina";
	_triplets["gcg"] = "alanina";
	
	_triplets["uca"] = "tyrozyna";
	_triplets["uac"] = "tyrozyna";
	_triplets["uaa"] = "Ochre";
	_triplets["uag"] = "Amber";
	_triplets["cau"] = "histydyna";
	_triplets["cac"] = "histydyna";
	_triplets["caa"] = "glutamina";
	_triplets["cag"] = "glutamina";
	_triplets["aau"] = "asparagina";
	_triplets["aac"] = "asparagina";
	_triplets["aaa"] = "lizyna";
	_triplets["aag"] = "lizyna";
	_triplets["gau"] = "asparaginian";
	_triplets["gac"] = "asparaginian";
	_triplets["gaa"] = "glutaminian";
	_triplets["gag"] = "glutaminian";
	
	_triplets["ugu"] = "cysteina";
	_triplets["ugc"] = "cysteina";
	_triplets["uga"] = "Opal";
	_triplets["ugg"] = "tryptofan";
	_triplets["cgu"] = "arginina";
	_triplets["cgc"] = "arginina";
	_triplets["cga"] = "arginina";
	_triplets["cgg"] = "arginina";
	_triplets["agu"] = "seryna";
	_triplets["agc"] = "seryna";
	_triplets["aga"] = "arginina";
	_triplets["agg"] = "arginina";
	_triplets["ggu"] = "glicyna";
	_triplets["ggc"] = "glicyna";
	_triplets["gga"] = "glicyna";
	_triplets["ggg"] = "glicyna";
}

string TripletBase::get(string &triplet) {
	if (!_instance) {
		_instance = new TripletBase();
	}
	
	map<string, string>::iterator it = _instance->_triplets.find(triplet);
	if (it != _instance->_triplets.end()) {
		return it->second;
	} else {
		return "";
	}
}
