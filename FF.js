function seededRandom(seed) {
    let lSeed = seed || 1337;

    return function rd(min=0, max=2147483647) {
        const random = Math.sin(lSeed) * 100;
        const seedDecimal = (random - Math.floor(random)).toFixed(8);
        lSeed = (Math.floor(seedDecimal * 25214903917) + 11) % 2147483647;
        return Math.floor(seedDecimal * (max - min + 1) + min);
    }
}

function robustSolition(K) {
    // 理想孤波分布
    const pIdeal = new Array(K).fill(0);
    pIdeal[0] = 1 / K;
    for (let i = 1; i < K; i++) {
        pIdeal[i] = 1 / (i * (i + 1));
    }

    // 鲁棒孤波分布
    const c = 0.05;
    const delta = 0.05;
    const pRobust = [...pIdeal];

    const R = c * Math.log(K / delta) * Math.sqrt(K);
    const degreeMax = Math.min(Math.max(Math.round(K / R), 2), K);
    // console.log('预处理集期望大小', R, '度数上限', degreeMax);
    const p = new Array(degreeMax).fill(0);

    for (let i = 0; i < degreeMax - 1; i++) {
        p[i] = R / ((i + 1) * K);
    }

    p[degreeMax - 1] = R * Math.log(R / delta) / K;

    for (let i = 0; i < degreeMax; i++) {
        pRobust[i] += p[i];
    }

    const sumPRobust = pRobust.reduce( (a, b) => a + b, 0);
    const normalizedPRobust = pRobust.map(x => x / sumPRobust);

    const maxNum = normalizedPRobust.length - normalizedPRobust.reverse().findIndex(x => x > (0.1 / K));
    normalizedPRobust.reverse();

    const distributionMatrixProb = normalizedPRobust.slice(0, maxNum);
    const tempSum = distributionMatrixProb.reduce( (a, b) => a + b, 0);
    let cumSum = 0;
    return distributionMatrixProb.map(x => {
        cumSum += (x / tempSum);
        return cumSum.toFixed(8);
    }
    );
}

function randChunkNums(k, prob, seed) {
    const r = seededRandom(seed);
    const d = (r(0, 2147483646) / 2147483647).toFixed(8);
    const degree = prob.findIndex(x => x >= d) + 1;
    k -= 1;
    const res = new Set();
    while (res.size < degree) {
        res.add(r(0, k));
    }
    return Array.from(res).sort( (a, b) => a - b);
}

function xor(arr1, arr2) {
    return new Uint8Array(arr1.map( (byte, i) => byte ^ arr2[i]));
}

class Droplet {
    constructor(data, seed, numChunks, padding) {
        this.data = data;
        this.seed = seed;
        this.numChunks = numChunks;
        this.padding = padding;
    }

    chunkNums() {
        return randChunkNums(this.numChunks, this.prob, this.seed);
    }

    getStr() {
        const data = btoa(String.fromCharCode.apply(null, new Uint8Array(this.data)));
        return `${this.seed}|${this.numChunks}|${this.padding}|${data}`;
    }

}

function str2Droplet(s) {
    // 使用split分割字符串，不限制分割次数
    let args = s.split('|');
    let seed = parseInt(args[0], 10);
    let num_chunks = parseInt(args[1], 10);
    let padding = parseInt(args[2], 10);
    // 将第四个及之后的所有部分合并到一起
    let data = args.slice(3).join('|');
    // 使用atob解码base64字符串，并将其转换为Uint8Array
    let decodedData = atob(data);
    let dataArray = new Uint8Array(decodedData.length);
    for (let i = 0; i < decodedData.length; i++) {
        dataArray[i] = decodedData.charCodeAt(i);
    }
    return new Droplet(dataArray, seed, num_chunks, padding);
}

class Fountain {
    constructor(data, chunkSize=32, seed=null) {
        this.data = new Uint8Array(data);
        this.chunkSize = chunkSize;
        this.numChunks = Math.ceil(data.length / chunkSize);
        this.seed = seed;
        this.r = seededRandom(seed);
        this.prob = robustSolition(this.numChunks);
        this.padding = this.numChunks * this.chunkSize - data.length;

        // Add padding
        const paddedData = new Uint8Array(this.numChunks * this.chunkSize);
        paddedData.set(this.data);
        this.data = paddedData;
    }

    droplet() {
        this.updateSeed();
        if (this.numChunks > 1) {
            const chunkNums = randChunkNums(this.numChunks, this.prob, this.seed);
            var data = null;
            for (const num of chunkNums) {
                if (data === null) {
                    data = this.chunk(num);
                } else {
                    data = xor(data, this.chunk(num));
                }
            }
        } else {
            var data = this.data;
        }
        return new Droplet(data,this.seed,this.numChunks,this.padding);
    }

    chunk(num) {
        const start = this.chunkSize * num;
        const end = this.chunkSize * (num + 1);
        return this.data.slice(start, end);
    }

    updateSeed() {
        this.seed = this.r();
    }
}

class Glass {
    constructor(d) {
        this.entries = [];
        this.droplets = [];
        this.numChunks = d.numChunks;
        this.chunks = new Array(this.numChunks).fill(null);
        this.prob = robustSolition(this.numChunks);
        this.padding = d.padding;
        this.addDroplet(d);
    }

    addDroplet(d) {
        if (this.numChunks > 1) {
            d.prob = this.prob;
            this.droplets.push(d);
            const entry = [d.chunkNums(), d.data];
            this.entries.push(entry);
            this.updateEntry(entry);
        } else {
            this.chunks[0] = d.data;
        }

    }

    updateEntry(entry) {
        for (const chunkNum of [...entry[0]]) {
            if (this.chunks[chunkNum] !== null) {
                entry[1] = xor(entry[1], this.chunks[chunkNum]);
                entry[0].splice(entry[0].indexOf(chunkNum), 1);
            }
        }
        if (entry[0].length === 1) {
            this.chunks[entry[0][0]] = entry[1];
            this.entries.splice(this.entries.indexOf(entry), 1);
            for (const d of this.entries) {
                if (d[0].includes(entry[0][0])) {
                    this.updateEntry(d);
                }
            }
        }
    }

    getData() {
        if (this.isDone()) {
            const lastChunk = this.chunks[this.chunks.length - 1];
            this.chunks[this.chunks.length - 1] = lastChunk.slice(0, lastChunk.length - this.padding);
            return new Uint8Array(this.chunks.reduce( (acc, chunk) => {
                acc.push(...chunk);
                return acc;
            }
            , []));
        }
        return new Uint8Array(0);
    }

    isDone() {
        return !this.chunks.includes(null);
    }

    chunksDone() {
        return this.chunks.filter(x => x !== null).length;
    }
}

let b = seededRandom();
for (let i = 0; i < 0; i++) {
    console.log(b());
}

let y = seededRandom();
for (let i = 49; i < 50; i++) {
    let a = robustSolition(2 + i);
    console.log(a);
    for (let j = 0; j < 500; j++) {
        let tmp = y();
        console.log(j, tmp, randChunkNums(2 + i, a, tmp));
    }
}

// 创建一个简单的测试数据
const testData = new Uint8Array([1, 2, 3, 4, 5, 6, 7, 8, 9, 10]);

// 创建一个Fountain实例
const fountain = new Fountain(testData,4);

for (let i = 0; i < 10; i++) {
    // 创建一个Glass实例
    const glass = new Glass(str2Droplet(fountain.droplet().getStr()));

    // 生成和接收droplets直到解码完成
    while (!glass.isDone()) {
        const droplet = fountain.droplet();
        glass.addDroplet(str2Droplet(droplet.getStr()));
        console.log(droplet.getStr());
        console.log(i, `完成度: ${glass.chunksDone()}/${glass.numChunks}`);
    }

    // 获取解码后的数据
    const decodedData = glass.getData();
    console.log('解码后的数据:', Array.from(decodedData));
}
