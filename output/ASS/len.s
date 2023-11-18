length:
    # $a0 = dirección del string en el heap

    move $t0, $a0     # Copia la dirección del string a $t0
    li $v0, 0         # Inicializa el contador de longitud a 0

loop:
    lb $t1, 0($t0)    # Carga el carácter actual en $t1
    beqz $t1, end     # Si el carácter es nulo, termina el loop
    addi $v0, $v0, 1  # Incrementa el contador de longitud
    addi $t0, $t0, 1  # Avanza al siguiente carácter
    j loop            # Repite el loop

end:
    # $v0 contiene ahora la longitud de la cadena
    jr $ra            # Retorna a la función llamadora
