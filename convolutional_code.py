from typing import List


class ConvolutionalCode:

    def __init__(self, generators: tuple):
        self.gens = self.fixgens(generators)
        self.l = len(max(self.gens, key=lambda p: len(p))) - 1
        self.regis = "0" * (self.l)

    def fixgens(self, generators):
        gens = generators
        genslist = []
        for i in range(len(gens)):
            genslist.append(str(bin(gens[i])))
            genslist[i] = genslist[i][2::]
        l = len(max(genslist, key=lambda p: len(p)))
        for i in range(len(genslist)):
            if l > len(genslist[i]):
                genslist[i] = "0" * (l - len(genslist[i])) + genslist[i]
        return tuple(genslist)

    def hammdis(self, x1, y1):
        dis = 0
        for i in range(len(x1)):
            if x1[i] != y1[i]:
                dis = dis + 1
        return dis

    def makeoutstr(self, output):
        nout = ""
        for m in output:
            nout = nout + m
        return nout

    def makesod(self, data):
        initkey = "0" * self.l
        sod = {initkey: [[0], [], [initkey]]}  # sod= state options dict
        nstates = {}
        states = []
        for i in range(self.l):
            for key in sod:
                for n in range(2):
                    nkey = str(n) + key[:-1:]
                    output = self.calc(str(n), key)
                    output = self.makeoutstr(output)
                    dis = sod.get(key)[0][0] + self.hammdis(output, data[i])
                    path = [output] + sod.get(key)[1]
                    states = [nkey] + sod.get(key)[2]
                    nstates.update({nkey: [[dis], path, states]})

            sod.update(nstates)
        return sod

    def calc(self, inp, state):
        gens = list(self.gens)
        num = inp + state
        output = []
        for i in range(len(gens)):
            gens[i] = gens[i][::-1]
        for i in gens:
            subsum = 0
            for n in range(len(i)):
                if i[n] == "1":
                    subsum = subsum + int(num[n])
            output = output + [str(subsum % 2)]
        return output

    def encode(self, data: bytes) -> List[int]:
        self.regis = "0" * (self.l)
        ndata = data
        bitlist = []
        for i in range(len(ndata)):
            x = bin(ndata[i])
            x = x[2::]
            x = x.zfill(8)
            while len(x) > 0:
                bitlist = bitlist + [x[0]]
                x = x[1::]
        bitlist = bitlist + ["0"] * self.l  # bytes to bits

        gens = list(self.gens)
        regis = self.regis
        output = []
        for i in range(len(gens)):
            gens[i] = gens[i][::-1]  # flip

        while len(bitlist) > 0:
            output = output + self.calc(bitlist[0], regis)
            regis = bitlist[0] + regis
            regis = regis[:-1:]
            bitlist = bitlist[1::]
        for i in range(len(output)):
            output[i] = int(output[i])
        return output

    def decode(self, data: List[int]) -> (bytes, int):
        data = data
        gennum = len(self.gens)
        divdata = []

        for i in range(0, len(data), gennum):
            nitem = ""
            for n in range(0, gennum):
                nitem = nitem + str(data[i + n])
            divdata = divdata + [nitem]
        sod = self.makesod(divdata[:self.l:])
        divdata = divdata[self.l::]
        for i in range(len(divdata)):
            nphasekeys = {}
            for key in sod:
                key0 = [key[1::] + "0"]
                output0 = self.calc(key[0], key0[0])
                output0 = self.makeoutstr(output0)
                tdis = sod.get(key0[0])[0][0] + self.hammdis(output0, divdata[i])
                key0 = key0 + [tdis] + [[output0] + sod.get(key0[0])[1]]
                key1 = [key[1::] + "1"]
                output1 = self.calc(key[0], key1[0])
                output1 = self.makeoutstr(output1)
                tdis = sod.get(key1[0])[0][0] + self.hammdis(output1, divdata[i])
                key1 = key1 + [tdis] + [[output1] + sod.get(key1[0])[1]]  # making the two possibale ways to get to key
                if key0[1] < key1[1]:
                    nphasekeys.update({key: [[key0[1]], key1[2], [key] + sod.get(key0[0])[2]]})
                else:
                    nphasekeys.update({key: [[key1[1]], key0[2], [key] + sod.get(key1[0])[2]]})
            sod.update(nphasekeys)
        print(sod.get("00"))
        bestval = min(sod.values(), key=lambda k: k[0][0])
        states = bestval[2]
        states = states[::-1]
        decoded = []
        while len(states) > 1:
            if ("1" + states[0][:-1:]) == states[1]:
                decoded = decoded + [1]
            if ("0" + states[0][:-1:]) == states[1]:
                decoded = decoded + [0]
            states = states[1::]
        final = []
        decoded=decoded[:-(gennum):]
        for i in range(0,len(decoded),8):
            nitem = ""
            for n in range(8):
                nitem = nitem + str(decoded[i+n])
            final=final+[nitem]
        byt=b""
        for i in final:
            p=int(i,2)
            p=hex(p)
            p=p[2::]
            if len(p)==1:
                p="0"+p
            byt= byt+bytes.fromhex(p)

        return byt, bestval[0][0]


