.data
vt_Factorial:
	.word Factorial.factorial
vt_Fibonacci:
	.word Fibonacci.fibonacci
vt_Main:
	.word Main.main

.text

main:
	jal CLASS_Main
# ======== FUNCIONES BASICAS ========
out_int:
	li $v0, 1
	syscall
	jr $ra

out_string:
	li $v0, 4
	syscall
	jr $ra

in_int:
	li $v0, 5
	syscall
	jr $ra

in_string:
	li $v0, 8
	syscall
	jr $ra


save_registers:
    addi $sp, $sp, -36
    sw $t0, 0($sp)
    sw $t1, 4($sp)
    sw $t2, 8($sp)
    sw $t3, 12($sp)
    sw $t4, 16($sp)
    sw $t5, 20($sp)
    sw $t6, 24($sp)
    sw $t7, 28($sp)
    sw $t8, 32($sp)
    jr $ra


restore_registers:
    lw $t0, 0($sp)
    lw $t1, 4($sp)
    lw $t2, 8($sp)
    lw $t3, 12($sp)
    lw $t4, 16($sp)
    lw $t5, 20($sp)
    lw $t6, 24($sp)
    lw $t7, 28($sp)
    lw $t8, 32($sp)
    addi $sp, $sp, 36
    jr $ra



# ======== CREAR CLASE IO ========
CLASS_IO:

# ======== RESERVAR ESPACIO EN EL HEAP PARA LA CLASE Object ========
    li $a0, 8
    li $v0, 9
    syscall
    move $t8, $v0

# ======== RESERVAR 3 BYTES EN EL HEAP ========
    li $t7, 3
    move $a0, $t7
    li $v0, 9
    syscall
    move $t7, $v0

# ======== ALMACENAR CADENA EN HEAP ========
    li $t6, 73
    sb $t6, 0($t7)
    li $t6, 79
    sb $t6, 1($t7)
    sb $zero, 2($t7)

    sw $t7, 0($t8)
    move $s6, $s7
    move $s7, $t8
    jr $ra

# ======== CODIGO ========
CLASS_Factorial:

# ======== RESERVA DE MEMORIA para CLASS_Factorial ========
	li $a0, 12
	li $v0, 9
	syscall
	move $t8, $v0
# ======== RESERVA DE 10 BYTES EN HEAP ========
	li $t7, 10
	move $a0, $t7
	li $v0, 9
	syscall
	move $t7, $v0
# ======== ALMACENAR CADENA EN HEAP ========
	li $t6, 70
	sb $t6, 0($t7)
	li $t6, 97
	sb $t6, 1($t7)
	li $t6, 99
	sb $t6, 2($t7)
	li $t6, 116
	sb $t6, 3($t7)
	li $t6, 111
	sb $t6, 4($t7)
	li $t6, 114
	sb $t6, 5($t7)
	li $t6, 105
	sb $t6, 6($t7)
	li $t6, 97
	sb $t6, 7($t7)
	li $t6, 108
	sb $t6, 8($t7)
	sb $zero, 9($t7)

	sw $t7, 0($t8)
	la $t0 vt_Factorial
	sw $t0, 4($t8)
	move $s7, $t8
# ======== sp_GLOBAL[index] = value ========
	li $t8, 0
	sw $t8, 8($s7)

	jr $ra


Factorial.factorial:
	move $s1, $a0
# ======== INICIALIZAR DE MEMORIA FUNCION Factorial.factorial ========
	addi $sp, $sp, -8
	sw $fp, 0($sp)
	sw $ra, 4($sp)
	move $fp, $sp
	addi $sp, $sp, -16
	sw $s1, 0($sp)
# ======== sp[index] = PARAM_X ========
	sw $a1, 4($sp)

	lw $s1, 4($sp)
	li $s2, 0
	beq $s1, $s2, set_true0
	li $t0, 0
	j continue_labnel0
set_true0:
	li $t0, 1
continue_labnel0:
# ======== IF temp ========
	bne $t0, $zero, label_l0

# ======== GOTO ========
	j label_l1

# ======== LABEL ========
label_l0:

# ======== sp[index] = value ========
	li $t8, 1
	sw $t8, 8($sp)
# ======== temp = sp[index] ========
	lw $t0, 8($sp)
# ======== GOTO ========
	j label_l2

# ======== LABEL ========
label_l1:

	lw $s1, 4($sp)
	li $s2, 1
	beq $s1, $s2, set_true1
	li $t1, 0
	j continue_labnel1
set_true1:
	li $t1, 1
continue_labnel1:
# ======== IF temp ========
	bne $t1, $zero, label_l3

# ======== GOTO ========
	j label_l4

# ======== LABEL ========
label_l3:

# ======== sp[index] = value ========
	li $t8, 1
	sw $t8, 8($sp)
# ======== temp = sp[index] ========
	lw $t1, 8($sp)
# ======== GOTO ========
	j label_l5

# ======== LABEL ========
label_l4:

	lw $s1, 4($sp)
	li $s2, 1
	sub $t2, $s1, $s2
# ======== PARAM = temp ========
	move $a1, $t2
# ======== CALL Factorial.factorial ========
	lw $s1, 0($sp)
	lw $s2, 4($s1)
	lw $t8, 0($s2)
	move $a0, $s1
	jal save_registers
	jalr $t8
	jal restore_registers
	move $t3, $v0
	lw $s1, 4($sp)
	mult $s1, $t3
	mflo $t2
# ======== sp[index] = temp# ========
	sw $t2, 8($sp)
# ======== temp = sp[index] ========
	lw $t1, 8($sp)
# ======== LABEL ========
label_l5:

# ======== temp = temp ========
	move $t0, $t1
# ======== LABEL ========
label_l2:

# ======== RETURN sp[index] ========
	lw $v0, 8($sp)
# ======== FIN FUNCION Factorial.factorial ========
	move $sp, $fp
	lw $ra, 4($sp)
	lw $fp, 0($sp)
	addi $sp, $sp, 8
	jr $ra

CLASS_Fibonacci:

# ======== RESERVA DE MEMORIA para CLASS_Fibonacci ========
	li $a0, 12
	li $v0, 9
	syscall
	move $t8, $v0
# ======== RESERVA DE 10 BYTES EN HEAP ========
	li $t7, 10
	move $a0, $t7
	li $v0, 9
	syscall
	move $t7, $v0
# ======== ALMACENAR CADENA EN HEAP ========
	li $t6, 70
	sb $t6, 0($t7)
	li $t6, 105
	sb $t6, 1($t7)
	li $t6, 98
	sb $t6, 2($t7)
	li $t6, 111
	sb $t6, 3($t7)
	li $t6, 110
	sb $t6, 4($t7)
	li $t6, 97
	sb $t6, 5($t7)
	li $t6, 99
	sb $t6, 6($t7)
	li $t6, 99
	sb $t6, 7($t7)
	li $t6, 105
	sb $t6, 8($t7)
	sb $zero, 9($t7)

	sw $t7, 0($t8)
	la $t0 vt_Fibonacci
	sw $t0, 4($t8)
	move $s7, $t8
# ======== sp_GLOBAL[index] = value ========
	li $t8, 0
	sw $t8, 8($s7)

	jr $ra


Fibonacci.fibonacci:
	move $s1, $a0
# ======== INICIALIZAR DE MEMORIA FUNCION Fibonacci.fibonacci ========
	addi $sp, $sp, -8
	sw $fp, 0($sp)
	sw $ra, 4($sp)
	move $fp, $sp
	addi $sp, $sp, -20
	sw $s1, 0($sp)
# ======== sp[index] = PARAM_X ========
	sw $a1, 4($sp)

	lw $s1, 4($sp)
	li $s2, 0
	beq $s1, $s2, set_true2
	li $t0, 0
	j continue_labnel2
set_true2:
	li $t0, 1
continue_labnel2:
# ======== IF temp ========
	bne $t0, $zero, label_l6

# ======== GOTO ========
	j label_l7

# ======== LABEL ========
label_l6:

# ======== sp[index] = value ========
	li $t8, 0
	sw $t8, 8($sp)
# ======== temp = sp[index] ========
	lw $t0, 8($sp)
# ======== GOTO ========
	j label_l8

# ======== LABEL ========
label_l7:

	lw $s1, 4($sp)
	li $s2, 1
	beq $s1, $s2, set_true3
	li $t1, 0
	j continue_labnel3
set_true3:
	li $t1, 1
continue_labnel3:
# ======== IF temp ========
	bne $t1, $zero, label_l9

# ======== GOTO ========
	j label_l10

# ======== LABEL ========
label_l9:

# ======== sp[index] = value ========
	li $t8, 1
	sw $t8, 8($sp)
# ======== temp = sp[index] ========
	lw $t1, 8($sp)
# ======== GOTO ========
	j label_l11

# ======== LABEL ========
label_l10:

	lw $s1, 4($sp)
	li $s2, 1
	sub $t2, $s1, $s2
# ======== PARAM = temp ========
	move $a1, $t2
# ======== CALL Fibonacci.fibonacci ========
	lw $s1, 0($sp)
	lw $s2, 4($s1)
	lw $t8, 0($s2)
	move $a0, $s1
	jal save_registers
	jalr $t8
	jal restore_registers
	move $t3, $v0
	lw $s1, 4($sp)
	li $s2, 2
	sub $t2, $s1, $s2
# ======== PARAM = temp ========
	move $a1, $t2
# ======== CALL Fibonacci.fibonacci ========
	lw $s1, 0($sp)
	lw $s2, 4($s1)
	lw $t8, 0($s2)
	move $a0, $s1
	jal save_registers
	jalr $t8
	jal restore_registers
	move $t4, $v0
	add $t2, $t3, $t4
# ======== sp[index] = temp# ========
	sw $t2, 8($sp)
# ======== temp = sp[index] ========
	lw $t1, 8($sp)
# ======== LABEL ========
label_l11:

# ======== temp = temp ========
	move $t0, $t1
# ======== LABEL ========
label_l8:

# ======== RETURN sp[index] ========
	lw $v0, 8($sp)
# ======== FIN FUNCION Fibonacci.fibonacci ========
	move $sp, $fp
	lw $ra, 4($sp)
	lw $fp, 0($sp)
	addi $sp, $sp, 8
	jr $ra

CLASS_Main:

# ======== RESERVA DE MEMORIA para CLASS_Main ========
	li $a0, 40
	li $v0, 9
	syscall
	move $t8, $v0
# ======== RESERVA DE 5 BYTES EN HEAP ========
	li $t7, 5
	move $a0, $t7
	li $v0, 9
	syscall
	move $t7, $v0
# ======== ALMACENAR CADENA EN HEAP ========
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
	la $t0 vt_Main
	sw $t0, 4($t8)
	move $s7, $t8
# ======== sp_GLOBAL[index] = value ========
	li $t8, 10
	sw $t8, 8($s7)
	jal Main.main

Main.main:
# ======== INICIALIZAR DE MEMORIA FUNCION Main.main ========
	addi $sp, $sp, -8
	sw $fp, 0($sp)
	sw $ra, 4($sp)
	move $fp, $sp
	addi $sp, $sp, -8
	sw $s7, 0($sp)
	lw $s1, 0($sp)
	move $s1, $s2
# ======== CREAR NUEVO OBJETO Factorial========
	jal CLASS_Factorial
	lw $s2, 0($sp)
	sw $s7, 12($s2)
	move $s7, $s6
# ======== CREAR NUEVO OBJETO Fibonacci========
	jal CLASS_Fibonacci
	lw $s2, 0($sp)
	sw $s7, 24($s2)
	move $s7, $s6
# ======== CREAR NUEVO OBJETO IO========
	jal CLASS_IO
	lw $s2, 0($sp)
	sw $s7, 36($s2)
	move $s7, $s6
# ======== PARAM = sp_GLOBAL[index] ========
	lw $s1, 0($sp)
	lw $a1, 8($s1)

# ======== CALL sp_GLOBAL[4].factorial ========
	lw $s1, 0($sp)
	lw $s2, 4($s1)
# ======== CALL sp_GLOBAL[index] ========
	lw $s2, 0($sp)
	lw $s1, 12($s2)
	lw $s2, 4($s1)
	lw $t8, 0($s2)
	move $a0, $s1
	jal save_registers
	jalr $t8
	jal restore_registers
	move $t0, $v0
# ======== PARAM = temp ========
	move $a1, $t0
# ======== sp_GLOBAL[index] ========
	lw $s2, 0($sp)
	lw $s1, 36($s2)
# ======== CALL out_int ========
	move $a0, $a1
	jal out_int

	lw $s2, 0($sp)
	move $s1, $s2
# ======== RESERVA DE 2 BYTES EN HEAP ========
	li $t8, 2
	move $a0, $t8
	li $v0, 9
	syscall
	move $t8, $v0
# ======== ALMACENAR CADENA EN HEAP ========
	li $t7, 10
	sb $t7, 0($t8)
	sb $zero, 1($t8)

	move $a1, $t8
# ======== sp_GLOBAL[index] ========
	lw $s2, 0($sp)
	lw $s1, 36($s2)
# ======== CALL out_string ========
	move $a0, $a1
	jal out_string

	lw $s2, 0($sp)
	move $s1, $s2
# ======== PARAM = sp_GLOBAL[index] ========
	lw $s1, 0($sp)
	lw $a1, 8($s1)

# ======== CALL sp_GLOBAL[16].fibonacci ========
	lw $s1, 0($sp)
	lw $s2, 4($s1)
# ======== CALL sp_GLOBAL[index] ========
	lw $s2, 0($sp)
	lw $s1, 24($s2)
	lw $s2, 4($s1)
	lw $t8, 0($s2)
	move $a0, $s1
	jal save_registers
	jalr $t8
	jal restore_registers
	move $t0, $v0
# ======== PARAM = temp ========
	move $a1, $t0
# ======== sp_GLOBAL[index] ========
	lw $s2, 0($sp)
	lw $s1, 36($s2)
# ======== CALL out_int ========
	move $a0, $a1
	jal out_int

	lw $s2, 0($sp)
	move $s1, $s2
# ======== RETURN t ========
	move $v0, $t0
# ======== FIN FUNCION Main.main ========
	move $sp, $fp
	lw $ra, 4($sp)
	lw $fp, 0($sp)
	addi $sp, $sp, 8

# ======== Salida del Programa ========
	li $v0, 10
	syscall

