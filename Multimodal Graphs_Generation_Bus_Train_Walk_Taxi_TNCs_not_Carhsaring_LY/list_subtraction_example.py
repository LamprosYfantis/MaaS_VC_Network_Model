from operator import sub


a = [1, 2, 3]
b = [1, 2, 3, 4]

diff_list = [a - b for a, b in zip(a, b)]
print(diff_list)

diff_list = list(map(sub, b, a))
print(diff_list)
