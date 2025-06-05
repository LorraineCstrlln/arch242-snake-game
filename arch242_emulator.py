import pyxel
import sys

class Arch242Emulator:
    def __init__(self, program):
        self.registers = {}
        self.registers['ACC'] = 0
        self.memory = [0]*256
        self.original_program = program[:]
        self.score = 0
        self.reset()
        pyxel.init(80, 80, title="Arch-242 Snake Game")
        pyxel.run(self.update, self.draw)

    def reset(self):
        self.memory = [0] * 256
        self.registers = {
            'ACC': 0,
            'CF': 0,
            'PC': 0,
            'RA': 0,
            'RB': 0,
            'RC': 0,
            'RD': 0,
            'RE': 0,
            'RF': 0,
            'TEMP': 0,
            'EI': 0,
            'PA': 0,
            'IOA': 0,
            'IOB': 0,
            'IOC': 0
        }
        self.delay_counter = 0
        self.score = 0
        self.load_program(self.original_program)

    def load_program(self, program):
        for i, byte in enumerate(program):
            self.memory[i] = byte

    def fetch(self):
        pc = self.registers['PC']
        opcode = self.memory[pc]
        self.registers['PC'] = (self.registers['PC'] + 1) & 0xFF
        return opcode

    def fetch_next_byte(self):
        pc = self.registers['PC']
        byte = self.memory[pc]
        self.registers['PC'] = (pc + 1) & 0xFF
        return byte

    def execute(self, opcode):
        if opcode == 0x00:  # NOP
            pass
        elif opcode == 0x01:  # LDA immediate
            val = self.fetch_next_byte()
            self.registers['ACC'] = val
        elif opcode == 0x02:  # STA addr
            addr = self.fetch_next_byte()
            self.memory[addr] = self.registers['ACC']
        elif opcode == 0x03:  # ADD immediate
            val = self.fetch_next_byte()
            result = self.registers['ACC'] + val
            self.registers['CF'] = 1 if result > 0xF else 0
            self.registers['ACC'] = result & 0xF
        elif opcode == 0x04:  # SUB immediate
            val = self.fetch_next_byte()
            result = self.registers['ACC'] - val
            self.registers['CF'] = 1 if result < 0 else 0
            self.registers['ACC'] = result & 0xF
        elif opcode == 0x05:  # JMP addr
            addr = self.fetch_next_byte()
            self.registers['PC'] = addr
        elif opcode == 0x06:  # JZ addr
            addr = self.fetch_next_byte()
            if self.registers['ACC'] == 0:
                self.registers['PC'] = addr
        elif opcode == 0x07:  # JC addr
            addr = self.fetch_next_byte()
            if self.registers['CF'] == 1:
                self.registers['PC'] = addr
        elif opcode == 0x08:  # IN port
            port = self.fetch_next_byte()
            if port == 0xA0:
                self.registers['ACC'] = self.registers['IOA']
            elif port == 0xB0:
                self.registers['ACC'] = self.registers['IOB']
            elif port == 0xC0:
                self.registers['ACC'] = self.registers['IOC']
            else:
                self.registers['ACC'] = 0
        elif opcode == 0x09:  # OUT port
            port = self.fetch_next_byte()
            if port == 0xA0:
                self.registers['IOA'] = self.registers['ACC']
            elif port == 0xB0:
                self.registers['IOB'] = self.registers['ACC']
            elif port == 0xC0:
                self.registers['IOC'] = self.registers['ACC']
        elif opcode == 0x0A:  # INC ACC
            self.registers['ACC'] = (self.registers['ACC'] + 1) & 0xF
        elif opcode == 0x0B:  # DEC ACC
            self.registers['ACC'] = (self.registers['ACC'] - 1) & 0xF
        elif opcode == 0x0C:  # AND immediate
            val = self.fetch_next_byte()
            self.registers['ACC'] &= val
        elif opcode == 0x0D:  # OR immediate
            val = self.fetch_next_byte()
            self.registers['ACC'] |= val
        elif opcode == 0x0E:  # XOR immediate
            val = self.fetch_next_byte()
            self.registers['ACC'] ^= val
        elif opcode == 0x0F:  # HALT
            sys.exit(0)
        else:
            pass

    def update(self):
        if pyxel.btnp(pyxel.KEY_R):
            self.reset()
        for _ in range(10):
            pc_snapshot = self.registers['PC']
            opcode = self.fetch()
            self.execute(opcode)
            if pc_snapshot == self.registers['PC']:
                self.delay_counter += 1
                if self.delay_counter > 300:
                    sys.exit(1)
            else:
                self.delay_counter = 0
        for row in range(20):
            self.memory[0x80 + row] = 0
        x = self.memory[0x80]
        y = self.memory[0x81]
        if 0 <= x < 10 and 0 <= y < 20:
            self.memory[0x80 + y] |= (1 << x)
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
        self.registers['PA'] = direction

    def draw(self):
        pyxel.cls(0)
        for row in range(2):
            pyxel.rect(0, row * 4, 80, 4, 12)
        pyxel.text(2, 2, f"Score = {self.score}", 7)
        for row in range(2, 20):
            pyxel.rect(0, row * 4, 7, 3, 8)
            pyxel.rect(72, row * 4, 7, 3, 8)
        for col in range(10):
            pyxel.rect(col * 8, 8, 7, 3, 8)
            pyxel.rect(col * 8, 76, 7, 3, 8)
        for row in range(20):
            row_bits = self.memory[0x80 + row]
            for col in range(10):
                if row >= 2 and (row_bits & (1 << col)):
                    pyxel.rect(col * 8, row * 4, 7, 3, 7)

program = []

if __name__ == "__main__":
    Arch242Emulator(program)
