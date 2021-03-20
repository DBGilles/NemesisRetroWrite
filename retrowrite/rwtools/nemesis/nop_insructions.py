
# TODO: check of deze allemaal correct zijn
# voorlopig gebruik maken van placholders (die wel effectief instructies zijn) om verder te kunnen
# werken
def get_nop_instruction(target_latency):
    # return 1) the instruction itself, 2) registers that need to be pushed and popped
    if target_latency == 1:
        return "addl $0, %eax", []

    if target_latency == 2:
        return "movq %xmm0, %xmm0", []

    if target_latency == 3:
        return "mulq %rax", ['%rax']

    if target_latency == 5:
        # TODO: check of latency hier wel effectief 5 is
        return "sbbq $0, %rax", []

    print(f"warning, no nop instruction found with latency {target_latency}")
    return "placeholder", []

