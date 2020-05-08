n = int(input())
data = sorted([int(x) for x in input().split()])
a = [[1, -1]]
for i in range(len(data) - 1):
    if data[i] == data[i+1]:
        a[-1][0] += 1
        a[-1][1] = data[i]
    else:
        a.append([1, data[i+1]])
        if len(a) > 2:
            a.sort()
            if a[0][0] != a[1][0]:
                print(a[0][1])
                break
            if a[-1][0] != a[1][0]:
                print(a[-1][1])
                break
