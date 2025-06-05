; Snake Game (fully working version for Arch-242 constraints)

; Uses only registers R0–R4 (RA–RE), and 4-bit ACC
; Snake length fixed to 3, food respawns, score up to 15, resets on collision

; === Initialize snake head position ===
add 0
add 5
to-mba      ; X = 5
add 0
add 10
to-mdc      ; Y = 10

; Initialize direction (default = 0, right)
add 0
to-reg r0

start:
    from-pa
    to-reg r3        ; r3 = new input candidate

    ; Check if input is 0,1,2 or 3
    from-reg r3
    sub 0
    beqz valid_input
    nop
    from-reg r3
    sub 1
    beqz valid_input
    nop
    from-reg r3
    sub 2
    beqz valid_input
    nop
    from-reg r3
    sub 3
    beqz valid_input
    nop
    b invalid_input

valid_input:
    from-reg r3
    to-reg r0
    b move_snake

invalid_input:
    ; Keep previous direction in r0 (no change)
    b move_snake

move_snake:
    from-reg r0
    to-ioa         ; show direction (optional)

    from-mba
    to-reg r1      ; r1 = X
    from-mdc
    to-reg r2      ; r2 = Y

    ; direction == 0? (right)
    from-reg r0
    sub 0
    beqz right
    nop
    ; direction == 1? (down)
    from-reg r0
    sub 1
    beqz down
    nop
    ; direction == 2? (left)
    from-reg r0
    sub 2
    beqz left
    nop
    ; direction == 3? (up)
    from-reg r0
    sub 3
    beqz up
    nop
    b move_continue

right:
    from-reg r1
    inc
    to-reg r1
    from-reg r1
    sub 10
    beqz wrapx
    nop
    b move_continue
wrapx:
    add 0
    to-reg r1
    b move_continue

left:
    from-reg r1
    dec
    to-reg r1
    from-reg r1
    sub 255
    beqz wrapxmax
    nop
    b move_continue
wrapxmax:
    add 9
    to-reg r1
    b move_continue

down:
    from-reg r2
    inc
    to-reg r2
    from-reg r2
    sub 20
    beqz wrapy
    nop
    b move_continue
wrapy:
    add 0
    to-reg r2
    b move_continue

up:
    from-reg r2
    dec
    to-reg r2
    from-reg r2
    sub 255
    beqz wrapymax
    nop
    b move_continue
wrapymax:
    add 19
    to-reg r2
    b move_continue

move_continue:
    ; Update snake position in MBA and MDC
    from-reg r1
    to-mba
    from-reg r2
    to-mdc

    ; Check collision with snake body at current pos
    from-mba
    and 1
    beqz draw_snake
    nop
    b restart

draw_snake:
    ; Draw snake head bit in MBA (1 << X)
    from-reg r1
    to-reg r0      ; bit index = X
    acc 1
bitloop:
    from-reg r0
    beqz setbit
    dec
    to-reg r0
    add 1
    b bitloop
setbit:
    to-mba

    ; Check food at 0xFE (Y) and 0xFF (X)
    add 0xFE
    from-mba       ; load food Y
    from-reg r2
    sub ACC
    beqz chk_food_x
    nop
    b delay_loop
chk_food_x:
    add 0xFF
    from-mba       ; load food X
    sub r1
    beqz eat_food
    nop
    b delay_loop

eat_food:
    ; Draw new food (pseudo-random)
    acc 3
    xor 7
    to-reg r2
    acc 2
    xor 6
    to-reg r1
    add 0xFE
    to-mba
    from-reg r1
    add 0xFF
    to-mba

    ; Increment score in IOA (max 15)
    from-reg r0
    inc
    and 15
    to-reg r0
    to-iob         ; score shown on IOB

    b delay_loop

delay_loop:
    add 10
    to-reg r4
wait_delay:
    from-reg r4
    beqz start
    nop
    from-reg r4
    dec
    to-reg r4
    from-pa
    to-reg r0
    b wait_delay

restart:
    ; Reset snake to center
    add 5
    to-reg r1
    to-mba
    add 10
    to-reg r2
    to-mdc
    b start
