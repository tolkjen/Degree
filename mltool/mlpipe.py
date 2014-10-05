__author__ = 'tolkjen'

import argparse
import sys
from sklearn import cross_validation

from descriptors import PreprocessingDescriptor, ClassificationDescriptor, QuantizationDescriptor, DescriptorException
from input.sample import SampleException
from input.xlsfile import XlsFile


class MlPipeResult:
    def __init__(self, row_count, accuracy_score, accuracy_std, columns):
        self.nrows = row_count
        self.accuracy_score = accuracy_score
        self.accuracy_std = accuracy_std
        self.columns = columns


class MlPipe:

    class ParserException(Exception):
        def __init__(self, msg):
            self.message = msg

        def __str__(self):
            return self.message

    class SplitAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super(MlPipe.SplitAction, self).__init__(option_strings, dest, nargs, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            setattr(namespace, self.dest, values.split(","))

    class QuantizationAction(argparse.Action):
        def __init__(self, option_strings, dest, nargs=None, **kwargs):
            super(MlPipe.QuantizationAction, self).__init__(option_strings, dest, nargs, **kwargs)

        def __call__(self, parser, namespace, values, option_string=None):
            column_names = values[0].split(",")
            algorithm = values[1]
            params = []
            for x in values[2].split(","):
                try:
                    float_value = float(x)
                except:
                    raise MlPipe.ParserException("Argument '%s' is not a number." % x)
                params += [float_value]

            quant_array = getattr(namespace, self.dest)
            quant_array.append((column_names, algorithm, params))
            setattr(namespace, self.dest, quant_array)

    def __init__(self, arguments):
        self._arguments = arguments

    def produce(self):
        args = self._parse_arguments()

        quantizers = [QuantizationDescriptor(cols, method, params) for cols, method, params in args.quant_array]
        preprocessor = PreprocessingDescriptor(args.fix, args.removed, args.normalized, quantizers)
        preprocessor.validate()

        classifier_descriptor = ClassificationDescriptor(args.classifier, args.params)
        classifier_descriptor.validate()

        sample = preprocessor.generate_sample(XlsFile.load(args.filepath))
        classifier = classifier_descriptor.create_classifier()
        scores = cross_validation.cross_val_score(classifier, sample.attributes, sample.categories, cv=5, scoring="f1")

        return MlPipeResult(sample.nrows, scores.mean(), scores.std(), sample.columns)

    def _parse_arguments(self):
        parser = argparse.ArgumentParser(description="Processes and classifies data.")
        parser.add_argument("filepath", help="Path to the file containing data for processing.")
        parser.add_argument("classifier", help="Classifier description.")
        parser.add_argument("-p", "--params", help="Classifier parameters.", default=[],
                            action=MlPipe.SplitAction)
        parser.add_argument("-f", "--fix", dest="fix", default="remove", help="Fixing method for missing values.")
        parser.add_argument("-r", "--remove", dest="removed", metavar="cols", default=[],
                            action=MlPipe.SplitAction,
                            help="List of columns which will be removed from file processing.")
        parser.add_argument("-n", "--normalize", dest="normalized", metavar="cols", default=[],
                            action=MlPipe.SplitAction,
                            help="List of columns which will be normalized.")
        parser.add_argument("-q", "--quantize", dest="quant_array", metavar=("columns", "algorithm", "params"), nargs=3,
                            default=[], action=MlPipe.QuantizationAction, help="Adds quantization scheme.")
        return parser.parse_args(self._arguments)


if __name__ == "__main__":
    app = MlPipe(sys.argv[1:])

    try:
        result = app.produce()
    except DescriptorException, e:
        print "Incorrect arguments: %s" % e
    except MlPipe.ParserException, e:
        print "Incorrect arguments: %s" % e
    except SampleException, e:
        print "Preprocessing data failed: %s" % e
    except Exception, e:
        print "Unknown error: %s" % e
    else:
        print ""
        print "Machine Learning Pipe"
        print "---------------------"
        print ""
        print "Columns: %s" % ", ".join(result.columns)
        print "Number of rows: %d" % result.nrows
        print "Classification accuracy: %0.2f (+/- %0.2f)" % (result.accuracy_score, result.accuracy_std * 2.0)
