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

Development Notes
- CPU architecture is 4 bit Harvard
- Instruction formant: 16 bit fixed width
- PC and memory are byte-addressable
- Emulator is built with Pytho and Pyxel
- Assembly is highly compact due to 4 bit register contraints

   
## Requirements
- Python 3.7+
- Pyxel

Install dependecies:
pip install pyxel

##Usage/Run
python arch242_assembler.py snake_game.asm snake_game.bin
python arch242_emulator.py snake_game.bin

Authors
CS 21 24.2 
