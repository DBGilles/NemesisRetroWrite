
def flatten(nested_list):
    ret = []
    for sublist in nested_list:
        ret += sublist
    return ret

class AbstractNemesisNode:
    """
    abstract version of the nemesis node -- contains only a list of latencies
    A concrete node contains a list of instruction wrappers (each wrapper can contain multiple
    instructions after instrumentation).
    In this abstract version of  a node an instruction wrapper is simply a (nested)
    list of latencies
    """

    def __init__(self, instruction_latency, name, mapped_node=None):
        if isinstance(instruction_latency, int):
            self.latencies = [[instruction_latency]]
        elif isinstance(instruction_latency, list):
            self.latencies = [instruction_latency]
        self.frozen = False
        self.id = name
        self.mapped_nodes = mapped_node  # reference to original node - acts as a pointer of sorts

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        out_str = ""
        out_str += f"{self.id}\n"
        for sublist in self.latencies:
            out_str += "[" + "\n".join(str(x) for x in sublist) + "]\n"
        return out_str

    # def __repr__(self):
    #     return self.id

    def num_instructions(self):
        """
        Return the total number of instructions
        """
        return sum(len(lat) for lat in self.latencies)

    def __lt__(self, other):
        return sum(self.latencies) < sum(other.latencies)

    def __gt__(self, other):
        """
        A node is 'larger' than another node if it takes a longer time to execute
        i.e. when the sum of all the latencies is larger than the other's
        """
        return sum(flatten(self.latencies)) > sum(flatten(other.latencies))

    def insert(self, index, instruction, latency):
        """
        Insert instruction at absolute index i
        Find where instruction at absolute index i-1 is locted, insert right after it
        """
        if index == 0:
            i, j = 0, 0
        elif index > self.num_instructions():
            raise ValueError(f"Cant insert instruction at index {index} into node with "
                             f"{self.num_instructions()} instructions")
        else:
            counter = 0
            out = None
            for i in range(len(self.latencies)):
                for j in range(len(self.latencies[i])):
                    if counter == index - 1:
                        out = (i, j)
                    if out is not None:
                        break
                    counter += 1
                if out is not None:
                    break

            # i, j are the indices of item with i = 'index'-1, to insert at 'index', insert at j+1
            i, j = out
            j += 1

        self.latencies[i].insert(j, latency)
        # if self.mapped_nodes is not None:
        #     for mapped_node in self.mapped_nodes:
        #         if mapped_node == self:
        #             continue
        #         else:
        #             mapped_node.latencies[i].insert(j, latency)

    def get(self, item):
        if item >= len(self.latencies):
            return_val = self[-1]
        else:
            return_val = self[item]
        assert (isinstance(return_val, int))
        return return_val

    def __getitem__(self, item):
        return self.latencies[item]

    def get_latency(self, i):
        """
        Return the latency with absolute position i
        """
        return flatten(self.latencies)[i]

    def append_node(self, node):
        self.latencies += node.latencies
