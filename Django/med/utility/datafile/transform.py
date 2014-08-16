# coding=utf-8

import sys
import random

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

class DistributionNumberTransform:
	def __init__(self, buckets):
		self.buckets = buckets
		self.data = []
		self.calculated = False

	def clone(self):
		return DistributionNumberTransform(self.buckets)

	def put(self, str_value):
		self.data.append(float(str_value))

	def transform(self, str_value):
		if not self.calculated:
			self.calculate()

		number = float(str_value)
		for i, edge in enumerate(self.bucket_edges):
			if number <= edge:
				return str(i)

	def calculate(self):
		bucket_size = len(self.data) / self.buckets
		self.data.sort()
		self.bucket_edges = [(self.data[i*bucket_size] + self.data[i*bucket_size+1]) / 2 for i in range(self.buckets - 1)]
		self.bucket_edges.append(self.data[-1])
		self.calculated = True

class KMeansNumberTransform:
	def __init__(self, k):
		self.k = k
		self.data = []
		self.calculated = False

	def clone(self):
		myself = KMeansNumberTransform(self.k)
		return myself

	def put(self, str_value):
		number = float(str_value)
		self.data.append(number)

	def transform(self, str_value):
		if not self.calculated:
			self.calculate()

		result = 0
		number = float(str_value)
		for i, centroid in enumerate(self.centroids):
			if (abs(number - centroid) < abs(number - self.centroids[result])):
				result = i
		return str(result)

	def calculate(self):
		error = sys.float_info.max
		delta = 0.001

		membership = [0]*len(self.data)
		self.centroids = self.initialize_centroids()

		while True:
			for i in range(len(self.data)):
				for j, centroid in enumerate(self.centroids):
					if abs(self.data[i] - centroid) < abs(self.data[i] - self.centroids[membership[i]]):
						membership[i] = j

			new_error = sum([pow((self.centroids[membership[i]] - self.data[i]), 2) for i in range(len(self.data))]) / len(self.data)
			if float((error - new_error) / new_error) < delta:
				break
			error = new_error

			for i in range(len(self.centroids)):
				elements = [self.data[j] for j in range(len(self.data)) if membership[j] == i]
				if len(elements) > 0:
					self.centroids[i] = sum(elements) / len(elements)

		self.calculated = True

	def initialize_centroids(self):
		return random.sample(self.data, self.k)

class KMeansPPNumberTransform(KMeansNumberTransform):
	def __init__(self, k):
		KMeansNumberTransform.__init__(self, k)

	def initialize_centroids(self):
		first_centroid_index = random.randint(0, len(self.data) - 1)
		centroids = [self.data[first_centroid_index]]
		while len(centroids) < self.k:
			distances = []
			non_centroid_data = [x for x in self.data if not x in centroids]
			for x in non_centroid_data:
				distances.append(min([pow((centroid - x), 2) for centroid in centroids]))
			random_pick = random.uniform(0, sum(distances))
			for i in range(len(distances)):
				if random_pick <= distances[i]:
					centroids.append(non_centroid_data[i])
					break
				random_pick = random_pick - distances[i]
		return centroids

class NumberTransformHelper:
	type_mapping = {
		u"Równy podział dziedziny": RangeNumberTransform,
		u"Równa liczność grup": DistributionNumberTransform,
		u"Metoda K-Średnich": KMeansNumberTransform,
		u"Metoda K-Średnich++": KMeansPPNumberTransform
	}

	@staticmethod
	def create_transform(type_name, argument):
		if not type_name in NumberTransformHelper.get_type_names():
			raise Exception("Transformacja o nazwie " + type_name + " nie istnieje.")
		return NumberTransformHelper.type_mapping[type_name](argument)

	@staticmethod
	def get_type_names():
		return NumberTransformHelper.type_mapping.keys()
