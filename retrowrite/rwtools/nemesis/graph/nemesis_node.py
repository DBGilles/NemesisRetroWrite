#####################################
# Definition of a NemesisNode class #
#####################################
from rwtools.nemesis.LatencyMapper import construct_latency_mapper
import os

latency_mapper = construct_latency_mapper(os.path.abspath(
    "/home/gilles/git-repos/NemesisRetroWrite/retrowrite/rwtools/nemesis/utils/pickled_latency_map.p"))


class AbstractNemesisNode:
    """
    abstract version of the nemesis node -- contains only a list of latencies
    """

    def __init__(self, latencies, name):
        self.latencies = latencies
        self.frozen = False
        self.id = name

    def __hash__(self):
        # self.frozen = True
        # self.latencies = tuple(self.latencies)
        return hash(self.id)

    def __repr__(self):
        return "\n".join(str(x) for x in [self.id] + self.latencies)
        # return str(self.id)

    def __len__(self):
        # return the sum of the latencies
        return len(self.latencies)

    def __lt__(self, other):
        return sum(self.latencies) < sum(other.latencies)

    def __gt__(self, other):
        return sum(self.latencies) > sum(other.latencies)

    def insert(self, i, latency):
        # if self.frozen:
        # print(f"can't add value {latency} to frozen node")
        # return

        self.latencies.insert(i, latency)

    def get(self, item):
        if item >= len(self.latencies):
            return self.latencies[-1]

        return self.latencies[item]

    def __getitem__(self, item):
        return self.latencies[item]


class NemesisNode(AbstractNemesisNode):
    """
    Concrete node, actually contains a code sequence with instructions
    """

    def __init__(self, instruction):
        latencies = [[latency_mapper.get_latency(instruction.mnemonic, instruction.op_str)]]
        name = str(instruction.address)
        super().__init__(latencies, name)
        self.instructions = [instruction]

    def __repr__(self):
        # for each node, get a string with all of its instructions and
        out_strings = [f"{self.id}"]
        for instr, lats in zip(self.instructions, self.latencies):
            instr_strings = [b for b in instr.before] + [str(instr)] + [a for a in instr.after]
            assert (len(lats) == len(instr_strings))

            for instr, l in zip(instr_strings, lats):
                out_strings.append(f"{instr} ~ {l} ")

        return ", \\n".join(out_strings)

    def add_instructions(self, instructions):
        assert (isinstance(instructions, list))
        self.instructions += instructions
        for i in instructions:
            assert len(i.before) == 0 and len(i.after) == 0
            self.latencies.append([latency_mapper.get_latency(i.mnemonic, i.op_str)])