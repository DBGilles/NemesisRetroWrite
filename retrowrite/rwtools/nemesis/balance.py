"""
Functions (including helper functions) for balancing two CodeSequence instancees
add instructions of specific latencies to balance both branches
"""

def needs_balancing(b1, b2):
    # map each sublist to its total sum, copmare the sum of these
    if sum(map(lambda x: sum(x), b1.latencies)) == sum(map(lambda x: sum(x), b2.latencies)):
        return True

    # map each sublist to its length, if sum of these length not equal then number of
    # instruction not equal, return True
    if sum(map(lambda x: len(x), b1.latencies)) != sum(map(lambda x: len(x), b2.latencies)):
        return True

    # finally,
    for b1l, b2l in zip(b1.latencies, b2.latencies):
        for sub1, sub2 in zip(b1l, b2l):
            if sub1 != sub2:
                return True
    return False


def get_null_instr(latency):
    if latency == 1:
        return "add %eax $0"
    if latency == 2:
        return "movl %eax, %eax"
    else:
        return f"instr with lat {3}"


def nested_f(b, f):
    return sum(map(lambda x: f(x), b))


def number_of_instructions(b):
    return sum(map(lambda x: len(x), b.latencies))


def balance(b1, b2):
    """
    implementation of the balancing strategy
    current strategy: add instructions of specific lengths, not taking anything into account
    """
    # first determine if balancing is required
    if not needs_balancing(b1, b2):
        return

    instr_index = 0

    while True:
        short_b = min(b1, b2)
        long_b = b1 if short_b == b2 else b2
        if instr_index >= len(short_b):
            if instr_index >= len(long_b):
                # branches should be balanced at this point
                break
            else:
                # TODO: check dit
                # special case -- the shorter branch needs additional instructions inserted, but take care that the last
                # instruction remains a jump (if it is a jump)
                inst_wrapper_long, lat_long = long_b.get(instr_index)
                # inst_wrapper_short, lat_short = short_b.get(instr_index - 1)
                filler_instr = get_null_instr(latency=lat_long)
                short_b.insert(instr_index - 1, filler_instr, lat_long)

        # get relevant instruction from both
        assert (short_b != long_b)

        inst_wrapper_short, lat_short = short_b.get(instr_index)
        inst_wrapper_long, lat_long = long_b.get(instr_index)

        # if latencies are equal, nothing to do, increment current instruction index
        if lat_short == lat_long:
            instr_index += 1
            continue

        # otherwise, determine 'filler' instruction, add it to shortest -- take latency from the longer branch as target latency
        # take the latency from the longer branch as target latency
        filler_instr = get_null_instr(latency=lat_long)

        # finally, insert the instruction into the shorter branch
        short_b.insert(instr_index, filler_instr, lat_long)

        instr_index += 1
