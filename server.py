import cv2
import pyzbar.pyzbar as pyzbar

import math
import base64


def seeded_random(seed):
    l_seed = seed if seed else 1337

    def rd(min=0, max=2147483647):
        nonlocal l_seed
        random = math.sin(l_seed) * 100
        seed_decimal = round(random - math.floor(random), 8)
        l_seed = (math.floor(seed_decimal * 25214903917) + 11) % 2147483647
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
    degree_max = min(max(round(K / R), 2), K)  # 度数上限
    print('预处理集期望大小', R, '度数上限', degree_max)
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
        distribution_matrix_prob[i] = round(temp_sum, 8)

    return distribution_matrix_prob


def randChunkNums(k, prob, seed):
    r = seeded_random(seed)
    d = round(r(0, 2147483646) / 2147483647, 8)
    d = next(i for i in range(len(prob)) if prob[i] >= d) + 1
    k -= 1
    res = set()
    while len(res) < d:
        res.add(r(0, k))
    res = list(res)
    res.sort()
    return res


def xor(str1, str2):
    return bytes(a ^ b for a, b in zip(str1, str2))


class Droplet:
    def __init__(self, data, seed, num_chunks, padding):
        self.data = data
        self.seed = seed
        self.num_chunks = num_chunks
        self.prob = None
        self.padding = padding

    def chunkNums(self):
        return randChunkNums(self.num_chunks, self.prob, self.seed)

    def getStr(self):
        data = base64.b64encode(self.data).decode()
        return f'{self.seed}|{self.num_chunks}|{self.padding}|{data}'


def str2Droplet(s: str):
    args = s.split('|', maxsplit=3)
    seed = int(args[0])
    num_chunks = int(args[1])
    padding = int(args[2])
    data = base64.b64decode(args[3])
    return Droplet(data, seed, num_chunks, padding)


class Glass:
    def __init__(self, d: Droplet):
        self.entries = []
        self.droplets = []
        self.num_chunks = d.num_chunks
        self.chunks = [None] * self.num_chunks
        self.prob = robust_solition(self.num_chunks)
        self.padding = d.padding
        self.addDroplet(d)

    def addDroplet(self, d):
        if self.num_chunks > 1:
            d.prob = self.prob
            self.droplets.append(d)
            entry = [d.chunkNums(), d.data]
            self.entries.append(entry)
            self.updateEntry(entry)
        else:
            self.chunks[0] = d.data

    def updateEntry(self, entry):
        for chunk_num in entry[0]:
            if self.chunks[chunk_num] is not None:
                entry[1] = xor(entry[1], self.chunks[chunk_num])
                entry[0].remove(chunk_num)
        if len(entry[0]) == 1:
            self.chunks[entry[0][0]] = entry[1]
            self.entries.remove(entry)
            for d in self.entries:
                if entry[0][0] in d[0]:
                    self.updateEntry(d)

    def getData(self):
        if self.isDone():
            self.chunks[-1] = self.chunks[-1][:-self.padding]
            return b''.join(self.chunks)
        return b''

    def isDone(self):
        return None not in self.chunks

    def chunksDone(self):
        return sum(1 for x in self.chunks if x is not None)


camera = cv2.VideoCapture(1)  # 0 表示前置
cv2.namedWindow('zbar', cv2.WINDOW_NORMAL)
size = (int(camera.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2, int(camera.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2)
print(size, cv2.resizeWindow('zbar', size[0], size[1]))

g = None
try:
    while True:
        ret, frame = camera.read()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        cv2.imshow('zbar', gray)
        barcodes = pyzbar.decode(gray)
        if barcodes:
            for barcode in barcodes:
                data = barcode.data.decode('utf-8')
                print(data)
                d = str2Droplet(data)
                if g:
                    g.addDroplet(d)
                else:
                    g = Glass(d)
                print(f'完成度: {g.chunksDone()}/{g.num_chunks}')
        c = cv2.waitKey(500)  # ms
        if c == 27 or (g and g.isDone()):
            break
finally:
    camera.release()
    cv2.destroyAllWindows()

if g and g.isDone():
    with open('qr.dl', 'wb') as f:
        f.write(g.getData())
