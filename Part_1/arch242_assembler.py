import sys
import re

# Arch-242 Assembler: Converts assembly to machine code

# Define instruction encodings
instruction_set = {
    'rot-r': 0x00, 'rot-l': 0x01, 'rot-rc': 0x02, 'rot-lc': 0x03,
    'from-mba': 0x04, 'to-mba': 0x05, 'from-mdc': 0x06, 'to-mdc': 0x07,
    'addc-mba': 0x08, 'add-mba': 0x09, 'subc-mba': 0x0A, 'sub-mba': 0x0B,
    'inc*-mba': 0x0C, 'dec*-mba': 0x0D, 'inc*-mdc': 0x0E, 'dec*-mdc': 0x0F,
    'and-ba': 0x1A, 'xor-ba': 0x1B, 'or-ba': 0x1C,
    'and*-mba': 0x1D, 'xor*-mba': 0x1E, 'or*-mba': 0x1F,
    'clr-cf': 0x2A, 'set-cf': 0x2B, 'set-ei': 0x2C, 'clr-ei': 0x2D,
    'ret': 0x2E, 'retc': 0x2F, 'from-pa': 0x30, 'inc': 0x31,
    'to-ioa': 0x32, 'to-iob': 0x33, 'to-ioc': 0x34,
    'bcd': 0x36, 'shutdown': [0x37, 0x3E], 'timer-start': 0x38, 'timer-end': 0x39,
    'from-timerl': 0x3A, 'from-timerh': 0x3B, 'to-timerl': 0x3C, 'to-timerh': 0x3D,
    'nop': 0x3E, 'dec': 0x3F,
}

# Instructions with register encodings
reg_ops = {'inc*-reg': 0x10, 'dec*-reg': 0x11, 'to-reg': 0x20, 'from-reg': 0x21}
regs = {'r0': 0b000, 'r1': 0b001, 'r2': 0b010, 'r3': 0b011, 'r4': 0b100}

# Two-byte immediate instructions
imm_ops = {
    'add': 0x40, 'sub': 0x41, 'and': 0x42, 'xor': 0x43, 'or': 0x44, 'timer': 0x47
}

# Special branch and jump instructions
branch_ops = {
    'b-bit': 0x80, 'bnz-a': 0xA0, 'bnz-b': 0xA8, 'beqz': 0xB0, 'bnez': 0xB8,
    'beqz-cf': 0xC0, 'bnez-cf': 0xC8, 'b-timer': 0xD0, 'bnz-d': 0xD8,
    'b': 0xE0, 'call': 0xF0
}

# ACC immediate load
acc_imm_prefix = 0x70

def parse_operand(operand):
    if operand.startswith('0x'):
        return int(operand, 16)
    elif operand.startswith('0b'):
        return int(operand, 2)
    else:
        return int(operand)

def assemble_line(line):
    # Strip comments and split tokens
    line = line.split(';')[0].strip()
    if not line:
        return []

    tokens = re.split(r'\s+', line)
    instr = tokens[0].lower()
    code = []

    if instr in instruction_set:
        encoding = instruction_set[instr]
        return encoding if isinstance(encoding, list) else [encoding]

    elif instr in reg_ops:
        if len(tokens) < 2:
            raise ValueError(f"Missing register operand for: {instr}")
        reg = tokens[1].lower()
        if reg not in regs:
            raise ValueError(f"Invalid register: {reg}")
        code.append(reg_ops[instr] | (regs[reg] << 1))
        return code

    elif instr in imm_ops:
        if len(tokens) < 2:
            raise ValueError(f"Missing immediate for: {instr}")
        imm = parse_operand(tokens[1])
        code.append(imm_ops[instr])
        code.append(imm & 0x0F)
        return code

    elif instr == 'acc':
        if len(tokens) < 2:
            raise ValueError("Missing immediate value for acc")
        imm = parse_operand(tokens[1])
        code.append(acc_imm_prefix | (imm & 0x0F))
        return code

    elif instr in branch_ops:
        if instr == 'b-bit':
            if len(tokens) < 3:
                raise ValueError("Expected: b-bit <k> <imm>")
            k = int(tokens[1])
            imm = parse_operand(tokens[2])
            imm_bin = imm & 0x7FF
            code.append(branch_ops[instr] | ((k & 0x3) << 3) | ((imm_bin >> 8) & 0x07))
            code.append(imm_bin & 0xFF)
        else:
            if len(tokens) < 2:
                raise ValueError(f"Missing branch address for: {instr}")
            imm = parse_operand(tokens[1])
            imm_bin = imm & 0x7FF
            code.append(branch_ops[instr] | ((imm_bin >> 8) & 0x0F))
            code.append(imm_bin & 0xFF)
        return code

    elif instr in ['rarb', 'rcrd']:
        if len(tokens) < 2:
            raise ValueError(f"Missing operand for {instr}")
        imm = parse_operand(tokens[1])
        x = (imm >> 4) & 0x0F
        y = imm & 0x0F
        prefix = 0x50 if instr == 'rarb' else 0x58
        code.append(prefix | x)
        code.append(y)
        return code

    else:
        raise ValueError(f"Unknown instruction: {instr}")

# def assemble(input_file, output_file):
#     with open(input_file, 'r') as fin, open(output_file, 'wb') as fout:
#         for lineno, line in enumerate(fin, 1):
#             try:
#                 machine_code = assemble_line(line)
#                 fout.write(bytearray(machine_code))
#             except ValueError as e:
#                 print(f"[Line {lineno}] Error: {e} -> \"{line.strip()}\"")

def assemble(input_file, output_file):
    # First pass: record labels
    labels = {}
    addr = 0
    with open(input_file, 'r') as fin:
        for line in fin:
            line_clean = line.split(';')[0].strip()
            if line_clean.endswith(':'):
                label = line_clean[:-1].strip()
                labels[label] = addr
            else:
                try:
                    code = assemble_line(line_clean)
                    addr += len(code)
                except ValueError:
                    pass  # Ignore errors for now (will catch later)

    # Second pass: generate code with label resolution
    with open(input_file, 'r') as fin, open(output_file, 'wb') as fout:
        for lineno, line in enumerate(fin, 1):
            line_clean = line.split(';')[0].strip()
            if not line_clean or line_clean.endswith(':'):
                continue
            tokens = re.split(r'\s+', line_clean)
            instr = tokens[0].lower()
            if instr in branch_ops and len(tokens) == 2:
                target = tokens[1]
                if target in labels:
                    tokens[1] = str(labels[target])
                    line_clean = ' '.join(tokens)
            try:
                machine_code = assemble_line(line_clean)
                fout.write(bytearray(machine_code))
            except ValueError as e:
                print(f"[Line {lineno}] Error: {e} -> \"{line.strip()}\"")


if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python assembler.py <input.asm> <output.bin>")
    else:
        assemble(sys.argv[1], sys.argv[2])