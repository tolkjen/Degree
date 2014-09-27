import transform

t = transform.KMeansPPNumberTransform(3)
t.put(1)
t.put(2)
t.put(30)
t.put(32)
t.put(100)
t.put(111)
print t.transform(1)
print t.transform(31)
print t.transform(110)
