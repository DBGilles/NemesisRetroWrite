def get_nop_instruction(target_latency):
    # return 1) the instruction itself, 2) registers that need to be pushed and popped
    if target_latency == 1:
        return "imulq %eax, %eax", []

    if target_latency == 2:
        return "movd %xmm, %xmm", []

    if target_latency == 3:
        return "mulq %rax", ['%rax']

    print(f"warning, no nop instruction found with latency {target_latency}")
    return "placeholder"

