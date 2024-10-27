import json
import random
from math import ceil


def charN(str, N):
    if N < len(str):
        return str[N]
    return 'X'


def xor(str1, str2):
    length = max(len(str1), len(str2))
    return ''.join(chr(ord(charN(str1, i)) ^ ord(charN(str2, i))) for i in range(length))


def randChunkNums(num_chunks):
    size = random.randint(1, min(5, num_chunks))
    return random.sample(range(num_chunks), size)


class Droplet:
    def __init__(self, data, seed, num_chunks):
        self.data = data
        self.seed = seed
        self.num_chunks = num_chunks

    def chunkNums(self):
        random.seed(self.seed)
        return randChunkNums(self.num_chunks)

    def toString(self):
        return json.dumps(
            {
                'seed': self.seed,
                'num_chunks': self.num_chunks,
                'data': self.data
            })


class Fountain:
    def __init__(self, data, chunk_size=32, seed=None):
        self.data = data
        self.chunk_size = chunk_size
        self.num_chunks = int(ceil(len(data) / float(chunk_size)))
        self.seed = seed
        random.seed(seed)

    def droplet(self):
        self.updateSeed()
        chunk_nums = randChunkNums(self.num_chunks)
        data = None
        for num in chunk_nums:
            if data is None:
                data = self.chunk(num)
            else:
                data = xor(data, self.chunk(num))

        return Droplet(data, self.seed, self.num_chunks)

    def chunk(self, num):
        start = self.chunk_size * num
        end = min(self.chunk_size * (num + 1), len(self.data))
        return self.data[start:end]

    def updateSeed(self):
        self.seed = random.randint(0, 2 ** 31 - 1)
        random.seed(self.seed)


class Glass:
    def __init__(self, num_chunks):
        self.entries = []
        self.droplets = []
        self.num_chunks = num_chunks
        self.chunks = [None] * num_chunks

    def addDroplet(self, d):
        self.droplets.append(d)
        entry = [d.chunkNums(), d.data]
        self.entries.append(entry)
        self.updateEntry(entry)

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

    def getString(self):
        return ''.join(x or ' _ ' for x in self.chunks)

    def isDone(self):
        return None not in self.chunks

    def chunksDone(self):
        count = 0
        for c in self.chunks:
            if c is not None:
                count += 1
        return count


m = """
Fountain codes provide a way for data to be transmitted across a lossy network connection from a single source to many users. The name "fountain code" arises because fountain codes behave analogously to a fountain. A file being transmitted is analogous to a glass of water from the fountain. To fill the glass (or reconstruct the file), you need to catch enough droplets from the fountain such that your glass becomes full. It isn't important which droplets of water you catch in your glass; once you have enough, the glass is full (and the file can be reconstructed). Fountain codes work in the same way, but with information instead of water. The data being transferred can be algorithmically encoded as an arbitrarily large number of chunks, or droplets, that can be sent over the network. The receiving client then needs to receive some number of these droplets in order to reconstruct the original file. It doesn't matter which droplets are received or in what order they are received, and it doesn't matter which are lost during transmission. This is the beauty of fountain codes. As long as a sufficient number of droplets are received, the original file can be reconstructed completely.
We'll explore the motivation behind fountain codes, how these codes are implemented, and why their properties can be useful for file transfer over the internet.
One application that at a glance seems to merit use of fountain codes is torrent sites. For users looking to download large files over a possibly temperamental connection, the fountain code seems ideal. Even if the connection is lost for a substantial period of time, which may be unavoidable with peer-to-peer connections, the fountain code will continue to work without the need for sending confirmation bits indicating that packets have been received. The result is that a file distributor can start a connection with any user, and they can start spewing out droplets for a particular file; they are the fountain. If the client stops catching the droplets, someone else with the file can apply the same algorithm to continue broadcasting the file without knowing how much of the file has been received or which parts of the previous transmission were dropped. While this seems ideal for peer to peer file transfer, it has one fatal flaw that fountain codes cannot resolve.
The flaw I speak of is a security vulnerability. With applications like BitTorrent, a sha1 hash of the file being transferred is used to verify that the sender of the file can be trusted to send the file, instead of sending malicious software to run on your computer or a corrupted version of the file. We are able to verify that the data being transmitted can be trusted using by comparing the hash of the file to the hash we received from a trusted source. When using fountain codes, the droplets that are sent over the network cannot be verified, because they are generated dynamically during transmission, and there is an arbitrarily large number of these chunks. It is therefore infeasible to precompute the hash of all possible droplets at the start of the transmission. One solution for this is to send the hash of the entire file, but that cannot be checked until the transmission has completed, which is too late in the process to be practical. Ideally we would be able to detect corrupt files during the transmission, like we can do when the file is transmitted sequentially, but unfortunately straightforward application of fountain codes does not allow this.
The most remarkable aspect of fountain codes is that any droplets can be caught and the file can still be reconstructed. To see how this is possible, we look now at one implementation of fountain codes.
The encoding scheme for this implementation is simple. First, the file is broken into chunks that will be used to create the droplets for the fountain. We use 32 character chunks by default for this implementation, but any size could be used. Larger chunks are more likely to be dropped on the lossy connection we're using, but decrease the number of droplets that have to be received, and so the chunk size is a tradeoff that must be carefully balanced. For each droplet that will be transmitted, we will select some number of these chunks, and XOR them together. The number of chunks to combine in this manner also affects the performance of the algorithm; in our implementation we choose a small number (single digit small) at random for the number of chunks for a particular droplet. Suppose for our first droplet we choose chunks 1, 3, and 7. These chunks are XOR'd together and the result is transmitted over the network along with enough information for the receiving client to figure out which chunks were included.
There are two ways to supply this information. The first, and simplest, is to include the chunk numbers in the transmitted droplet. With larger numbers of chunks, this amount of information could be prohibitively large, and since the number of chunks in a droplet varies, this method would complicate the droplet protocol because it would no longer be a fixed width protocol. The second method of transmitting the chunk numbers is for the sender and receiver to agree on a random number generator that will be used to generate the chunk numbers. The sender then merely includes the seed used to create the chunk numbers inside the droplet. When the droplet is caught, the receiving client then uses the same random number generator with the same seed to determine which chunks were included in the droplet.
As droplets are caught, a client can begin decoding the data and recovering the original chunks. Here is the method for doing so. As droplets are caught, the receiving client stores them all. They need sufficient information to determine the contents of each chunk of the original file uniquely. Suppose the receiving client has droplets with chunk numbers (1, 3, 7), (1, 3, 4), and (1, 4, 7). Then the XOR of these three chunks will produce precisely chunk 1 of the original file. The algorithm works by having the client simply wait until it has sufficient information to reconstruct all of the chunks. These are then concatenated together to produce the original file. However, implementing this method of reconstruction naively is prohibitively slow due to the number of possible combinations of droplets. Instead, the algorithm waits for droplets that contain single chunks. These are used to determine the contents of sum chunks, and are used to puzzle apart the contents of other droplets. If we have three droplets with chunk numbers (1), (1, 2), and (1, 2, 3) then chunks 1, 2, and 3 can all be determined in this manner.
I implemented the encoding and decoding algorithms here. I have set up a server as a fountain at fountain.herokuapp.com. You can watch as the web client receives chunks from the fountain and is slowly able to reconstruct the original data, which I chose to be this essay. I include the source code in the attached appendix, and it is also available on GitHub at https://github.com/dbieber/fountaincode.
With this algorithm implemented, I was able to examine its efficiency some. Experimentally I've found that the client typically has to receive about 4 times the amount of data being transferred before being able to reconstruct the entire file. This implementation is not the industry standard, but it is the easiest implementation of fountain codes to implement and to explain. By changing the method of random number selection, fountain codes can be improved. These improvements still rely on the model of catching droplets, but are more suitable to real world applications.
However, fountain codes have the downside of transmitting files only in their entirety. If insufficient droplets are received, there is no guarantee that any continuous part of the file will be readable. Other methods exist for applications where it would be better to receive the file in continuous segments. For such applications, such as watching YouTube videos, streaming data is more applicable. The water analogues never seem to end.
""".strip()

f = Fountain(m)

glasses = {}


def getGlass(id):
    id = int(id)
    g = None
    if id not in glasses:
        g = Glass(f.num_chunks)
        glasses[id] = g
    return glasses[id]


def fillAmt(id, amt):
    id = int(id)
    amt = int(amt)

    g = getGlass(id)
    for i in range(amt):
        g.addDroplet(f.droplet())


def glass(id):
    id = int(id)
    g = getGlass(id)
    message = "%d of %d chunks reconstructed." % (g.chunksDone(), g.num_chunks)

    return ['glass.html',
            len(g.droplets),
            message,
            g.getString(),
            id]

import time
for _i in range(1000):
    fillAmt(_i, 512)
    print(glass(_i))
    time.sleep(0.5)
