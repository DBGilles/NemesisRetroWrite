from rwtools.nemesis.op_types import map_latencydata_types

def convert_latency(lat):
    """
    Convert the given latency to a fixed type (float) -- ensure uniformity between rows
    """
    if isinstance(lat, int):
        return lat
    elif isinstance(lat, float):
        return int(lat)
    elif isinstance(lat, str):
        try:
            # try casting string to float and returning it
            return int(lat)
        except ValueError:
            # if it doesn succeed, continue with rest of the function z
            pass
            # several special cases, handle seperately
        if "-" in lat:
            # latency of type 'a-b' -- return float(b)
            return int(lat.split("-")[-1])
        if 'b' in lat:
            return -1
        if "~" in lat:
            return int(lat[1:])


def split_operands(ops):
    # special cases mm/x, mm/y refer to xmm or mmx and mmy or ymm
    if ops == "mm/x":
        return ["mmx", "xmm"]
    elif ops == "mm/y":
        return ["mmy", "ymm"]

    if '/' not in ops:
        return [ops.strip()]
    else:
        ops = list(map(lambda x: x.strip(), ops.split('/')))

    # take care of special cases here
    # (1) 2 ops where the second type is only a number -- first op has one or more chars that need to be appended to second op
    # eg m8/16 --> [m8, 16] --> [m8, m16]
    if len(ops) == 2 and ops[1].isnumeric():
        # first get the index of the first non-numerical character in ops[0]
        i = ops[0].index(list(filter(lambda x: x.isnumeric(), ops[0]))[0])
        ops[1] = ops[0][:i] + ops[1]
        return ops

    return ops


def extract_operand_types(op_string):
    """
    Return for each operand position (seperated by commas) a list of possible operand typess
    eg input 'r32/64,r32/64' return [r32, r64], [r32, r64]
    """

    if op_string == "nan" or op_string is None or isinstance(op_string, float):
        # nan is apparently of type float
        return []

    operand_positions = op_string.split(",")
    operand_types = []
    for ops in operand_positions:
        # now we are looking at individual operands
        op_types = split_operands(ops)
        try:
            op_types = list(map(lambda x: map_latencydata_types(x), op_types))
        except ValueError:
            print("unable to map one of types ", op_types)
        operand_types.append(op_types)
    return operand_types


def length_diff(a, b):
    return abs(len(a) - len(b))


def best_candidate(key, candidates):
    # get the candidate that is the best/closest match to key k (in terms of name, operands, etc)
    if len(candidates) == 1:
        return candidates.iloc[0]
    else:
        # sort candidates based on length similarity
        target_name, target_gas_name = key[:2]
        operands = key[2:] if len(key) > 2 else []
        candidates = candidates.values.tolist()
        candidates.sort(key=lambda x: length_diff(x[0], key[0]))

        candidate_match_counts = []
        for c in candidates:
            candidate_ops = c[1]
            candidate_op_types = extract_operand_types(candidate_ops)

            match_count = 0
            for op, candidate_types in zip(operands, candidate_op_types):
                for candidate_type in candidate_types:
                    if candidate_type == op:
                        match_count += 1
                        break
            candidate_match_counts.append(match_count)
        max_i = candidate_match_counts.index(max(candidate_match_counts))
        return candidates[max_i]
