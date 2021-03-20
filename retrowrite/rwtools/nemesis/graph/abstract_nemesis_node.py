############################################
# Definition of Abstract NemesisNode class #
############################################

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

    def __init__(self, instruction_latency, name):
        if isinstance(instruction_latency, int):
            self.latencies = [[instruction_latency]]
        elif isinstance(instruction_latency, list):
            self.latencies = [instruction_latency]
        self.instructions = [[]]
        self.frozen = False
        self.id = name
        self.mapped_nodes = None  # reference to original node - acts as a pointer of sorts

    def is_abstract(self):
        return True

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        out_str = ""
        out_str += f"#{self.id}#\n"
        for i, sublist in enumerate(self.latencies):
            strings = []
            for j, latency in enumerate(sublist):
                try:
                    instruction = self.instructions[i][j]
                except IndexError:
                    instruction = ""
                strings.append(f"{instruction} ~ {latency}")
            out_str += "\n".join(strings) + "\n"
        #
        # for sublist in self.latencies:
        #     out_str += "[" + "\n".join(str(x) for x in sublist) + "]\n"
        return out_str

    # def __repr__(self):
    #     return self.id

    def __gt__(self, other):
        """
        A node is 'larger' than another node if it takes a longer time to execute
        i.e. when the sum of all the latencies is larger than the other's
        """
        # return sum(flatten(self.latencies)) > sum(flatten(other.latencies))
        return sum(sum(lats) for lats in self.latencies) > sum(
            sum(lats) for lats in other.latencies)

    def num_instructions(self):
        """
        Return the total number of instructions
        """
        return sum(len(lat) for lat in self.latencies)

    def insert(self, index, instruction, latency):
        """
        Insert instruction at absolute index i
        Find where instruction at absolute index i-1 is locted, insert right after it
        """
        print("inserting ", instruction, latency)
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
        self.instructions[i].insert(j, instruction)

    def get_instr_mnemonic(self, index):
        return ""

    def get_latency(self, i):
        """
        Return the latency with absolute position i
        """
        return flatten(self.latencies)[i]

    def append_node(self, node):
        self.latencies += node.latencies

