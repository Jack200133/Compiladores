.data
vt_Main:
	.word Main.print_name
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
	sw $t9, 36($sp)
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
	lw $t9, 36($sp)
	addi $sp, $sp, 36
	jr $ra

# ======== CODIGO ========
CLASS_Main:

# ======== RESERVA DE MEMORIA para CLASS_Main ========
	li $a0, 24
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
# ======== RESERVA DE 9 BYTES EN HEAP ========
	li $t8, 9
	move $a0, $t8
	li $v0, 9
	syscall
	move $t8, $v0
# ======== ALMACENAR CADENA EN HEAP ========
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

	sw $t8, 8($s7)
# ======== sp_GLOBAL[index] = value ========
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

	sw $t8, 12($s7)
# ======== sp_GLOBAL[index] = value ========
	li $t8, 3
	sw $t8, 16($s7)
	jal Main.main

Main.print_name:
	move $s1, $a0
# ======== INICIALIZAR DE MEMORIA FUNCION Main.print_name ========
	addi $sp, $sp, -8
	sw $fp, 0($sp)
	sw $ra, 4($sp)
	move $fp, $sp
	addi $sp, $sp, -8
	sw $s7, 0($sp)
	lw $s2, 0($sp)
	move $s1, $s2
# ======== PARAM = sp_GLOBAL[index] ========
	lw $s1, 0($sp)
	lw $a1, 8($s1)

# ======== CALL out_string ========
	move $a0, $a1
	jal out_string

	lw $s2, 0($sp)
	move $s1, $s2
# ======== RETURN t ========
	move $v0, $t0
# ======== FIN FUNCION Main.print_name ========
	move $sp, $fp
	lw $ra, 4($sp)
	lw $fp, 0($sp)
	addi $sp, $sp, 8
	jr $ra

Main.main:
	move $s1, $a0
# ======== INICIALIZAR DE MEMORIA FUNCION Main.main ========
	addi $sp, $sp, -8
	sw $fp, 0($sp)
	sw $ra, 4($sp)
	move $fp, $sp
	addi $sp, $sp, -8
	sw $s7, 0($sp)
	lw $s2, 0($sp)
	move $s1, $s2
# ======== CALL Main.print_name ========
	lw $s2, 4($s1)
	lw $t8, 0($s2)
	move $a0, $s1
	jal save_registers
	jal $t8
	jal restore_registers
	move $t0, $v0
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

