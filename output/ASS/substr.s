substr:
    # $a0 = dirección de self
    # $a1 = posición inicial (i)
    # $a2 = longitud de la subcadena (l)

    # Calcula la longitud de self para validar
    move $t0, $a0         # Copia la dirección de self a $t0
    li $t1, 0             # Contador de longitud
loop_length:
    lb $t2, 0($t0)        # Carga el byte en $t2
    beqz $t2, end_length  # Si es cero, fin de la cadena
    addi $t0, $t0, 1      # Incrementa la dirección
    addi $t1, $t1, 1      # Incrementa el contador de longitud
    j loop_length
end_length:

    # Verifica si los parámetros son válidos
    bge $a1, $t1, error   # Si i >= longitud de self, error
    add $t3, $a1, $a2
    bge $t3, $t1, error   # Si i + l > longitud de self, error

    # Reserva espacio en el heap para la subcadena
    addi $a0, $a2, 1      # l + 1 para el carácter nulo
    li $v0, 9             # syscall para reservar memoria
    syscall
    move $t4, $v0         # Dirección del nuevo espacio en $t4

    # Copia la subcadena al nuevo espacio
    add $t0, $a0, $a1     # Dirección de inicio de la subcadena en self
    move $t5, $t4         # Dirección de inicio del nuevo espacio
copy_substring:
    lb $t2, 0($t0)
    beqz $t2, end_copy    # Termina si encuentra carácter nulo
    sb $t2, 0($t5)
    addi $t0, $t0, 1
    addi $t5, $t5, 1
    addi $a2, $a2, -1
    beqz $a2, end_copy    # Termina si hemos copiado l caracteres
    j copy_substring
end_copy:
    sb $zero, 0($t5)      # Agrega el carácter nulo al final

    # Retorna la dirección de la nueva subcadena
    move $v0, $t4
    jr $ra

error:
    # Manejar error, posiblemente devolviendo una cadena vacía o nula
    jr $ra
