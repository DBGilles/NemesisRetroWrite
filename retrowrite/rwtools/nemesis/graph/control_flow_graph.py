import copy
import random
from collections import defaultdict

import networkx as nx
from networkx.algorithms.cycles import simple_cycles
from networkx.algorithms.simple_paths import all_simple_paths, all_simple_edge_paths

from librw.container import InstructionWrapper
from rwtools.nemesis.graph.abstract_nemesis_node import AbstractNemesisNode
from rwtools.nemesis.graph.nemesis_node import NemesisNode

from rwtools.nemesis.graph.utils import single_source_longest_dag_path_length, get_node_depth, \
    to_img

random.seed(10)

random_numbers = random.sample(range(1, 1000), 100)  # sampling without replacement


def find_branch_target(branch_instruction):
    start = branch_instruction.find(".")
    return branch_instruction[start:]

def set_branch_target(instruction_sequence, label):
    # TODO: use NemesisNode.setBranchingtarget()
    if isinstance(instruction_sequence, list):
        # replace last instruction in the list
        instruction_sequence[-1] = f"jmp {label}"
    elif isinstance(instruction_sequence, InstructionWrapper):
        # if after is not empty the instruction has been instrumented
        # if it hasn't been instrumented simply modify the op string
        if len(instruction_sequence.after) > 0:
            instruction_sequence.after[-1] = f"jmp {label}"
        else:
            instruction_sequence.op_str = f"{label}"


def is_branching_instruction(instruction):
    return True in [x in instruction for x in ["jmp", "je", "jne", "jge"]]

def get_node_id():
    node_id = random_numbers[0]
    random_numbers.remove(node_id)
    return node_id

class ControlFlowGraph:
    """
    Wrapper class for modifying and querying networkx graph
    """

    def __init__(self, graph):
        # self.nodes = nodes # TODO: doe deze weg (do equivalent to self.graph.nodes)
        self.graph = graph
        self.removed_edges = []
        self.inserted_node_counter = 0

    def to_img(self):
        return to_img(self.graph)

    def get_root(self):
        for node in self.graph.nodes:
            if self.graph.in_degree[node] == 0:
                return node

    def get_leaves(self):
        return [node for node in self.graph.nodes if self.graph.out_degree(node) == 0]

    def merge_consecutive_nodes(self):
        # get in and out degrees for all nodes that belong to this function
        current_node = self.get_root()
        marked = []  # keep track of the ndoes we have already visited
        branches = []

        def next_node():
            # go to next node, return false if no next node
            if len(branches) == 0:
                return None
            current_node = branches[0]
            branches.remove(current_node)
            marked.append(current_node)
            return current_node

        while True:
            # get out degree current nodes
            out_d = self.graph.out_degree[current_node]
            if out_d == 0:
                # current node is leaf -- go to next
                current_node = next_node()
                if current_node is None:
                    break
            if out_d == 1:
                # if out degree is 1 we merge if
                # 1) current node last instruction is not a jump
                # 2) succ in degree is equal to 1
                succ = next(self.graph.successors(current_node))
                assert succ is not None
                if current_node.get_instr_latency(-1) != -1 and \
                        self.graph.in_degree[succ] == 1 \
                        and succ not in marked:
                    # merge the node
                    current_node.append_node(succ)

                    # 2) add edge from all neighbors of next_node
                    for neighbor in self.graph.neighbors(succ):
                        self.graph.add_edge(current_node, neighbor)

                    # 3) remove node from graph (also removes edges) and from list of nodes
                    self.graph.remove_node(succ)
                    if succ in branches:
                        branches.remove(succ)
                else:
                    # do not merge the node -- go to next node if it is not marked ?
                    branches.append(succ)
                    current_node = next_node()
                    if current_node is None:
                        break
            elif out_d > 1:
                branches += [n for n in self.graph.neighbors(current_node) if n not in marked]
                current_node = next_node()
                if current_node is None:
                    break

    def get_node(self, label):
        target_node = None
        for node in self.graph.nodes:
            if node.id == label:
                target_node = node
                break
        return target_node

    def get_instruction_node(self, address):
        # return the node that contains instruction with address
        for node in self.graph.nodes:
            for instr in node.instruction_wrappers:
                if hex(instr.address)[2:] == address:
                    return node

    def equalize_path_lengths(self, root, node):
        # equalize all path lengths to the given node
        # path length is defined as the number of nodes from the root to the target node
        paths = list(all_simple_edge_paths(self.graph, root, node))

        if len(paths) == 0:
            # there are not paths from root to node
            return

        longest_path = max(paths, key=lambda x: len(x))
        max_len = len(longest_path)

        counter = 0
        for i in range(len(paths)):
            p = paths[i]
            diff = max_len - len(p)
            if diff == 0:
                continue
            candidates = set(p).difference(longest_path)
            candidates = sorted(candidates, key=lambda x: str(x[0].id) + str(x[1].id))

            unique_edge = candidates[0]
            from_node = unique_edge[0]
            to_node = unique_edge[1]

            for _ in range(diff):
                # create a new node
                new_node = AbstractNemesisNode([], f"{from_node.id}{to_node.id}")
                counter += 1

                # add it to graph
                self.graph.add_node(new_node)
                # self.nodes.append(new_node)

                # add edge from second to last node  new node, from new node to last in path
                self.graph.add_edge(from_node, new_node)
                self.graph.add_edge(new_node, to_node)

                # remove edge from first in path to second in path
                self.graph.remove_edge(from_node, to_node)

                if isinstance(to_node, NemesisNode):

                    # if the next node is a 'real node' add a jmp instruction
                    # if the next node is not a 'real node' then you don't need to add jump
                    # because they will later be merged anyway
                    jmp_label = to_node.get_start_label()
                    jmp_instruction = f"jmp {jmp_label}"

                    # we also want to insert the jmp instruction in the sibling
                    for node in self.graph.successors(from_node):
                        if not isinstance(node, NemesisNode):
                            continue
                        else:
                            # this node is a sibling that is not the newly created node, also
                            # add the jump here
                            node.append_instructions([[jmp_instruction]], [[-1]])

                # update second_to_last
                for j in range(i + 1, len(paths)):
                    following_path = paths[j]
                    # following_path.remove((from_node, to_node))
                    edge = (from_node, to_node)
                    if edge in following_path:
                        edge_index = following_path.index(edge)
                        # first insert new edges at edge_index, edge_index+1, then remove old edge
                        following_path.insert(edge_index, (from_node, new_node))
                        following_path.insert(edge_index + 1, (new_node, to_node))
                        following_path.remove((from_node, to_node))
                from_node = new_node

    def insert_nodes(self, target_node):
        subgraph = self.subgraph(target_node)
        longest_path_lengths = single_source_longest_dag_path_length(subgraph, target_node)

        # loop over all edges in the subgraph. If an edge goes between nodes where the diffeence
        # in lengths is more than 1 then there is a problem
        target_edges = []
        for from_node, to_node in nx.edges(subgraph):
            diff = longest_path_lengths[to_node] - longest_path_lengths[from_node]
            if diff > 1:
                target_edges.append((from_node, to_node, diff))

        for from_node, to_node, diff in target_edges:
            for i in range(diff - 1):
                # create a new node
                new_node = AbstractNemesisNode([], f"{self.inserted_node_counter}")
                self.inserted_node_counter += 1
                # insert 'inside' edge
                self.insert_between_nodes(new_node, from_node, to_node)

                # a newly inserted node will later need to be merged with its successor (i.e.
                # to_node). If to node has other predecessors, then this node needs to have a
                # branching instruction to the current start of to_node, so that when the
                # new node is merged the flow is still correct
                # if a predecessor of to_node does not have a branching instruction, add it
                for node in self.graph.predecessors(to_node):
                    if node.num_instructions() == 0 or not is_branching_instruction(
                            node.get_instr_mnemonic(-1)):
                        jmp_label = to_node.get_start_label()
                        jmp_instruction = f"jmp {jmp_label}"
                        node.append_instructions([[jmp_instruction]], [[-1]])

                # new node becomes to_node so that other nodes are inserted before the new node
                to_node = new_node

    def equalize_branches(self, target_node):
        # root = get_root(self.graph)
        subgraph = self.subgraph(target_node)

        longest_path_lengths = single_source_longest_dag_path_length(subgraph, target_node)
        leaves = [node for node in subgraph if subgraph.out_degree(node) == 0]
        leaf_depth = max(longest_path_lengths[l] for l in leaves)
        for leaf in leaves:
            if diff := leaf_depth - longest_path_lengths[leaf]:
                # true if diff is not equal to 0
                # name_prefix = f"leaf_{leaf.id}"
                current_node = leaf
                for i in range(diff):
                    # TODO: use function insert_as_parent()
                    new_node = AbstractNemesisNode([], f"{self.inserted_node_counter}")
                    self.inserted_node_counter += 1
                    # insert the node into the graph
                    predecessors = list(self.graph.predecessors(current_node))
                    for predecessor in predecessors:
                        self.graph.add_edge(predecessor, new_node)
                        self.graph.remove_edge(predecessor, current_node)
                        if predecessor.num_instructions() >= 1 and is_branching_instruction(
                                predecessor.get_instr_mnemonic(-1)):
                            predecessor.set_branching_target(new_node.get_start_label())
                    self.graph.add_edge(new_node, current_node)

    def restore_cycles(self):
        mapped_nodes = []
        root = self.get_root()
        for node in self.graph.nodes:
            # get the nodes children
            children = self.graph.successors(node)
            for child in children:
                if child.mapped_nodes is not None:
                    mapped_nodes.append((child, node))

        for mapped_node, parent in mapped_nodes:
            self.graph.remove_node(mapped_node)
            self.graph.add_edge(parent, mapped_node.mapped_nodes[0])

        remove_nodes = []
        for node in self.graph.nodes:
            if node == root:
                continue
            try:
                next(all_simple_paths(self.graph, root, node))
            except StopIteration:
                remove_nodes.append(node)

        for node in remove_nodes:
            self.graph.remove_node(node)

        for from_node, to_node in self.removed_edges:
            self.graph.add_edge(from_node, to_node)

    def merge_with_descendant(self, from_node, to_node):
        to_node_predecessors = set(self.graph.predecessors(to_node))
        # step 1:
        # we will be inserting instructions into the start of the node
        # all other predecessors of the to_node need to have a jump to the (currently) first
        # instruction
        to_node_label = None
        for node in to_node_predecessors - {from_node}:
            # by construction all other descendants of to_node will have a jump (inserted when
            # from node was first inserted)
            last_instr = node.get_instr_mnemonic(-1)
            assert(is_branching_instruction(last_instr))
            branch_target = find_branch_target(last_instr)
            # if this branch target is equal to the node i
            if isinstance(to_node, NemesisNode) and branch_target == to_node.get_start_label():
                if to_node_label is None:
                    node_id = get_node_id()
                    to_node_label = f".R{node_id}"
                    to_node.insert(0, f"{to_node_label}:", 0)
                instruction_sequence = node.get_instruction_sequence(-1)
                set_branch_target(instruction_sequence, to_node_label)

        # step 2: prepend the instruction of from node into to_node if from_node has a
        # branching instruction and the target is equal to to_node's start label then insert a
        # new label and modify
        last_instr = from_node.get_instr_mnemonic(-1)
        if "jmp" in last_instr:
            branch_target = find_branch_target(last_instr)
            if branch_target == to_node.get_start_label():
                node_id = get_node_id()
                label_name = f".R{node_id}"
                to_node.insert(0, f"{label_name}:", 0)

                # modify last istruction in from_node so that it jumps to newly created label
                # insert newly created label in to node
                instruction_sequence = from_node.get_instruction_sequence(-1)
                set_branch_target(instruction_sequence, label_name)

        # step 3: finally insert instructions into to_node, remove from graph
        to_node.prepend_instructions(from_node.instructions, from_node.latencies)
        parent = list(self.graph.predecessors(from_node))[0]
        self.graph.add_edge(parent, to_node)
        self.graph.remove_node(from_node)

    def merge_inserted_nodes(self):
        # cycles will mess with topological ordering needed for merging inserted node,
        # remove the cycles and restore them later
        targets = []
        # determine which nodes need to be inserted
        # for node in self.graph.nodes:
        for node in nx.algorithms.dag.topological_sort(self.graph):
            if not isinstance(node, NemesisNode):
                # merge this node with it successor
                targets.append(node)
        for node in targets:
            succ = list(self.graph.successors(node))[0]
            self.merge_with_descendant(node, succ)

    def unwind_graph(self, root=None):
        # 1) first determine which edges to remove (keep track of tuples of node)
        # 2) remove the nodes

        cyclic_edges = []
        if root is None:
            root = self.get_root()
        # step 1: determine which edges to remove by first finding cycles and then removing the
        # edge that goes from the deepest node to the most shallow node
        cycles = simple_cycles(self.graph)
        for cycle in cycles:
            depths = [get_node_depth(self.graph, root, node) for node in cycle]

            deepest_index = depths.index(max(depths))
            shallow_index = depths.index(min(depths))
            assert (deepest_index + 1) % len(depths) == shallow_index
            # assert abs(deepest_index - shallow_index) == 1 or abs(deepest_index - shallow_index)

            cyclic_edges.append((cycle[deepest_index], cycle[shallow_index]))

        # step 2: given the target edges this step is really straightforward
        cyclic_edges = set(cyclic_edges)

        node_copies = defaultdict(list)
        for last_node, first_node in cyclic_edges:
            # remove the edge from the last node to the first node
            self.graph.remove_edge(last_node, first_node)

            # add a copy of the first node as a child of the last node if the last node
            # has anoteher descendant
            if len(list(self.graph.successors(last_node))) == 0:
                # if the node has no other descendants we can simply remove the edge
                # there is no need for balancing here, so no reason to keep the successor
                self.removed_edges.append((last_node, first_node))
            else:
                # here we do have to keep the successor (while removing the cycle) so we
                # create a copy of the node and add it as a child (while also keeping the original
                # we keep track of which nodes are 'mapped' in this way,
                print(list(node.id for node in self.graph.successors(last_node)))

                # new_node = copy.deepcopy(first_node)
                new_node = copy.copy(first_node)
                new_node.id = new_node.id + f"_{random.randint(0, 100)}"
                node_copies[first_node].append(new_node)
                # new_node.mapped_node = first_node
                self.graph.add_node(new_node)
                self.graph.add_edge(last_node, new_node)

        # add to each newly created node as as mapped node
        # 1) the original node it is a copy of
        # 2) all other copies of that original node
        for node, copies in node_copies.items():
            for c in copies:
                c.mapped_nodes = [node] + copies

    def insert_between_nodes(self, new_node, from_node, to_node):
        self.graph.add_node(new_node)
        self.graph.add_edge(from_node, new_node)
        self.graph.add_edge(new_node, to_node)
        self.graph.remove_edge(from_node, to_node)
        if from_node.num_instructions() > 0 and is_branching_instruction(
                from_node.get_instr_mnemonic(-1)):
            from_node.set_branching_target(new_node.get_start_label())

    def insert_as_parent(self, new_node, target_node):
        # insert the new node as a parent of the target node
        self.graph.add_node(new_node)
        for pred in list(self.graph.predecessors(target_node)):
            self.graph.add_edge(pred, new_node)
            self.graph.remove_edge(pred, target_node)
            if pred.num_instructions() > 0 and is_branching_instruction(
                    pred.get_instr_mnemonic(-1)):
                pred.set_branching_target(new_node.get_start_label())
        self.graph.add_edge(new_node, target_node)

    def remove_node(self, target_node):
        assert self.graph.in_degree(target_node) == 1 and self.graph.out_degree(target_node) == 1
        parent = next(self.graph.predecessors(target_node))
        child = next(self.graph.successors(target_node))
        self.graph.remove_node(target_node)
        self.graph.add_edge(parent, child)

    def subgraph(self, node):
        # first find a node that dominates all leaves
        dominator = None
        immediate_dominators = nx.immediate_dominators(self.graph, node)
        leaves = [node for node in self.graph.nodes if self.graph.out_degree(node) == 0]
        leaf_dominators = set(
            immediate_dominators[leaf] for leaf in leaves if leaf in immediate_dominators.keys())
        if len(leaf_dominators) == 1:
            dominator = leaf_dominators.pop()
            # if dominator is the node itself then there is no suitable dominator
            if dominator == node:
                dominator = None

        if dominator is None:
            subgraph_nodes = []
            for l in leaves:
                for p in all_simple_paths(self.graph, source=node, target=l):
                    for n in p:
                        if n not in subgraph_nodes:
                            subgraph_nodes.append(n)
            return self.graph.subgraph(subgraph_nodes)
        else:
            # TODO: find better way of doing this?
            subgraph_nodes = []
            paths = all_simple_paths(self.graph, source=node, target=dominator)
            for p in paths:
                for n in p:
                    if n not in subgraph_nodes:
                        subgraph_nodes.append(n)
            return self.graph.subgraph(subgraph_nodes)

    def insert_labels(self):
        # for each abstract node, if its successors has a branching instruction to it and
        for node in self.graph.nodes:
            if isinstance(node, NemesisNode):
                continue
            for pred in self.graph.predecessors(node):
                instr = pred.get_instr_mnemonic(-1)
                if is_branching_instruction(instr) and node.get_start_label() in instr:
                    if node.get_instr_latency(0) != 0:
                        node.insert(0, f"{node.get_start_label()}:", 0)

    def get_branching_nodes(self):
        return [node for node in self.graph.nodes if self.graph.out_degree(node) > 1]
