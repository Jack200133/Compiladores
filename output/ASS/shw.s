.data
str0: .asciiz "Hello World\n"

.text

main:

jal CLASS_Main

# ------> FUNCIONES BÁSICAS
out_string:
    li $v0, 4
    syscall
    jr $ra


out_int:
    li $v0, 1
    syscall
    jr $ra



CLASS_Main:

# ------> RESERVAR ESPACIO EN EL HEAP PARA LA CLASE Main
    li $a0, 12
    li $v0, 9
    syscall
    move $t8, $v0

# ---> RESERVAR 5 BYTES EN EL HEAP
    li $t7, 5
    move $a0, $t7
    li $v0, 9
    syscall
    move $t7, $v0

# ---> ALMACENAR CADENA EN HEAP (EN EL ESPACIO RESERVADO)
    li $t6, 77
    sb $t6, 0($t7)
    li $t6, 97
    sb $t6, 1($t7)
    li $t6, 105
    sb $t6, 2($t7)
    li $t6, 110
    sb $t6, 3($t7)
    sb $zero, 4($t7)

    sw $t7, 0($t8)
    move $s7, $t8

# ------> sp_GLOBAL[index] = value;

# ---> RESERVAR 9 BYTES EN EL HEAP
    li $t8, 9
    move $a0, $t8
    li $v0, 9
    syscall
    move $t8, $v0

# ---> ALMACENAR CADENA EN HEAP (EN EL ESPACIO RESERVADO)
    li $t7, 83
    sb $t7, 0($t8)
    li $t7, 116
    sb $t7, 1($t8)
    li $t7, 101
    sb $t7, 2($t8)
    li $t7, 102
    sb $t7, 3($t8)
    li $t7, 97
    sb $t7, 4($t8)
    li $t7, 110
    sb $t7, 5($t8)
    li $t7, 111
    sb $t7, 6($t8)
    li $t7, 10
    sb $t7, 7($t8)
    sb $zero, 8($t8)

    sw $t8, 4($s7)


# ------> sp_GLOBAL[index] = value;

# ---> RESERVAR 2 BYTES EN EL HEAP
    li $t8, 2
    move $a0, $t8
    li $v0, 9
    syscall
    move $t8, $v0

# ---> ALMACENAR CADENA EN HEAP (EN EL ESPACIO RESERVADO)
    li $t7, 10
    sb $t7, 0($t8)
    sb $zero, 1($t8)

    sw $t8, 8($s7)

    jal Main.main


Main.print_name:
    move $s1, $a0
# ------> INICIALIZAR MEMORIA DE LA FUNCIÓN Main.print_name
    addi $sp, $sp, -8
    sw $ra, 4($sp)
    sw $fp, 0($sp)
    move $fp, $sp
    addi $sp, $sp, -12
    sw $s1, 0($sp)

# ------> sp[index] = PARAM_X
    sw $a1, 4($sp)

    lw $s2, 0($sp)
    move $s1, $s2

# ------> OUT_STRING
    lw $a0, 4($sp)
    jal out_string


# ------> RETURN REGISTRO[index];
    move $v0, $t0

# ------> FIN DE LA FUNCIÓN Main.print_name
    move $sp, $fp
    lw $fp, 0($sp)
    lw $ra, 4($sp)
    addi $sp, $sp, 8
    jr $ra


Main.main:
# ------> INICIALIZAR MEMORIA DE LA FUNCIÓN Main.main
    addi $sp, $sp, -8
    sw $ra, 4($sp)
    sw $fp, 0($sp)
    move $fp, $sp
    addi $sp, $sp, -16
    sw $s7, 0($sp)

# ------> sp[index] = value;

# ---> RESERVAR 4 BYTES EN EL HEAP
    li $t8, 4
    move $a0, $t8
    li $v0, 9
    syscall
    move $t8, $v0

# ---> ALMACENAR CADENA EN HEAP (EN EL ESPACIO RESERVADO)
    li $t7, 72
    sb $t7, 0($t8)
    li $t7, 101
    sb $t7, 1($t8)
    li $t7, 121
    sb $t7, 2($t8)
    sb $zero, 3($t8)

    sw $t8, 4($sp)


# ------> sp[index] = value;
    li $t0, 2
    sw $t0, 8($sp)
    lw $s1, 8($sp)
    lw $s2, 8($sp)
    add $t1, $s1, $s2

# ------> sp[index] = REGISTRO[index];
    sw $t1, 8($sp)

# ------> sp[index] = value;

# ---> RESERVAR 8 BYTES EN EL HEAP
    li $t8, 8
    move $a0, $t8
    li $v0, 9
    syscall
    move $t8, $v0

# ---> ALMACENAR CADENA EN HEAP (EN EL ESPACIO RESERVADO)
    li $t7, 80
    sb $t7, 0($t8)
    li $t7, 117
    sb $t7, 1($t8)
    li $t7, 108
    sb $t7, 2($t8)
    li $t7, 105
    sb $t7, 3($t8)
    li $t7, 100
    sb $t7, 4($t8)
    li $t7, 111
    sb $t7, 5($t8)
    li $t7, 10
    sb $t7, 6($t8)
    sb $zero, 7($t8)

    sw $t8, 4($sp)

    lw $s2, 0($sp)
    move $s1, $s2

# ------> OUT_STRING
    lw $a0, 4($sp)
    jal out_string

    lw $s2, 0($sp)
    move $s1, $s2

# ------> LLAMAR A LA FUNCIÓN print_name
    move $a0, $s1
    lw $t8, 4($s1)
    move $a1, $t8
    jal Main.print_name
    move $t0, $v0

    lw $s2, 0($sp)
    move $s1, $s2

# ------> OUT_STRING
    lw $s1, 0($sp)
    lw $a0, 8($s1)
    jal out_string

    lw $s2, 0($sp)
    move $s1, $s2

# ------> OUT_STRING
    la $a0, str0
    jal out_string


# ------> RETURN REGISTRO[index];
    move $v0, $t0

# ------> FIN DE LA FUNCIÓN Main.main
    move $sp, $fp
    lw $fp, 0($sp)
    lw $ra, 4($sp)
    addi $sp, $sp, 8

# ------> TERMINAR MEMORIA DE LA CLASE Main

    lw $t0, 0($sp)
    addi $sp, $sp, 4


# ------> TERMINAR PROGRAMA
    li $v0, 10
    syscall