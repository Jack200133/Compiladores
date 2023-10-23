.data
prompt: .asciiz "Enter the firts number: "
prompt2: .asciiz "Enter the second number: "
result: .asciiz "The result is: "

.text
.globl main

main:
    # Imprimir prompt del primer numero
    li $v0, 4
    la $a0, prompt
    syscall
    
    # Leer primer numero
    li $v0, 5
    syscall
    move $t0, $v0

    # Imprimir prompt del segundo numero
    li $v0, 4
    la $a0, prompt2
    syscall

    # Leer segundo numero
    li $v0, 5
    syscall
    move $t1, $v0

    jal mcd

    move $t1, $v0

    # Imprimir resultado
    li $v0, 4
    la $a0, result
    syscall

    move $a0, $t1
    li $v0, 1
    syscall


    li $v0, 10
    syscall


mcd:
    beq $t0, $t1, iguales  # Si son iguales, ya tenemos el MCD
    blt $t1, $t0, swap  # Si n2 < n1, intercambiar
    sub $t1, $t1, $t0
    j mcd

swap:
    move $t2, $t0
    move $t0, $t1
    move $t1, $t2
    j mcd

iguales:
    move $v0, $t0
    jr $ra

