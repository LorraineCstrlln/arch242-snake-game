import pyxel
import sys
import random

class Arch242Emulator:
    def __init__(self, program):
        self.memory = [0] * 256
        self.registers = {
            # General reg
            'RA': 0,
            'RB': 0,
            'RC': 0,
            'RD': 0,
            'RE': 0,

            # Special reg
            'ACC': 0,     # 4
            'CF': 0,      # 1
            'PC': 0,      # 16
            'TEMP': 0,    # 16
            # 'TIMER': 0,   # 8
            # 'EI': 0,      # 1
            'PA': 0,      # 4

            # I/O reg
            'IOA': 0,     # 4
            # 'IOB': 0,     # 4
            # 'IOC': 0      # 4
        }

        self.delay_counter = 0
        # self.timer_running = False
        self.load_program(program)

        # === SnakeGame State ===
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        # ========================

        pyxel.init(80, 80, title="Arch-242 Snake Game")
        pyxel.run(self.update, self.draw)

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
        self.registers['PC'] = (pc + 1) & 0xFF  # PC is 8-bit for 256-byte memory
        return byte

    def spawn_food(self):
        while True:
            food = (random.randint(0, 9), random.randint(2, 18))
            if food not in self.snake:
                return food

    def reset_snake_game(self):
        self.snake = [(5, 10), (4, 10), (3, 10)]
        self.direction = (1, 0)
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False

    def execute(self, opcode):
        # helper to get memory address from 2 registers: upper nibble first
        def get_addr(reg_high, reg_low):
            return ((self.registers[reg_high] & 0x0F) << 4) | (self.registers[reg_low] & 0x0F)

        # rot-r 0x00: rotate ACC right by 1 bit
        if opcode == 0x00:
            self.registers['ACC'] = ((self.registers['ACC'] >> 1) | ((self.registers['ACC'] & 1) << 3)) & 0xF

        # rot-l 0x01: rotate ACC left by 1 bit
        elif opcode == 0x01:
            self.registers['ACC'] = ((self.registers['ACC'] << 1) | ((self.registers['ACC'] >> 3) & 1)) & 0xF

        # rot-rc 0x02: rotate CF:ACC right by 1 bit
        elif opcode == 0x02:
            combined = (self.registers['CF'] << 4) | self.registers['ACC']
            combined = ((combined >> 1) | ((combined & 1) << 4)) & 0x1F
            self.registers['CF'] = (combined >> 4) & 1
            self.registers['ACC'] = combined & 0xF

        # rot-lc 0x03: rotate CF:ACC left by 1 bit
        elif opcode == 0x03:
            combined = (self.registers['CF'] << 4) | self.registers['ACC']
            combined = ((combined << 1) | ((combined >> 4) & 1)) & 0x1F
            self.registers['CF'] = (combined >> 4) & 1
            self.registers['ACC'] = combined & 0xF

        # from-mba 0x04: ACC = MEM[RB:RA]
        elif opcode == 0x04:
            addr = get_addr('RB', 'RA')
            self.registers['ACC'] = self.memory[addr] & 0xF

        # to-mba 0x05: MEM[RB:RA] = ACC
        elif opcode == 0x05:
            addr = get_addr('RB', 'RA')
            self.memory[addr] = self.registers['ACC'] & 0xF

        # from-mdc 0x06: ACC = MEM[RD:RC]
        elif opcode == 0x06:
            addr = get_addr('RD', 'RC')
            self.registers['ACC'] = self.memory[addr] & 0xF

        # to-mdc 0x07: MEM[RD:RC] = ACC
        elif opcode == 0x07:
            addr = get_addr('RD', 'RC')
            self.memory[addr] = self.registers['ACC'] & 0xF

        # addc-mba 0x08: ACC = ACC + MEM[RB:RA] + CF
        elif opcode == 0x08:
            addr = get_addr('RB', 'RA')
            total = self.registers['ACC'] + (self.memory[addr] & 0xF) + self.registers['CF']
            self.registers['ACC'] = total & 0xF
            self.registers['CF'] = 1 if total > 0xF else 0

        # add-mba 0x09: ACC = ACC + MEM[RB:RA]
        elif opcode == 0x09:
            addr = get_addr('RB', 'RA')
            total = self.registers['ACC'] + (self.memory[addr] & 0xF)
            self.registers['ACC'] = total & 0xF
            self.registers['CF'] = 1 if total > 0xF else 0

        # subc-mba 0x0A: ACC = ACC - MEM[RB:RA] + CF
        elif opcode == 0x0A:
            addr = get_addr('RB', 'RA')
            diff = self.registers['ACC'] - (self.memory[addr] & 0xF) + self.registers['CF']
            if diff < 0:
                diff += 16
                self.registers['CF'] = 1  # underflow
            else:
                self.registers['CF'] = 0
            self.registers['ACC'] = diff & 0xF

        # sub-mba 0x0B: ACC = ACC - MEM[RB:RA]
        elif opcode == 0x0B:
            addr = get_addr('RB', 'RA')
            diff = self.registers['ACC'] - (self.memory[addr] & 0xF)
            if diff < 0:
                diff += 16
                self.registers['CF'] = 1
            else:
                self.registers['CF'] = 0
            self.registers['ACC'] = diff & 0xF

        # inc*-mba 0x0C: MEM[RB:RA] += 1 (wrap 4 bits)
        elif opcode == 0x0C:
            addr = get_addr('RB', 'RA')
            self.memory[addr] = (self.memory[addr] + 1) & 0xF

        # dec*-mba 0x0D: MEM[RB:RA] -= 1 (wrap 4 bits)
        elif opcode == 0x0D:
            addr = get_addr('RB', 'RA')
            self.memory[addr] = (self.memory[addr] - 1) & 0xF

        # inc*-mdc 0x0E: MEM[RD:RC] += 1 (wrap 4 bits)
        elif opcode == 0x0E:
            addr = get_addr('RD', 'RC')
            self.memory[addr] = (self.memory[addr] + 1) & 0xF

        # dec*-mdc 0x0F: MEM[RD:RC] -= 1 (wrap 4 bits)
        elif opcode == 0x0F:
            addr = get_addr('RD', 'RC')
            self.memory[addr] = (self.memory[addr] - 1) & 0xF

        # inc*-reg 0x10 to 0x14: 0001RRR0
        elif 0x10 <= opcode <= 0x14:
            reg_index = (opcode >> 1) & 0x7
            reg_name = ['RA', 'RB', 'RC', 'RD', 'RE'][reg_index]
            self.registers[reg_name] = (self.registers[reg_name] + 1) & 0xF

        # dec*-reg 0x11 to 0x15: 0001RRR1
        elif 0x11 <= opcode <= 0x15:
            reg_index = (opcode >> 1) & 0x7
            reg_name = ['RA', 'RB', 'RC', 'RD', 'RE'][reg_index]
            self.registers[reg_name] = (self.registers[reg_name] - 1) & 0xF

        # to-reg 0x20 to 0x28 (0010RRR0): REG[RRR] = ACC
        elif 0x20 <= opcode <= 0x28 and (opcode & 1) == 0:
            reg_index = (opcode >> 1) & 0x7
            if reg_index <= 4:
                reg_name = ['RA', 'RB', 'RC', 'RD', 'RE'][reg_index]
                self.registers[reg_name] = self.registers['ACC'] & 0xF

        # from-reg 0x21 to 0x29 (0010RRR1): ACC = REG[RRR]
        elif 0x21 <= opcode <= 0x29 and (opcode & 1) == 1:
            reg_index = (opcode >> 1) & 0x7
            if reg_index <= 4:
                reg_name = ['RA', 'RB', 'RC', 'RD', 'RE'][reg_index]
                self.registers['ACC'] = self.registers[reg_name] & 0xF

        # clr-cf 0x2A
        elif opcode == 0x2A:
            self.registers['CF'] = 0

        # set-cf 0x2B
        elif opcode == 0x2B:
            self.registers['CF'] = 1

        # removed EI
        # # set-ei 0x2C (Enable Interrupts)
        # elif opcode == 0x2C:
        #     self.registers['EI'] = 1

        # # clr-ei 0x2D (Disable Interrupts)
        # elif opcode == 0x2D:
        #     self.registers['EI'] = 0

        # ret 0x2E
        elif opcode == 0x2E:
            self.registers['PC'] = (self.registers['PC'] & 0xF000) | (self.registers['TEMP'] & 0x0FFF)
            self.registers['TEMP'] = 0

        # retc 0x2F
        elif opcode == 0x2F:
            self.registers['PC'] = (self.registers['PC'] & 0xF000) | (self.registers['TEMP'] & 0x0FFF)
            self.registers['CF'] = (self.registers['TEMP'] >> 12) & 1
            self.registers['TEMP'] = 0

        # from-pa 0x30
        elif opcode == 0x30:
            self.registers['ACC'] = self.registers.get('PA', 0) & 0xF
            # print(f"[from-pa] ACC = {self.registers['ACC']}")

        # inc 0x31
        elif opcode == 0x31:
            self.registers['ACC'] = (self.registers['ACC'] + 1) & 0xF

        # from-ioa 0x32
        elif opcode == 0x32:  # from-ioa
            self.registers['ACC'] = self.registers['IOA'] & 0xF
        
        # # to-ioa 0x32
        # elif opcode == 0x32:
        #     self.registers['IOA'] = self.registers['ACC'] & 0xF

        # # to-iob 0x33
        # elif opcode == 0x33:
        #     self.registers['IOB'] = self.registers['ACC'] & 0xF

        # # to-ioc 0x34
        # elif opcode == 0x34:
        #     self.registers['IOC'] = self.registers['ACC'] & 0xF

        # # to-iod 0x35
        # elif opcode == 0x35:
        #     self.registers['IOD'] = self.registers['ACC'] & 0xF

        # # to-ioe 0x36
        # elif opcode == 0x36:
        #     self.registers['IOE'] = self.registers['ACC'] & 0xF

        # # to-iof 0x37
        # elif opcode == 0x37:
        #     self.registers['IOF'] = self.registers['ACC'] & 0xF

        # to-pc 0x38
        elif opcode == 0x38:
            self.registers['PC'] = self.registers['ACC']


        # add <imm> (0x40)
        elif opcode == 0x40:
            imm = self.fetch_next_byte() & 0x0F
            self.registers['ACC'] = (self.registers['ACC'] + imm) & 0xF

        # sub <imm>
        elif opcode == 0x41:
            imm = self.fetch_next_byte() & 0x0F
            diff = self.registers['ACC'] - imm
            if diff < 0:
                diff += 16
                self.registers['CF'] = 1
            else:
                self.registers['CF'] = 0
            self.registers['ACC'] = diff & 0xF

        # and <imm>
        elif opcode == 0x42:
            imm = self.fetch_next_byte() & 0x0F
            self.registers['ACC'] = self.registers['ACC'] & imm

        # xor <imm>
        elif opcode == 0x43:
            imm = self.fetch_next_byte() & 0x0F
            self.registers['ACC'] = self.registers['ACC'] ^ imm

        # or <imm>
        elif opcode == 0x44:
            imm = self.fetch_next_byte() & 0x0F
            self.registers['ACC'] = self.registers['ACC'] | imm

        # call 0x4C [2-byte instruction]
        elif opcode == 0x4C:
            addr = self.fetch_next_byte()
            self.registers['TEMP'] = self.registers['PC'] + 2  # save return address
            self.registers['PC'] = addr

        # reti 0x4D
        elif opcode == 0x4D:
            self.registers['PC'] = self.registers['TEMP']
            self.registers['TEMP'] = 0
        
        # nop
        elif opcode == 0x3E:
            pass  # No operation
        
        # dec 
        elif opcode == 0x3F:
            self.registers['ACC'] = (self.registers['ACC'] - 1) & 0xF

        # acc <imm>
        elif 0x70 <= opcode <= 0x7F:
            self.registers['ACC'] = opcode & 0x0F

        # beqz <imm> (0xB0–0xB7)
        elif 0xB0 <= opcode <= 0xB7:
            target = self.fetch_next_byte()
            if self.registers['ACC'] == 0:
                self.registers['PC'] = target

        # b <imm>
        elif 0xE0 <= opcode <= 0xEF:
            target = self.fetch_next_byte()  # 8-bit only
            self.registers['PC'] = target
            # print(f"b <imm>: Jumping to {target:02X}")

        # # timer-start 0x38
        # elif opcode == 0x38:
        #     self.timer_running = True

        # # timer-end 0x39
        # elif opcode == 0x39:
        #     self.timer_running = False

        # # from-timerl 0x3A
        # elif opcode == 0x3A:
        #     self.registers['ACC'] = self.registers['TIMER'] & 0x0F

        # # from-timerh 0x3B
        # elif opcode == 0x3B:
        #     self.registers['ACC'] = (self.registers['TIMER'] >> 4) & 0x0F

        # # to-timerl 0x3C
        # elif opcode == 0x3C:
        #     self.registers['TIMER'] = (self.registers['TIMER'] & 0xF0) | (self.registers['ACC'] & 0x0F)

        # # to-timerh 0x3D
        # elif opcode == 0x3D:
        #     self.registers['TIMER'] = ((self.registers['ACC'] & 0x0F) << 4) | (self.registers['TIMER'] & 0x0F)

        # # timer <imm> 0x47
        # elif opcode == 0x47:
        #     imm = self.fetch_next_byte() & 0x0F
        #     self.registers['TIMER'] = imm

        # # b-timer <imm> 0xD0–0xD7
        # elif 0xD0 <= opcode <= 0xD7:
        #     target = self.fetch_next_byte()
        #     if self.timer_running:
        #         self.registers['PC'] = target

        else:
            raise ValueError(f"Unknown opcode: 0x{opcode:02X}")

    def update(self):
        # if self.timer_running:
        #     if not hasattr(self, 'timer_tick_counter'):
        #         self.timer_tick_counter = 0
        #     self.timer_tick_counter += 1
        #     if self.timer_tick_counter >= 4:
        #         self.timer_tick_counter = 0
        #         self.registers['TIMER'] = (self.registers['TIMER'] + 1) & 0xFF
        #         self.registers['PC'] = 0x04  # Reset PC to 0x04 when timer ticks

        if pyxel.btnp(pyxel.KEY_R):
            self.registers['PC'] = 0
            self.delay_counter = 0

        for _ in range(10):
            pc_snapshot = self.registers['PC']
            opcode = self.fetch()

            self.execute(opcode)
            
            if pc_snapshot == self.registers['PC']:
                self.delay_counter += 1
                if self.delay_counter > 300:
                    # print(f"[Warning] Looping at PC = 0x{pc_snapshot:02X} (likely intentional)")
                    self.delay_counter = 0  # reset counter
            else:
                self.delay_counter = 0

        # === Python Snake Logic ===
        if self.game_over:
            if pyxel.btnp(pyxel.KEY_R):
                self.reset_snake_game()
            return

        if pyxel.frame_count % 8 != 0:
            return

        dx, dy = self.direction

        if pyxel.btn(pyxel.KEY_RIGHT) and (dx, dy) != (-1, 0):
            self.direction = (1, 0)
        elif pyxel.btn(pyxel.KEY_LEFT) and (dx, dy) != (1, 0):
            self.direction = (-1, 0)
        elif pyxel.btn(pyxel.KEY_DOWN) and (dx, dy) != (0, -1):
            self.direction = (0, 1)
        elif pyxel.btn(pyxel.KEY_UP) and (dx, dy) != (0, 1):
            self.direction = (0, -1)

        head_x, head_y = self.snake[0]
        dx, dy = self.direction
        new_head = ((head_x + dx) % 10, (head_y + dy - 2) % 17 + 2)

        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
        else:
            self.snake.pop()
        # ====================

        # Clear frame memory area
        for row in range(20):
            self.memory[0x80 + row] = 0

        # Read snake length
        # length = self.memory[0xA1]  # Snake length
        # for i in range(length):
        #     x = self.memory[0xA2 + i * 2]
        #     y = self.memory[0xA2 + i * 2 + 1]
        #     if 0 <= x < 10 and 0 <= y < 20:
        #         self.memory[0x80 + y] |= (1 << x)

        length = self.memory[0xA1]
        max_safe_len = min(length, (0xFF - 0xA2) // 2)

        for i in range(max_safe_len):
            addr_x = 0xA2 + i * 2
            addr_y = addr_x + 1
            if addr_y > 0xFF:
                break
            x = self.memory[addr_x]
            y = self.memory[addr_y]
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

        # Draw game border
        border_color = 5  # dark gray
        pyxel.rect(0, 0, 80, 8, border_color)     # top
        # pyxel.rect(0, 76, 80, 4, border_color)    # bottom
        # pyxel.rect(0, 8, 8, 68, border_color)     # left
        # pyxel.rect(72, 8, 8, 68, border_color)    # right

        # Draw snake
        if self.snake:
            head_x, head_y = self.snake[0]
            pyxel.rect(head_x * 8, head_y * 4, 7, 3, 11)
            for x, y in self.snake[1:]:
                pyxel.rect(x * 8, y * 4, 7, 3, 3) 

        # Draw food
        fx, fy = self.food
        pyxel.rect(fx * 8, fy * 4, 7, 3, 8)

        # Draw score
        pyxel.text(2, 2, f"Score: {self.score}", 7)
        if self.game_over:
            pyxel.text(16, 40, "Press R to retry", 7)
        # ==========================


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python3 emulator.py <program.bin>")
        sys.exit(1)
    with open(sys.argv[1], "rb") as f:
        program = list(f.read())
    Arch242Emulator(program)
