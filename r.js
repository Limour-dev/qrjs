function seededRandom(seed, min, max) {
    var l_seed = seed;
    function rd() {
        const random = Math.sin(l_seed) * 10000;
        const seedDecimal = random - Math.floor(random);
        l_seed = Math.floor(seedDecimal * 2147483647);
        return Math.floor(seedDecimal * (max - min + 1) + min);
    }
    return rd;
}

const seed = 12345;
const min = 1;
const max = 100;
const r = seededRandom(seed, min, max);
for (let i = 0; i < 100; i++) {
    console.log(r());
}