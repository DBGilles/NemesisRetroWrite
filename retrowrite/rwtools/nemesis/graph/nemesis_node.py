#####################################
# Definition of a NemesisNode class #
#####################################

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
    def __init__(self, latencies, name, code_sequence):
        super().__init__(latencies, name)
        self.code_sequence = code_sequence
