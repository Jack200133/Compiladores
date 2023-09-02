from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):
    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        tokenError = offendingSymbol.text
        if "extraneous input" in msg:
            print(f"Error en la línea {line}, posición {column}: {tokenError}; Entrada no esperada.")
        elif "no viable alternative at input" in msg:
            print(f"Error en la línea {line}, posición {column}: {tokenError}; Entrada no reconocida.")
        elif "missing ';' at" in msg:
            print(f"Error en la línea {line}, posición {column}: Falta ';' en la entrada.")
        elif "mismatched input" in msg:
            print(f"Error en la línea {line}, posición {column}: Entrada no coincide con lo esperado.")
        else:
            print(f"Error de sintaxis en la línea {line}, posición {column}: {msg}")


    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        print("Error de ambigüedad entre tokens.")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        print("Error al intentar contexto completo.")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        print("Error de sensibilidad de contexto.")

