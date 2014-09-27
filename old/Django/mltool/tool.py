__author__ = 'tolkjen'

from med.utility.datafile.sample import Sample
from sklearn import svm, cross_validation
import sys


def prepare_sample(argv):
    x = Sample.fromFile("D:\\Moje dokumenty\\Documents\\Informatyczne\\Degree\\Test0.xls")

    if len(argv) < 2:
        raise Exception("Wrong number of arguments.")

    if argv[1] == "remove":
        x = x.fix_none_remove()
    elif argv[1] == "mean":
        x = x.fix_none_mean()
    else:
        raise Exception("Unsupported none-fix type.")

    return x


def prepare_svm_classifier(description):
    try:
        num0 = float(description[0])
        num1 = float(description[1])
    except:
        raise Exception("SVM classifier argument is not a number.")

    return svm.SVC(gamma=num0, C=num1)


def prepare_classifier(argv):
    if len(argv) < 3:
        raise Exception("Wrong number of arguments.")

    classifier_description = argv[2].split(':')
    if len(classifier_description) < 1:
        raise Exception("Classifier description must be in form 'name:x:y:z'.")

    if classifier_description[0] == "svm":
        return prepare_svm_classifier(classifier_description[1:])
    else:
        raise Exception("Wrong name of the classifier.")


if __name__ == "__main__":
    try:
        sample = prepare_sample(sys.argv)
    except Exception, e:
        print "Error:", e.message
        print "Usage: python -m mltool.tool <remove/mean>"
        sys.exit(1)

    try:
        classifier = prepare_classifier(sys.argv)
    except Exception, e:
        print "Error:", e.message
        print "Usage: python -m mltool.tool <remove/mean>"
        sys.exit(1)

    data = [attributes for attributes, category in sample.rows()]
    target = [category for attributes, category in sample.rows()]
    scores = cross_validation.cross_val_score(classifier, data, target, cv=10)

    print ""
    print "Number of rows:", len(sample.rows())
    print "Result:", scores.mean()
