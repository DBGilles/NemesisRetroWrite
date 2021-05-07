import re

# register can have a name of length 2 or length 3, preceded by modulo sign.
# Can have parenthesis in some cases
register_regex_str = "\\(?%[a-zA-Z0-9]{2,3}\\)?"
register_regex = re.compile(register_regex_str)

# immediate value is a dollar signed followed by optional '-' followed by either decimal or
# hex value. In cases where the immediate value isn't an actual operand the dollar sign
# is not present (so make it optional)
# eg $10, or $0x10
imm_values_regex_str = "\\$?-?(0x[0-9a-fA-F]+|[0-9]+)"
imm_values_regex = re.compile(imm_values_regex_str)

# labels are any alphanumeric string starting with 'L'
labels_regex_str = ".L[a-zA-Z0-9]+"
labels_regex = re.compile(labels_regex_str)

# register regex string preceded by some offset (decimal number with optional '-')
# offset can be either decimal or hex number (without '$'
relative_from_register_regex_str = f"{imm_values_regex_str}{register_regex_str}"
relative_from_register_regex = re.compile(relative_from_register_regex_str)

label_relative_from_register_regex_str = f"{labels_regex_str}{register_regex_str}"
label_relative_from_register_regex = re.compile(label_relative_from_register_regex_str)

compound_op_regex_str = f"\\({register_regex_str}, {register_regex_str}(, {imm_values_regex_str})?\\)"
compound_op_regex = re.compile(compound_op_regex_str)

relative_from_compound_op_regex_str = f"{imm_values_regex_str}{compound_op_regex_str}"
relative_from_compound_op_regex = re.compile(relative_from_compound_op_regex_str)

jump_target_regex_str = ".+@PLT"
jump_target_regex = re.compile(jump_target_regex_str)

operand_regex_str = f"({register_regex_str})|" \
                    f"({imm_values_regex_str})|" \
                    f"({labels_regex_str})|" \
                    f"{relative_from_register_regex_str}|" \
                    f"{label_relative_from_register_regex_str}|" \
                    f"{relative_from_compound_op_regex_str}|" \
                    f"{compound_op_regex_str}|" \
                    f"{jump_target_regex_str}"

operand_regex = re.compile(operand_regex_str, re.VERBOSE)  # set verbose for spaces in pattern

one_op_regex_str = f"{operand_regex_str}"
one_op_regex = re.compile(operand_regex_str)

two_ops_regex_str = f"({operand_regex_str}), ({operand_regex_str})"
two_ops_regex = re.compile(two_ops_regex_str)

three_ops_regex_str = f"({operand_regex_str}), ({operand_regex_str}), ({operand_regex_str})"
three_ops_regex = re.compile(three_ops_regex_str)

