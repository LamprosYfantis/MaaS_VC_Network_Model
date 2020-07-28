# from itertools import count, islice
# b = [1, 2]
# A = {'a': 1, 'b': 2, 'c': 3, 'd': 4, 'e': 5}
# mm = islice(A, 2)
# for k in mm:
#     print(A[k])
# print(str(b))

# print((1200000 - 86399) % 86399)
# print(ValueError)

# if ValueError:
#     print('ok')


from bisect import bisect_left
from operator import itemgetter
import bisect
import random

# A = {(20, 30): 20, (1, 10): 10, (10, 19): 30}
# sorted_dict = sorted(A)
# print(sorted_dict)

# data = list(A.keys())
# print(data)


# def lookup_ip(ip, data):
#     sorted_data = sorted(data, key=itemgetter(0))
#     lower_bounds = [lower for lower, _ in data]
#     index = bisect.bisect(lower_bounds, ip) - 1
#     if index < 0:
#         return None
#     # _, upper = sorted_data[index]
#     return data[index]
# #     # return index if ip <= upper else None


# print(lookup_ip(15, data))          # => None
# # print(lookup_ip(999))         # => 'ZZ'
# # print(lookup_ip(16777216))    # => None
# # print(lookup_ip(1000013824))  # => 'CN'
# # print(lookup_ip(1000400000))  # => 'IN'
# item_count = 100000
# items = [(str(i), random.randint(1, 10)) for i in range(item_count)]
# print(items)

# def find_ge(a, x):                                  # binary search algorithm
#     'Find leftmost item greater than or equal to x'
#     i = bisect_left(a, x)
#     if i != len(a):
#         return a[i]
#     raise ValueError

# A = {(0, 299): 2, (300, 599): 10, (600, 899): 100}

# time = int(300 / 299)
# print(time)
# time_intrv = list(A.keys())[time]
# print(A[time_intrv])

# G = [1, 3, (1, 2, 3), (10, 20, 30), (100, 2, 9)]

# B = (1, 2, 3)

# gama = tuple(G)
# print(gama)

# if B in G:
#     print('ok')
# else:
#     print('no')

# bre = {'a': 1, 'b': 2}

# print(bre['c'])

# print(int(0.23))


A = [0,1]

B=A

print(B)
