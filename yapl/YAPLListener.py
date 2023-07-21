# Generated from YAPL.g4 by ANTLR 4.13.0
from antlr4 import *
if "." in __name__:
    from .YAPLParser import YAPLParser
else:
    from YAPLParser import YAPLParser

# This class defines a complete listener for a parse tree produced by YAPLParser.
class YAPLListener(ParseTreeListener):

    # Enter a parse tree produced by YAPLParser#program.
    def enterProgram(self, ctx:YAPLParser.ProgramContext):
        pass

    # Exit a parse tree produced by YAPLParser#program.
    def exitProgram(self, ctx:YAPLParser.ProgramContext):
        pass


    # Enter a parse tree produced by YAPLParser#classDef.
    def enterClassDef(self, ctx:YAPLParser.ClassDefContext):
        pass

    # Exit a parse tree produced by YAPLParser#classDef.
    def exitClassDef(self, ctx:YAPLParser.ClassDefContext):
        pass


    # Enter a parse tree produced by YAPLParser#featureDef.
    def enterFeatureDef(self, ctx:YAPLParser.FeatureDefContext):
        pass

    # Exit a parse tree produced by YAPLParser#featureDef.
    def exitFeatureDef(self, ctx:YAPLParser.FeatureDefContext):
        pass


    # Enter a parse tree produced by YAPLParser#formalDef.
    def enterFormalDef(self, ctx:YAPLParser.FormalDefContext):
        pass

    # Exit a parse tree produced by YAPLParser#formalDef.
    def exitFormalDef(self, ctx:YAPLParser.FormalDefContext):
        pass


    # Enter a parse tree produced by YAPLParser#returnFunc.
    def enterReturnFunc(self, ctx:YAPLParser.ReturnFuncContext):
        pass

    # Exit a parse tree produced by YAPLParser#returnFunc.
    def exitReturnFunc(self, ctx:YAPLParser.ReturnFuncContext):
        pass


    # Enter a parse tree produced by YAPLParser#expr.
    def enterExpr(self, ctx:YAPLParser.ExprContext):
        pass

    # Exit a parse tree produced by YAPLParser#expr.
    def exitExpr(self, ctx:YAPLParser.ExprContext):
        pass



del YAPLParser