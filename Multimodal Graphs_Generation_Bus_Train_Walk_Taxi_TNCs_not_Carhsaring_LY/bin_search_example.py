# # Python code to demonstrate working
# # of binary search in library
from bisect import bisect_left, bisect_right

def find_ge(a, x):
    'Find leftmost item greater than or equal to x'
    i = bisect_left(a, x)
    if i != len(a):
        return a[i]
    raise ValueError

#example
a  = [1, 2, 3, 4.3, 5, 8, 11, 15, 20]
x = int(4)
res = find_ge(a, x)
print(res)
# if res == -1:
#     print("No value smaller than ", x)
# else:
#     print("Largest value smaller than ", x, " is at index ", res)
