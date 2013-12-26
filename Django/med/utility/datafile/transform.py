import sys

class StringTransform:
	def clone(self):
		myself = StringTransform()
		return myself

	def put(self, str_value):
		pass

	def transform(self, str_value):
		return str_value

class RangeNumberTransform:
	def __init__(self, number):
		self.maximum_value = sys.float_info.min
		self.minimum_value = sys.float_info.max
		self.buckets = number

	def clone(self):
		myself = RangeNumberTransform(self.buckets)
		return myself

	def put(self, str_value):
		number = float(str_value)
		self.maximum_value = max(self.maximum_value, number)
		self.minimum_value = min(self.minimum_value, number)

	def transform(self, str_value):
		number = float(str_value)
		bucket = int(self.buckets * (number - self.minimum_value) / (self.maximum_value - self.minimum_value))
		return str(bucket)
