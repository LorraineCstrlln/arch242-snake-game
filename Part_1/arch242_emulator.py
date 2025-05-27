# import pyxel
# import sys

# class Arch242Emulator:
#     def __init__(self, program):
#         self.memory = [0] * 256
#         self.registers = {'ACC': 0, 'CF': 0, 'PC': 0,
#                           'R0': 0, 'R1': 0, 'R2': 0, 'R3': 0, 'R4': 0}
#         self.load_program(program)
#         pyxel.init(100, 80, title="Arch-242 Emulator")
#         pyxel.run(self.update, self.draw)

#     def load_program(self, program):
#         for i, byte in enumerate(program):
#             self.memory[i] = byte
#         print("Program loaded:", program[:20])  # print first few bytes


#     def fetch(self):
#         pc = self.registers['PC']
#         opcode = self.memory[pc]
#         self.registers['PC'] = (self.registers['PC'] + 1) & 0xFF
#         print(f"PC: {pc:02X}, Opcode: {opcode:02X}")  # Add this
#         return opcode


#     def execute(self, opcode):
#         # acc imm (0x70 - 0x7F): load immediate 4-bit to ACC
#         if 0x70 <= opcode <= 0x7F:
#             imm = opcode & 0x0F
#             self.registers['ACC'] = imm

#         # from-mba (0x04): ACC = memory[0x80]
#         elif opcode == 0x04:
#             self.registers['ACC'] = self.memory[0x80]

#         # to-mba (0x05): memory[0x80] = ACC
#         elif opcode == 0x05:
#             self.memory[0x80] = self.registers['ACC'] & 0xFF

#         # from-mdc (0x08): ACC = memory[0x81]
#         elif opcode == 0x08:
#             self.registers['ACC'] = self.memory[0x81]

#         # from-pa (0x09): Set ACC to PA
#         elif opcode == 0x09:
#             self.registers['ACC'] = self.memory[0x90]

#         # to-mdc (0x07): memory[0x81] = ACC
#         elif opcode == 0x07:
#             self.memory[0x81] = self.registers['ACC'] & 0xFF

#         # to-ioa (0x0A): memory[0x90] = ACC
#         elif opcode == 0x0A:
#             self.memory[0x90] = self.registers['ACC'] & 0xFF

#         # inc (0x31): ACC++
#         elif opcode == 0x31:
#             self.registers['ACC'] = (self.registers['ACC'] + 1) & 0xFF

#         # dec (0x3F): ACC--
#         elif opcode == 0x3F:
#             self.registers['ACC'] = (self.registers['ACC'] - 1) & 0xFF

#         # nop (0x3E): do nothing
#         elif opcode == 0x3E:
#             pass

#         # beqz (0xB0 - 0xBF): branch if ACC == 0, 1-byte address following
#         elif 0xB0 <= opcode <= 0xBF:
#             addr = self.fetch()
#             if self.registers['ACC'] == 0:
#                 self.registers['PC'] = addr & 0xFF

#         # b (0xE0 - 0xEF): unconditional branch, next byte is address
#         elif 0xE0 <= opcode <= 0xEF:
#             addr = self.fetch()
#             self.registers['PC'] = addr & 0xFF

#             # add <imm> (0x40)
#         elif opcode == 0x40:
#             imm = self.fetch()
#             self.registers['ACC'] = (self.registers['ACC'] + imm) & 0xFF

#         # sub <imm> (0x41)
#         elif opcode == 0x41:
#             imm = self.fetch()
#             self.registers['ACC'] = (self.registers['ACC'] - imm) & 0xFF

#         # to-reg (0x20 - 0x24)
#         elif 0x20 <= opcode <= 0x24:
#             reg_index = opcode - 0x20
#             self.registers[f'R{reg_index}'] = self.registers['ACC'] & 0xFF

#         # from-reg (0x21 - 0x25)
#         elif 0x21 <= opcode <= 0x25:
#             reg_index = opcode - 0x21
#             self.registers['ACC'] = self.registers[f'R{reg_index}'] & 0xFF

#         # xor (0x30): ACC = ACC ^ R0
#         elif opcode == 0x30:
#             self.registers['ACC'] ^= self.registers['R0']

#         # swap (0x06): swap memory[0x80] <-> memory[0x81]
#         elif opcode == 0x06:
#             self.memory[0x80], self.memory[0x81] = self.memory[0x81], self.memory[0x80]

#         # or <imm> (0x44)
#         elif opcode == 0x44:
#             imm = self.fetch()
#             self.registers['ACC'] |= imm

#         # and <imm> (0x42)
#         elif opcode == 0x42:
#             imm = self.fetch()
#             self.registers['ACC'] &= imm

#         # xor <imm> (0x43)
#         elif opcode == 0x43:
#             imm = self.fetch()
#             self.registers['ACC'] ^= imm

#         else:
#             print(f"Unknown opcode: {opcode:02X}")

#     def update(self):
#         # Run a few instructions per frame for smoother simulation
#         for _ in range(10):
#             opcode = self.fetch()
#             self.execute(opcode)

#         # Clear display memory area (0x80-0x93, 20 rows)
#         for row in range(20):
#             self.memory[0x80 + row] = 0

#         # Get snake position from memory
#         snake_x = self.memory[0x80]  # MBA holds X
#         snake_y = self.memory[0x81]  # MDC holds Y

#         # Safety check bounds
#         if 0 <= snake_x < 10 and 0 <= snake_y < 20:
#             # Set bit at snake_x in row snake_y
#             self.memory[0x80 + snake_y] |= (1 << snake_x)

#         # Handle input: map arrow keys to direction bits in 0x90 (IOA)
#         # Example: 0=right, 1=down, 2=left, 3=up (just one direction at a time)
#         direction = 0  # default right
#         if pyxel.btn(pyxel.KEY_UP):
#             direction = 3
#         elif pyxel.btn(pyxel.KEY_DOWN):
#             direction = 1
#         elif pyxel.btn(pyxel.KEY_LEFT):
#             direction = 2
#         elif pyxel.btn(pyxel.KEY_RIGHT):
#             direction = 0

#         self.memory[0x90] = direction

#     def draw(self):
#         pyxel.cls(0)
#         for row in range(20):
#             byte = self.memory[0x80 + row]
#             for col in range(10):
#                 if byte & (1 << col):
#                     pyxel.rect(col * 8, row * 4, 7, 3, 9)  # Bigger LED blocks

# if __name__ == "__main__":
#     if len(sys.argv) != 2:
#         print("Usage: python3 emulator.py <program.bin>")
#         sys.exit(1)
#     with open(sys.argv[1], "rb") as f:
#         program = list(f.read())
#     Arch242Emulator(program)

import pyxel
import sys

class Arch242Emulator:
    def __init__(self, program):
        self.memory = [0] * 256
        self.registers = {'ACC': 0, 'CF': 0, 'PC': 0,
                          'R0': 0, 'R1': 0, 'R2': 0, 'R3': 0, 'R4': 0}
        self.delay_counter = 0
        self.load_program(program)
        pyxel.init(100, 80, title="Arch-242 Emulator")
        pyxel.run(self.update, self.draw)

    def load_program(self, program):
        for i, byte in enumerate(program):
            self.memory[i] = byte
        print("Program loaded:", program[:20])

    def fetch(self):
        pc = self.registers['PC']
        opcode = self.memory[pc]
        self.registers['PC'] = (self.registers['PC'] + 1) & 0xFF
        # print(f"PC: {pc:02X}, Opcode: {opcode:02X}")
        return opcode

    def execute(self, opcode):
        if 0x70 <= opcode <= 0x7F:
            imm = opcode & 0x0F
            self.registers['ACC'] = imm

        elif opcode == 0x04:
            self.registers['ACC'] = self.memory[0x80]

        elif opcode == 0x05:
            self.memory[0x80] = self.registers['ACC'] & 0xFF

        elif opcode == 0x06:
            self.memory[0x80], self.memory[0x81] = self.memory[0x81], self.memory[0x80]

        elif opcode == 0x07:
            self.memory[0x81] = self.registers['ACC'] & 0xFF

        elif opcode == 0x08:
            self.registers['ACC'] = self.memory[0x81]

        elif opcode == 0x09:
            self.registers['ACC'] = self.memory[0x90]

        elif opcode == 0x0A:
            self.memory[0x90] = self.registers['ACC'] & 0xFF

        elif opcode == 0x31:
            self.registers['ACC'] = (self.registers['ACC'] + 1) & 0xFF

        elif opcode == 0x3F:
            self.registers['ACC'] = (self.registers['ACC'] - 1) & 0xFF

        # to-ioa (0x0A): memory[0x90] = ACC
        elif opcode == 0x0A:
            self.memory[0x90] = self.registers['ACC'] & 0xFF

        elif opcode == 0x3E:
            pass

        elif 0xB0 <= opcode <= 0xBF:
            addr = self.fetch()
            if self.registers['ACC'] == 0:
                self.registers['PC'] = addr & 0xFF

        elif 0xE0 <= opcode <= 0xEF:
            addr = self.fetch()
            self.registers['PC'] = addr & 0xFF

        elif opcode == 0x40:
            imm = self.fetch()
            self.registers['ACC'] = (self.registers['ACC'] + imm) & 0xFF

        elif opcode == 0x41:
            imm = self.fetch()
            self.registers['ACC'] = (self.registers['ACC'] - imm) & 0xFF

        elif opcode == 0x42:
            imm = self.fetch()
            self.registers['ACC'] &= imm

        elif opcode == 0x43:
            imm = self.fetch()
            self.registers['ACC'] ^= imm

        elif opcode == 0x44:
            imm = self.fetch()
            self.registers['ACC'] |= imm

        elif 0x20 <= opcode <= 0x24:
            reg_index = opcode - 0x20
            self.registers[f'R{reg_index}'] = self.registers['ACC'] & 0xFF

        elif 0x21 <= opcode <= 0x25:
            reg_index = opcode - 0x21
            self.registers['ACC'] = self.registers[f'R{reg_index}'] & 0xFF

        elif opcode == 0x30:
            self.registers['ACC'] ^= self.registers['R0']

        else:
            print(f"Unknown opcode: {opcode:02X} at PC={self.registers['PC']:02X}")

    def update(self):
        for _ in range(10):
            pc_snapshot = self.registers['PC']
            opcode = self.fetch()
            self.execute(opcode)

            if pc_snapshot == self.registers['PC']:
                self.delay_counter += 1
                if self.delay_counter > 300:
                    print("Stuck loop detected. Exiting...")
                    sys.exit(1)
            else:
                self.delay_counter = 0

        for row in range(20):
            self.memory[0x80 + row] = 0

        snake_x = self.memory[0x80]
        snake_y = self.memory[0x81]

        if 0 <= snake_x < 10 and 0 <= snake_y < 20:
            self.memory[0x80 + snake_y] |= (1 << snake_x)

        direction = 0
        if pyxel.btn(pyxel.KEY_UP):
            direction = 3
        elif pyxel.btn(pyxel.KEY_DOWN):
            direction = 1
        elif pyxel.btn(pyxel.KEY_LEFT):
            direction = 2
        elif pyxel.btn(pyxel.KEY_RIGHT):
            direction = 0

        self.memory[0x90] = direction

    def draw(self):
        pyxel.cls(0)
        for row in range(20):
            byte = self.memory[0x80 + row]
            for col in range(10):
                if byte & (1 << col):
                    pyxel.rect(col * 8, row * 4, 7, 3, 9)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 emulator.py <program.bin>")
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        program = list(f.read())
    Arch242Emulator(program)