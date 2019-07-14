from itertools import count, islice
b = [1, 2]
A = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
mm = islice(A, 2)
for k in mm:
    print(A[k])
print(str(b))
