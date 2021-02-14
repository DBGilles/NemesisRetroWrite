#####################################
# Definition of a NemesisNode class #
#####################################

class NemesisNode:
    def __init__(self, latencies, name):
        self.latencies = latencies
        self.frozen = False
        self.id = name

    def __hash__(self):
        # self.frozen = True
        # self.latencies = tuple(self.latencies)
        return hash(self.id)

    def __repr__(self):
        return "\n".join([f"{self.id}"] + [str(v) for v in self.latencies])

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
