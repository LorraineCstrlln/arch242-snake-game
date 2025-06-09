# Arch242 Snake Game Project

## Overview

This project simulates a custom 4-bit Harvard architecture, featuring a full toolchain and components to assemble, emulate, and run programs written in a custom assembly language.

It includes:  
- **Assembler:** A Python-based assembler to compile `.asm` source files into machine code.  
- **Emulator:** A Python-based emulator using Pyxel for display and input, which runs the compiled machine code.  
- **Snake.asm:** An assembly program implementing a playable Snake game on the custom architecture.

> **Note:** Professor's changes have been implemented in Part A of the code.

---

## Components

### Assembler (`parta1.py`)
- Converts `.asm` files into `.bin` machine code.
- Supports instructions like `to-reg`, `add-mba`, `jmp`, `b`, `beqz`, and others.
- Supports `.byte <value>` directive for raw memory initialization.
- Outputs machine code in hexadecimal format compatible with the emulator.

### Emulator (`parta2.py`)
- Runs machine code using Pyxel for graphical display and input.
- Features 256 bytes of memory.
- 4-bit registers and accumulator (ACC).
- Memory-mapped I/O:  
  - `0xF0` to `0xFF`: LED display matrix  
  - `IOA`: User input port
- Supports real-time timer ticks for smooth movement.

### Snake Game Program
- `parta3.asm`: Assembly source for the Snake game.  
- `snake_game.bin`: Machine code produced by the assembler.

**Features of the Snake game:**  
- 20x10 display grid.  
- Snake grows as it eats fruit.  
- Controlled via memory-mapped input (`IOA`).  
- Score tracking and random fruit spawning.

---

## Controls

User inputs are mapped to the `IOA` memory location as follows:  
- `IOA = 1`: Up  
- `IOA = 2`: Down  
- `IOA = 3`: Left  
- `IOA = 4`: Right  

---

## How to Run

### Assemble the Snake Game Program

Run the assembler to convert the assembly source file (`snake_game.asm`) into machine code (`snake_game.bin`):

```
python parta1.py parta3.asm snake_game.bin
```

### Run the Emulator

Launch the emulator with the compiled machine code file:

```
python parta2.py snake_game.bin
```

---

## Logisim Circuit (`partb.circ`)

Designed to be loaded in **Logisim-evolution v3.9.0**, this file contains the CPU implementation of the custom architecture.

**Core Components:**  
- PC (Program Counter)  
- Instruction Memory (`instrmem`)  
- Instruction Length Decoder (`instrlengthdec`) for 1- or 2-byte instructions  
- Immediate Decoder (`immdec`)  
- Control Unit (`maindec`)  
- Register File (`regfile`) with registers RA to RE  
- Special Registers: ACC, CF, TEMP  
- ALU (Arithmetic Logic Unit)  
- Rotate Unit  
- ALU Decoder (`aludec`)  
- Data Memory (`datamem`)

**Control Signals:**  
- `RegWrite`: Enable register write  
- `ACCWrite`: Enable ACC write  
- `MemWrite`: Enable memory write  
- `ResultSrc`: Select input source for ACC or register write  
- `CFWrite`: Enable CF write  
- `DataSrc`: Select data source (ACC or register)  
- `MemSrc`: Select memory address source (RA:RB or RC:RD)  
- `RegSrc`: Select general register (RA-RE)  
- `ALUSrcA`, `ALUSrcB`: Select ALU input operands  
- `CFSrc`: Select CF source  
- `PCSrc`: Select PC update source  
- `TEMPSrc`: Select TEMP register input  
- `TEMPWrite`: Enable TEMP register write  
- `DualWrite`: Write to two general registers simultaneously  
- `Carry`: Select carry-in for ALU  
- `Branch`: Enable conditional branch  
- `BEQZ`: Invert conditional branch logic (for `beqz`, `beqz-cf`)

**Testing:**  
- Modify instruction memory ROMs (two ROMs for 1-byte and 2-byte instructions)  
- Use probes to monitor data values

---

## Development Notes
- CPU architecture is 4 bit Harvard
- Instruction formant: 16 bit fixed width
- PC and memory are byte-addressable
- Emulator is built with Pytho and Pyxel
- Assembly is highly compact due to 4 bit register contraints
- Control logic in Logisim is purely combinational
- Logisim's overall design prioritize clarity over hardware minimalism
   
---

## Requirements
- Python 3.7+
- Pyxel (`pip install pyxel`)  
- Logisim Evolution v3.9.0 ([https://github.com/logisim-evolution/](https://github.com/logisim-evolution/))

---

## Authors ##
Project by:
- Lorraine Gwen M. Castrillon 
- Gabriel Inigo D. De Guzman
- Miguel Joaquin Millora
- Vitro Atienza Enrique

*(University of the Philippines - Diliman, Department of Computer Science)*