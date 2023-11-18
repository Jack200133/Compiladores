concat:
    # $a0 = dirección de self
    # $a1 = dirección de s

    # Calcula la longitud de self
    move $t0, $a0         # Copia la dirección de self a $t0
    li $t1, 0             # Contador de longitud para self
loop_self:
    lb $t2, 0($t0)        # Carga el byte en $t2
    beqz $t2, end_self    # Si es cero, fin de la cadena
    addi $t0, $t0, 1      # Incrementa la dirección
    addi $t1, $t1, 1      # Incrementa el contador de longitud
    j loop_self
end_self:

    # Calcula la longitud de s
    move $t0, $a1         # Copia la dirección de s a $t0
    li $t3, 0             # Contador de longitud para s
loop_s:
    lb $t2, 0($t0)
    beqz $t2, end_s
    addi $t0, $t0, 1
    addi $t3, $t3, 1
    j loop_s
end_s:

    # Reserva espacio en el heap
    add $a0, $t1, $t3     # Suma las longitudes
    addi $a0, $a0, 1      # Agrega uno para el carácter nulo al final
    li $v0, 9             # syscall para reservar memoria
    syscall
    move $t4, $v0         # Dirección del nuevo espacio en $t4

    # Copia self al nuevo espacio
    move $t0, $a0         # Dirección de self
    move $t5, $t4         # Dirección de inicio del nuevo espacio
copy_self:
    lb $t2, 0($t0)
    beqz $t2, end_copy_self
    sb $t2, 0($t5)
    addi $t0, $t0, 1
    addi $t5, $t5, 1
    j copy_self
end_copy_self:

    # Copia s al final de self en el nuevo espacio
    move $t0, $a1
copy_s:
    lb $t2, 0($t0)
    beqz $t2, end_copy_s
    sb $t2, 0($t5)
    addi $t0, $t0, 1
    addi $t5, $t5, 1
    j copy_s
end_copy_s:

    sb $zero, 0($t5)      # Agrega el carácter nulo al final

    # Retorna la dirección de la nueva cadena
    move $v0, $t4
    jr $ra
