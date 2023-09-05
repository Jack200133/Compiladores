from antlr4.error.ErrorListener import ErrorListener

class MyErrorListener(ErrorListener):

    def __init__(self):
        self.ErrorList = []

    def add_error(self, error_mesagge, line, column, full_error):
        # Verificar si el error no existe ya en la misma linea
        for err in self.ErrorList:
            if err["line"] == line and err["error_mesagge"] == error_mesagge:
                return
        self.ErrorList.append({"error_mesagge": error_mesagge,
                              "line": line, "column": column, "full_error": full_error})

    def syntaxError(self, recognizer, offendingSymbol, line, column, msg, e):
        tokenError = offendingSymbol.text
        expected_symbols = recognizer.getExpectedTokens().toString(recognizer.literalNames, recognizer.symbolicNames)
        if "extraneous input" in msg:
            sms = f"Error Sintaxis (Línea {line}, posición {column}): {tokenError}; Entrada esperdada: {expected_symbols}."
            self.add_error("",line,column,sms)
           # print(f"Error en la línea {line}, posición {column}: {tokenError}; Entrada no esperada.")
        elif "no viable alternative at input" in msg:
            sms = f"Error Sintaxis (Línea {line}, posición {column}): {tokenError}; Entrada no reconocida. Entrada esperdada: {expected_symbols}"
            self.add_error("",line,column,sms)
           # print(f"Error en la línea {line}, posición {column}: {tokenError}; Entrada no reconocida.")
        elif "missing ';' at" in msg:
            sms = f"Error Sintaxis (Línea {line}, posición {column}): Falta ';' en la entrada."
            self.add_error("",line,column,sms)
           # print(f"Error en la línea {line}, posición {column}: Falta ';' en la entrada.")
        elif "mismatched input" in msg:
            sms = f"Error Sintaxis (Línea {line}, posición {column}): Entrada no coincide con lo esperado: {expected_symbols}."
            self.add_error("",line,column,sms)
           # print(f"Error en la línea {line}, posición {column}: Entrada no coincide con lo esperado. Entrada esperdada: {expected_symbols}.")
        else:
            sms = f"Error Sintaxis (Línea {line}, posición {column}): {msg}"
            self.add_error("",line,column,sms)
           # print(f"Error de sintaxis en la línea {line}, posición {column}: {msg}")


    def reportAmbiguity(self, recognizer, dfa, startIndex, stopIndex, exact, ambigAlts, configs):
        print("Error de ambigüedad entre tokens.")

    def reportAttemptingFullContext(self, recognizer, dfa, startIndex, stopIndex, conflictingAlts, configs):
        print("Error al intentar contexto completo.")

    def reportContextSensitivity(self, recognizer, dfa, startIndex, stopIndex, prediction, configs):
        print("Error de sensibilidad de contexto.")

