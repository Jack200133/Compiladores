grammar YAPL;

// Palabras reservadas
CLASS: 'class'|'CLASS';
ELSE: 'else'|'ELSE';
FALSE: 'false';
TRUE: 'true';
FI: 'fi'|'FI';
IF: 'if'|'IF';
IN: 'in'|'IN';
INHERITS: 'inherits'|'INHERITS';
ISVOID: 'isvoid'|'ISVOID';
LOOP: 'loop'|'LOOP';
POOL: 'pool'|'POOL';
THEN: 'then'|'THEN';
WHILE: 'while'|'WHILE';
NEW: 'new'|'NEW';
NOT: 'not'|'NOT';
AND: 'and'|'AND';
OR: 'or'|'OR';
LET: 'let'|'LET';

// Reglas lexicas
INT: [0-9]+; // Enteros
TYPE_ID: [A-Z][a-z0-9_]*; // Identificadores de tipos
ID: [a-z][a-zA-Z0-9_]*; // Identificadores
STRING: '"' (~["\r\n\\] | '\\' ["\\/bfnrt])* '"';

// Identificadores
SELF: 'self';
SELF_TYPE: 'SELF_TYPE';

// Caracteres especiales
PLUS: '+';
MINUS: '-';
MULT: '*';
DOBLE: ':';
DIV: '/';
EQ: '=';
LPAREN: '(';
RPAREN: ')';
LBRACE: '{';
RBRACE: '}';
SEMI: ';';
COMMA: ',';
LESS_THAN: '<'; // Menor que
GREATER_THAN: '>'; // Mayor que
AT: '@';
DOT: '.';
LEFT_ARROW: '<-';
TILDE: '~'; // Virgulilla

// WhiteSpace
WS: [ \t\r\n\f]+ -> channel(HIDDEN);

// Comentarios
COMMENT: '--' ~[\n]* '\n' -> skip;

// La regla ERROR captura cualquier caracter no reconocido y genera un token ERROR
ERROR: . ;


program: (classDef SEMI)+ EOF;
classDef : CLASS TYPE_ID (INHERITS TYPE_ID)? LBRACE (featureDef SEMI)* RBRACE ;
featureDef : ID LPAREN (formalDef (COMMA formalDef)*)? RPAREN DOBLE TYPE_ID LBRACE (expr)* (returnFunc)? RBRACE
           | ID DOBLE TYPE_ID (LEFT_ARROW expr)?
           ;
formalDef: ID DOBLE TYPE_ID ;
returnFunc: 'return' expr SEMI;

expr : expr (AT TYPE_ID)? DOT ID LPAREN (expr (COMMA expr)*)? RPAREN
    | ID LPAREN (expr (COMMA expr)*)? RPAREN
    | IF expr THEN expr ELSE expr FI
    | WHILE expr LOOP expr POOL
    | LBRACE (expr SEMI)+ RBRACE
    | LET ID DOBLE TYPE_ID (LEFT_ARROW expr)? (COMMA ID DOBLE TYPE_ID (LEFT_ARROW expr)?)* IN expr
    | NEW TYPE_ID
    | ISVOID expr
    | expr DIV expr
    | expr MULT expr
    | expr MINUS expr
    | expr PLUS expr
    | TILDE expr
    | expr LESS_THAN expr
    | expr LESS_THAN EQ expr
    | expr EQ expr
    | NOT expr
    | RPAREN expr LPAREN
    | ID
    | INT
    | STRING
    | TRUE
    | FALSE   
    | ID LEFT_ARROW expr
    ;