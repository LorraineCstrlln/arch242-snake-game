; Initialize X = 5, Y = 10
add 0          ; clear ACC
add 5
to-mba         ; X

add 0          ; clear ACC
add 10
to-mdc         ; Y

start:
    ; Simulate memory read: direction at 0x90 (assume already loaded to I/O beforehand)
    from-pa
    to-reg r0   ; direction -> r0

    ; Debug: store direction to IOA for emulator to confirm key press
    from-reg r0
    to-ioa

    ; Load X and Y into r1 and r2
    from-mba
    to-reg r1

    from-mdc
    to-reg r2

    ; Compare direction == 0 (right)
    from-reg r0
    sub 0
    beqz right
    nop

    ; Compare direction == 1 (down)
    from-reg r0
    sub 1
    beqz down
    nop

    ; Compare direction == 2 (left)
    from-reg r0
    sub 2
    beqz left
    nop

    ; Compare direction == 3 (up)
    from-reg r0
    sub 3
    beqz up
    nop

    b update     ; Unknown direction → skip

right:
    from-reg r1
    inc
    to-reg r1

    from-reg r1
    sub 10
    beqz wrapx
    nop
    b update

wrapx:
    add 0
    to-reg r1
    b update

left:
    from-reg r1
    dec
    to-reg r1

    from-reg r1
    sub 255
    beqz wrapxmax
    nop
    b update

wrapxmax:
    add 0
    add 9
    to-reg r1
    b update

down:
    from-reg r2
    inc
    to-reg r2

    from-reg r2
    sub 20
    beqz wrapy
    nop
    b update

wrapy:
    add 0
    to-reg r2
    b update

up:
    from-reg r2
    dec
    to-reg r2

    from-reg r2
    sub 255
    beqz wrapymax
    nop
    b update

wrapymax:
    add 0
    add 19
    to-reg r2
    b update

update:
    ; Write updated X and Y
    from-reg r1
    to-mba

    from-reg r2
    to-mdc

    ; Delay loop initialization
    add 0
    add 10       ; Set delay count
    to-reg r3

delay_loop:
    from-reg r3
    dec
    to-reg r3

    from-reg r3
    beqz start
    nop
    b delay_loop