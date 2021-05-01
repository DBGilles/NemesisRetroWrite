#
# # TODO: check of deze allemaal correct zijn
# # voorlopig gebruik maken van placholders (die wel effectief instructies zijn) om verder te kunnen
# # werken
# def get_nop_instruction(target_latency):
#     # return 1) the instruction itself, 2) registers that need to be pushed and popped
#     if target_latency == 1:
#         return "movq %rax, %rax", None
#         # return "movq %rax, %rax", None
#         # return "addl $0, %eax", '%rax'
#
#     if target_latency == 2:
#         return "movq %xmm0, %xmm0", None
#
#     if target_latency == 3:
#         return "mulq %rax", '%rax'
#
#     if target_latency == 5:
#         # TODO: check of latency hier wel effectief 5 is
#         return "sbbq $0, %rax"
#
#     if target_latency == 0:
#         return "", []
#     print(f"warning, no nop instruction found with latency {target_latency}")
#     return "placeholder", []
#
#
# def get_added_instructions(target_latency):
#     #
#     if target_latency == 1:
#         return 1
#     elif target_latency == 2:
#         return 1
#     elif target_latency == 3:
#         return 5  # instruction itself + push + pop + increment SP + decrement SP
#     elif target_latency == 5:
#         return 1
#
# def get_nop_sequence(target_latency):
#     if target_latency == 1:
#         return ["addl $0, %eax"]
#     if target_latency == 2:
#         return ["movq %xmm0, %xmm0"]
#     if target_latency == 3:
#         return ["sub $0x8, %rsp",
#                 "pushq %rax",
#                 "mulq %rax",
#                 "popq %rax",
#                 "add $0x8, %rsp"]
#     if target_latency == 4:
#         return ["placeholder"]
#     if target_latency == 5:
#         # TODO: check of latency hier wel effectief 5 is
#         return ["sbbq $0, %rax"]
#     if target_latency == 0:
#         return [""]
#     raise ValueError(f"Can't map {target_latency} to nop sequence")
#
#
# def map_latency_sequence_to_instructions(latency_sequence):
#     if len(latency_sequence) == 1:
#         return get_nop_sequence(latency_sequence[0])
#     elif len(latency_sequence) > 1 and latency_sequence[0] != 3:
#         return get_nop_sequence(latency_sequence[0]) * len(latency_sequence)
#     elif len(latency_sequence) == 5 and latency_sequence[0] == 3:
#         return ["sub $0x8, %rsp",
#                 "pushq %rax",
#                 "mulq %rax",
#                 "popq %rax",
#                 "add $0x8, %rsp"]
#     elif len(latency_sequence) == 4 and latency_sequence[0] == 3:
#         return ["sub $0x8, %rsp",
#                 "pushq %rax",
#                 "popq %rax",
#                 "add $0x8, %rsp"]
#     else:
#         raise ValueError(f"Don't know what to do for latency sequence {latency_sequence}")