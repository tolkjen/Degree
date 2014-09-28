__author__ = 'tolkjen'

import argparse
import sys
import os
from sklearn import cross_validation

from descriptors import PreprocessingDescriptor, ClassificationDescriptor, QuantizationDescriptor, DescriptorException
from input.sample import SampleException


class SplitAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(SplitAction, self).__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values.split(","))


class QuantizationAction(argparse.Action):
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        super(QuantizationAction, self).__init__(option_strings, dest, nargs, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        column_names = values[0].split(",")
        algorithm = values[1]
        params = [float(x) for x in values[2].split(",")]

        quant_array = getattr(namespace, self.dest)
        quant_array.append((column_names, algorithm, params))
        setattr(namespace, self.dest, quant_array)


def parse_arguments():
    parser = argparse.ArgumentParser(description="Processes and classifies data.")
    parser.add_argument("filepath", help="Path to the file containing data for processing.")
    parser.add_argument("classifier", help="Classifier description.")
    parser.add_argument("-p", "--params", help="Classifier parameters.", default=[], action=SplitAction)
    parser.add_argument("-f", "--fix", dest="fix", default="remove", help="Fixing method for missing values.")
    parser.add_argument("-r", "--remove", dest="removed", metavar="cols", default=[], action=SplitAction,
                        help="List of columns which will be removed from file processing.")
    parser.add_argument("-n", "--normalize", dest="normalized", metavar="cols", default=[], action=SplitAction,
                        help="List of columns which will be normalized.")
    parser.add_argument("-q", "--quantize", dest="quant_array", metavar=("columns", "algorithm", "params"), nargs=3,
                        default=[], action=QuantizationAction, help="Adds quantization scheme.")
    return parser.parse_args()


def main():
    args = parse_arguments()

    try:
        quantizers = [QuantizationDescriptor(cols, method, params) for cols, method, params in args.quant_array]
        preprocessor = PreprocessingDescriptor(args.fix, args.removed, args.normalized, quantizers)
        preprocessor.validate()
    except DescriptorException, e:
        print "Incorrect options:", e.message
        sys.exit(1)
    except Exception, e:
        print "Unknown error:", e
        sys.exit(1)

    try:
        sample = preprocessor.generate_sample(args.filepath)
    except SampleException, e:
        print "Processing file failed:", e.message
        sys.exit(1)
    except Exception, e:
        print "Unknown error:", e
        sys.exit(1)

    try:
        classifier_descriptor = ClassificationDescriptor(args.classifier, args.params)
        classifier = classifier_descriptor.create_classifier()
        scores = cross_validation.cross_val_score(classifier, sample.attributes, sample.categories, cv=5)
    except DescriptorException, e:
        print "Can\t perform classification:", e
        sys.exit(1)
    except Exception, e:
        print "Unknown error:", e
        sys.exit(1)

    print "File name: %s" % (os.path.basename(args.filepath))
    print ""
    print "Columns:", ", ".join(sample.columns)
    print "Row count:", sample.nrows
    print "Accuracy: %0.2f (+/- %0.2f)" % (scores.mean(), scores.std() * 2)

if __name__ == "__main__":
    main()
