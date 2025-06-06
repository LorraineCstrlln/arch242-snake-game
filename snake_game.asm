; === Initialize snake position ===
add 0
add 5
to-mba      ; X = 5

add 0
add 10
to-mdc      ; Y = 10

timer-start     ; Start TIMER

main:
    from-pa
    to-reg r0      ; Load direction input

    from-reg r0
    to-ioa         ; Echo direction to IOA (optional)

    from-mba
    to-reg r1      ; Load X

    from-mdc
    to-reg r2      ; Load Y

    ; Direction checks
    from-reg r0
    sub 0
    beqz right
    nop

    from-reg r0
    sub 1
    beqz down
    nop

    from-reg r0
    sub 2
    beqz left
    nop

    from-reg r0
    sub 3
    beqz up
    nop

    b wait

; === Movement Handlers ===
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
    acc 0
    to-reg r1
    b update

left:
    from-reg r1
    dec
    to-reg r1
    from-reg r1
    sub 0
    beqz wrapxmax
    nop
    b update

wrapxmax:
    acc 9
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
    acc 0
    to-reg r2
    b update

up:
    from-reg r2
    dec
    to-reg r2
    from-reg r2
    sub 0
    beqz wrapymax
    nop
    b update

wrapymax:
    acc 19
    to-reg r2
    b update

; === Draw and Save Position ===
update:
    from-reg r1
    to-mba

    from-reg r2
    to-mdc

    ; Compute addr = 0xC0 + Y
    acc 12
    to-reg r0      ; RB = 0xC

    from-reg r2
    to-reg r1      ; RA = Y

    ; Get X value
    from-reg r1
    to-reg r4      ; r4 = X

    from-reg r4
    to-reg r3      ; r3 = X counter

    acc 1
bitloop:
    from-reg r3
    beqz setbit
    dec
    to-reg r3
    add 1
    b bitloop

setbit:
    to-mba             ; MEM[RB:RA] = bitmask

    b wait

; === Wait until next timer tick (emulator will jump to 0x04 every 4 ticks) ===
wait:
    from-pa
    to-reg r4          ; Still allow updating direction
    b wait             ; Wait forever; emulator will reset PC to 0x04 on timer tick