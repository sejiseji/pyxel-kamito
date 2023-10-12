def primenumbers(n):
    prime_list = []
    for i in range(2, n):
        if i > 1:
            for j in range(2, i):
                if (i % j) == 0:
                    break
            else:
                prime_list.append(i)
    return prime_list