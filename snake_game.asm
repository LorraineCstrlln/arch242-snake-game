; === INIT ===
acc 0x0A
to-reg r0
acc 0x00
to-reg r1

from-reg r4
to-mba          ; [A0] = 0

inc*-reg r1
from-reg r4
to-mba          ; [A1] = 0

inc*-reg r1
from-reg r4
to-mba          ; [A2] = 0

inc*-reg r1
from-reg r4
to-mba          ; [A3] = 0

init:
    acc 0
    to-reg r0
    to-reg r1
    to-reg r2

    ; Head = (0,0)
    acc 0
    to-reg r3 ;X
    acc 0
    to-reg r4 ;Y

    ; store to snake head -> A2 (X), A3 (Y)
    acc 0x0A
    to-reg r0       ; RB = 0x0A
    acc 0x02
    to-reg r1       ; RA = 0x02
    from-reg r3
    to-mba          ; [0xA2] = 5
    inc*-reg r1
    from-reg r4
    to-mba          ; [0xA3] = 10

    ; length = 1 (snake bodeh)
    acc 1
    acc 0x0A
    to-reg r0
    acc 0x01
    to-reg r1
    to-mba          ; [0xA1] = 1

    ; score = 0 (default)
    acc 0
    to-reg r4
    acc 0x0A
    to-reg r0
    acc 0x00
    to-reg r1
    from-reg r4
    to-mba

    ; Food pos = (3, 5)
    acc 3
    acc 0x0B
    to-reg r0
    acc 0x00
    to-reg r1
    to-mba          ; [0xB0] = 3
    acc 5
    inc*-reg r1
    to-mba          ; [0xB1] = 5

    b main

; === Main Loop ===
main:
    ; IOA: direction
    from-ioa
    to-reg r4       ; r4 = dir

    ; load head 
    acc 0x0A
    to-reg r0
    acc 0x02
    to-reg r1
    from-mba        ; X
    to-reg r2
    inc*-reg r1
    from-mba        ; Y
    to-reg r3

    ; direction (r4)
    from-reg r4
    sub 0
    beqz dir_right
    from-reg r4
    sub 1
    beqz dir_down
    from-reg r4
    sub 2
    beqz dir_left
    from-reg r4
    sub 3
    beqz dir_up
    b store_head

dir_right:
    inc*-reg r2
    from-reg r2
    sub 10
    beqz wrap_x
    b store_head
wrap_x:
    acc 0
    to-reg r2
    b store_head

dir_left:
    dec*-reg r2
    from-reg r2
    sub 0
    beqz wrap_xmax
    b store_head
wrap_xmax:
    acc 9
    to-reg r2
    b store_head

dir_down:
    inc*-reg r3
    from-reg r3
    sub 20
    beqz wrap_y
    b store_head
wrap_y:
    acc 2
    to-reg r3
    b store_head

dir_up:
    dec*-reg r3
    from-reg r3
    sub 2
    beqz wrap_ymax
    b store_head
wrap_ymax:
    acc 18
    to-reg r3

store_head:
    ; store updated head -> A2, A3
    acc 0x0A
    to-reg r0
    acc 0x02
    to-reg r1
    from-reg r2
    to-mba
    inc*-reg r1
    from-reg r3
    to-mba

    ; draw head: RB = 0x0C, RA = Y
    acc 0x0C
    to-reg r0
    from-reg r3
    to-reg r1
    from-reg r2
    to-reg r4        ; bit loop counter
    acc 1

bitloop:
    from-reg r4
    beqz setpixel
    dec*-reg r4
    add 1
    b bitloop

setpixel:
    to-mba
    b wait

wait:
    from-ioa
    to-reg r5
    from-reg r5
    sub 0
    bnez main
    b wait

; === Eat Food Routine ===
eat_food:
    ; Load score from memory [A0] (score addr = 0x0A, 0x00)
    acc 0x0A
    to-reg r0
    acc 0x00
    to-reg r1
    from-mba           ; ACC = score
    inc                ; ACC = score + 1
    to-mba             ; store new score

    ; Reset food position to (1,1) as example
    acc 0x0B
    to-reg r0
    acc 0x00
    to-reg r1
    acc 1
    to-mba
    inc*-reg r1
    acc 1
    to-mba

    b wait