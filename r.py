import math

def seeded_random(seed, min, max):
    l_seed = seed
    def rd():
        nonlocal l_seed
        random = math.sin(l_seed) * 10000
        seed_decimal = random - math.floor(random)
        l_seed = math.floor(seed_decimal * 2147483647)
        return math.floor(seed_decimal * (max - min + 1) + min)
    return rd

seed = 12345
min = 1
max = 100
r = seeded_random(seed, min, max)
for i in range(100):
    print(r())