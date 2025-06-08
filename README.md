# arch242-snake-game Project

A full stack of tools and components to simulate a 4 bit custom Harvard Architecutre, including:
- Assembler: A Python based assembler that compiles custom '.asm' files into machine code.
- Emulator: A Python base emulator that runs the compile machine code using Pyxel for display and input
- Snake.asm: An assembly program that runs on the custom architecture


Assembler
- arch242_assembler.py #Converts .asm to .bin
Features:
- Supports instructions like to-reg, add-mba, jmp, b. beqz, etc.
- Supoerts .byte <value> for raw memory initialization
- Outputs in hexadecimal format compatible with the emulator

Emulator
- arch242_emulator.py #Runs machin code in Pyxel
Features:
- 256 byte memory
- 4 bit registers and ACC
- Memory-mapped I/O
    - 0xF0 to 0xFF: LED display matrix
    - IOA: USer input
 - Supports real-time timer ticks and movement 

Programs
- snake_game.asm #Assembly program of the Snake game
- snake_game.bin #Machine code output from assembler
Features:
- snake_game.asm program implements a playable snake game:
   - 20x10 display grid
   - Snake grows
   - Controlled via memory-mapped input(IOA)
   - Score tracking and random fruit spawning
 
Controls
Use emulator input handling mapped to:
- IOA = 1:Up
- IOA = 2:Down
- IOA = 3:Left
- IOA = 4:Right

Logisim
- arch242.circ is intented to be loaded by Logisim-evolution v3.9.0
Core Components
- PC: Holds instruction address
- instrmem: Instruciton Memory
- instrlengthdec: Decoder for choosing between 1-byte or 2-byte instructions
- immdec: Immediate Decoder
- maindec: Control Unit
- regfile: Registers RA-RE
- Special Registers: ACC, CF, TEMP
- alu: Handles arithmetic/logical operations
- rotate: Handles rotate operations
- aludec: Decoder for alu
- datamem: Data memory
Control Signals
- RegWrite: Enable write to regfile
- ACCWrite: Enable write to ACC
- MemWrite: Enable memory write
- ResultSrc: Select result for ACC input or register write input
- CFWrite: Enable write to CF
- DataSrc: Select data source (ACC or register)
- MemSrc: Choose memory address source (RA:RB or RC:RD)
- RegSrc: Select general register (RA-RE)
- ALUSrcA/ALUSrcB: Select ALU input operands
- CFSrc: Select CF source
- PCSrc: Select PC update source
- TEMPSrc: Selects input to TEMP register
- TEMPWrite: Enables writing to TEMP register
- DualWrite: Enables writing to 2 general registers (RA-RE) at once
- Carry: Select whether ALU uses carry-in
- Branch: Enables conditional branch
- BEQZ: Inverts conditional branch logic (for beqz, beqz-cf)
Testing
- modify instrmem which uses 2 ROMs that stores 1-byte instructions (2nd ROM is used for 2-byte instructions)
- using probes to track data values

Development Notes
- CPU architecture is 4 bit Harvard
- Instruction formant: 16 bit fixed width
- PC and memory are byte-addressable
- Emulator is built with Pytho and Pyxel
- Assembly is highly compact due to 4 bit register contraints
- Control logic in Logisim is purely combinational
- Logisim's overall design prioritize clarity over hardware minimalism
   
## Requirements ##
- Python 3.7+
- Pyxel
- Logisim Evolution v3.9.0

Install dependecies:
pip install pyxel
https://github.com/logisim-evolution/

## Usage/Run ##
- python arch242_assembler.py snake_game.asm snake_game.bin
- python arch242_emulator.py snake_game.bin

## Authors ##
Project by:
- Lorraine Gwen M. Castrillon 
- Gabriel Inigo D. De Guzman
- Miguel Joaquin Millora
- Vitro Atienza Enrique

*(University of the Philippines - Diliman, Department of Computer Science)*
