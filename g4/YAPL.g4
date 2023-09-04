grammar YAPL;

// ----------------- Tokens -----------------

// Palabras reservadas
CLASS       : [Cc][Ll][Aa][Ss][Ss] ;
ELSE        : [Ee][Ll][Ss][Ee] ;
FI          : [Ff][Ii] ;
IF          : [Ii][Ff] ;
IN          : [Ii][Nn] ;
LET         : [Ll][Ee][Tt] ;
INHERITS    : [Ii][Nn][Hh][Ee][Rr][Ii][Tt][Ss] ;
ISVOID      : [Ii][Ss][Vv][Oo][Ii][Dd] ;
LOOP        : [Ll][Oo][Oo][Pp] ;
POOL        : [Pp][Oo][Oo][Ll] ;
THEN        : [Tt][Hh][Ee][Nn] ;
WHILE       : [Ww][Hh][Ii][Ll][Ee] ;
NEW         : [Nn][Ee][Ww] ;
NOT         : [Nn][Oo][Tt] ;
TRUE        : 'true' ;
FALSE       : 'false' ;

// Identificadores
TYPE_ID     : [A-Z][A-Za-z0-9_]* | SELF_TYPE;
OBJECT_ID   : [a-z][A-Za-z0-9_]* | SELF;
SELF        : 'self';
SELF_TYPE   : 'SELF_TYPE';

// Caracteres especiales
LPAREN  : '(' ;
RPAREN  : ')' ;
LBRACE  : '{' ;
RBRACE  : '}' ;
LBRACKET : '[' ;
RBRACKET : ']' ;

COLON   : ':' ;
SEMICOLON : ';' ;
COMMA   : ',' ;

DOT     : '.' ;
NEG     : '~' ;
AT      : '@' ;

MULT    : '*' ;
DIV     : '/' ;
PLUS    : '+' ;
MINUS   : '-' ;

LE      : '<=' ;
LT      : '<' ;
EQ      : '=' ;

INCR    : '++' ;
DECR    : '--' ;
ASSIGN_MULT : '=*' ;
ASSIGN_DIV  : '=/' ;
ASSIGN_PLUS : '=+' ;
ASSIGN_MINUS : '=-' ;
ASSIGN  : '<-' ;

// Cadenas
STRING: '"' ( ESC_SEQ | ~["\\\r\n] )* '"';
fragment ESC_SEQ: '\\' [btnfr"'\\];

// Enteros
INT     : [0-9]+ ;

// Whitespaces
WHITESPACE  : [\u0020\u0009\u000A\u000C\u000D\u000B]+ -> skip ;

// Comentarios
COMMENT     : '--' .*? [\n\f\r] -> skip;
COMMENT_BLOCK: '(' .? '*)' -> skip;

// Token de error
ERROR : . ;

// ----------------- Gramatica -----------------

program: (classDef SEMICOLON)+ EOF;

classDef: CLASS TYPE_ID (INHERITS TYPE_ID)? LBRACE (featureDef SEMICOLON | ERROR )* RBRACE ;

featureDef : OBJECT_ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN COLON TYPE_ID LBRACE expr RBRACE 
        | OBJECT_ID COLON TYPE_ID (ASSIGN expr)?
        | ERROR ;

formalDef: OBJECT_ID COLON TYPE_ID;

expr    : expr  (AT TYPE_ID)? DOT OBJECT_ID LPAREN  (expr (COMMA expr)*)? RPAREN
        | OBJECT_ID LPAREN (expr (COMMA expr)*)? RPAREN
        | IF expr THEN expr ELSE expr FI
        | WHILE expr LOOP expr POOL
        | LBRACE (expr SEMICOLON)+ RBRACE
        | LET OBJECT_ID COLON TYPE_ID (ASSIGN expr)? (COMMA OBJECT_ID COLON TYPE_ID (ASSIGN expr)?)* IN expr
        | NEW TYPE_ID 

        | NEG expr
        | ISVOID expr
        | expr MULT expr
        | expr DIV expr
        | expr PLUS expr
        | expr MINUS expr
        | expr LE expr
        | expr LT expr
        | expr EQ expr
        | NOT expr

        | OBJECT_ID ASSIGN expr
        
        | LPAREN expr RPAREN

        | OBJECT_ID
        | INT
        | STRING
        | TRUE
        | FALSE 
        | ERROR
        ;