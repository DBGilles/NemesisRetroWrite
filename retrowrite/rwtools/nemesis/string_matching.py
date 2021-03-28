import re

# register can have a name of length 2 or length 3, preceded by modulo sign.
# Can have parenthesis in some cases
REGISTER_REGEX_STR = "\\(?%[a-zA-Z]{2,3}\\)?"
REGISTER_REGEX = re.compile(REGISTER_REGEX_STR)

# immediate value is a dollar signed followed by optional '-' followed by either decimal or
# hex value. In cases where the immediate value isn't an actual operand the dollar sign
# is not present (so make it optional)
# eg $10, or $0x10
IMM_VALUES_REGEX_STR = "\\$?-?(0x[0-9a-fA-F]+|[0-9]+)"
IMM_VALUES_REGEX = re.compile(IMM_VALUES_REGEX_STR)

# labels are any alphanumeric string starting with 'L'
LABELS_REGEX_STR = ".L[a-zA-Z0-9]+"
LABELS_REGEX = re.compile(LABELS_REGEX_STR)

# register regex string preceded by some offset (decimal number with optional '-')
# offset can be either decimal or hex number (without '$'
RELATIVE_FROM_REGISTER_REGEX_STR = f"{IMM_VALUES_REGEX_STR}{REGISTER_REGEX_STR}"
# RELATIVE_FROM_REGISTER_REGEX_STR = f"-?(0x[0-9a-fA-F]+|[0-9]+){REGISTER_REGEX_STR}"
RELATIVE_FROM_REGISTER_REGEX = re.compile(RELATIVE_FROM_REGISTER_REGEX_STR)

LABEL_RELATIVE_FROM_REGISTER_STR = f"{LABELS_REGEX_STR}{REGISTER_REGEX_STR}"
LABEL_RELATIVE_FROM_REGISTER = re.compile(LABEL_RELATIVE_FROM_REGISTER_STR)

COMPOUND_OP_STR = f"\\({REGISTER_REGEX_STR}, {REGISTER_REGEX_STR}(, {IMM_VALUES_REGEX_STR})?\\)"
COMPOUND_OP = re.compile(COMPOUND_OP_STR)

RELATIVE_FROM_COMPOUND_OP_STR = f"{IMM_VALUES_REGEX_STR}{COMPOUND_OP_STR}"
RELATIVE_FROM_COMPOUND_OP = re.compile(RELATIVE_FROM_COMPOUND_OP_STR)

JUMP_TARGET_STR = ".+@PLT"
JUMP_TARGET_REGEX = re.compile(JUMP_TARGET_STR)
