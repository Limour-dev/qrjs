import math


def seeded_random(seed):
    l_seed = seed

    def rd(min=0, max=2147483647):
        nonlocal l_seed
        random = math.sin(l_seed) * 10000
        seed_decimal = random - math.floor(random)
        l_seed = (math.floor(seed_decimal * 2147483647) * 25214903917 + 11) % 1000000001339
        return math.floor(seed_decimal * (max - min + 1) + min)

    return rd


def robust_solition(K):
    # 理想孤波分布
    p_ideal = [0] * K
    p_ideal[0] = 1 / K
    for i in range(1, K):
        p_ideal[i] = 1 / (i * (i + 1))

    # 鲁棒孤波分布
    c = 0.05  # 参数
    delta = 0.05  # 保证译码成功概率为 1-delta
    p_robust = p_ideal.copy()

    R = c * math.log(K / delta) * math.sqrt(K)
    degree_max = round(K / R)  # 度数上限
    p = [0] * degree_max  # 度分布概率矩阵

    for i in range(degree_max - 1):
        p[i] = R / ((i + 1) * K)

    p[degree_max - 1] = R * math.log(R / delta) / K

    # 鲁棒孤波分布为p与p_ideal相加然后归一化
    for i in range(degree_max):
        p_robust[i] += p[i]

    sum_p_robust = sum(p_robust)
    p_robust = [x / sum_p_robust for x in p_robust]

    # 找到最后一个大于 0.1/packet_num 的元素的索引 + 1
    max_num = next(i for i in range(len(p_robust) - 1, -1, -1) if p_robust[i] > (0.1 / K)) + 1

    distribution_matrix_prob = p_robust[:max_num]
    temp_sum = sum(distribution_matrix_prob)
    distribution_matrix_prob = [x * (1 / temp_sum) for x in distribution_matrix_prob]
    temp_sum = 0
    for i in range(max_num):
        temp_sum += distribution_matrix_prob[i]
        distribution_matrix_prob[i] = temp_sum

    return distribution_matrix_prob


def randChunkNums(k, prob, seed):
    r = seeded_random(seed)
    d = r(0, 2147483646) / 2147483647
    d = next(i for i in range(len(prob)) if prob[i] >= d) + 1
    res = {r(0, k) for i in range(d)}
    while len(res) < d:
        res.add(r(0, k))
    return res


a = robust_solition(512)
b = seeded_random(1337)
for i in range(10):
    x = b()
    print(x, randChunkNums(512, a, x))
