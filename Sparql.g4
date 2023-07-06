/*
 * Copyright 2007 the original author or authors.
 *
 * All rights reserved.
 *
 * Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following
 * conditions are met:
 *
 * Redistributions of source code must retain the above copyright notice, this list of conditions and the following
 * disclaimer.
 *
 * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following
 * disclaimer in the documentation and/or other materials provided with the distribution.
 *
 * Neither the name of the author or authors nor the names of its contributors may be used to endorse or promote
 * products derived from this software without specific prior written permission.
 *
 * THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
 * "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
 * LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
 * A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT OWNER OR
 * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
 * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
 * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
 * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
 * LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
 * NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
 * SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
 *
 * @author Simone Tripodi   (simone)
 * @author Michele Mostarda (michele)
 * @version $Id: Sparql.g 5 2007-10-30 17:20:36Z simone $
 */
 /*
 * Ported to Antlr4 by Tom Everett
 */

grammar Sparql;

query
    : prologue ( selectQuery | constructQuery | describeQuery | askQuery ) EOF
    ;

prologue
    : baseDecl? prefixDecl*
    ;

baseDecl
    : K_BASE IRI_REF
    ;

prefixDecl
    : K_PREFIX PNAME_NS IRI_REF
    ;

selectQuery
    : K_SELECT ( K_DISTINCT | K_REDUCED )? ( var_+ | '*' ) datasetClause* whereClause solutionModifier
    ;

constructQuery
    : K_CONSTRUCT constructTemplate datasetClause* whereClause solutionModifier
    ;

describeQuery
    : K_DESCRIBE ( varOrIRIref+ | '*' ) datasetClause* whereClause? solutionModifier
    ;

askQuery
    : K_ASK datasetClause* whereClause
    ;

datasetClause
    : K_FROM ( defaultGraphClause | namedGraphClause )
    ;

defaultGraphClause
    : sourceSelector
    ;

namedGraphClause
    : K_NAMED sourceSelector
    ;

sourceSelector
    : iriRef
    ;

whereClause
    : K_WHERE? groupGraphPattern
    ;

solutionModifier
    : orderClause? limitOffsetClauses?
    ;

limitOffsetClauses
    : ( limitClause offsetClause? | offsetClause limitClause? )
    ;

orderClause
    : K_ORDER K_BY orderCondition+
    ;

orderCondition
    : ( ( K_ASC | K_DESC ) brackettedExpression )
    | ( constraint | var_ )
    ;

limitClause
    : K_LIMIT INTEGER
    ;

offsetClause
    : K_OFFSET INTEGER
    ;

groupGraphPattern
    : '{' triplesBlockMy? (( graphPatternNotTriplesMy | filter_My ) '.'? triplesBlockMy? )* '}'
    ;

triplesBlockMy
    : compiler_set? triplesBlock compiler_set?
    ;

triplesBlock
    : triplesSameSubjectMy ( '.' triplesBlock? )?
    ;

graphPatternNotTriplesMy
    : compiler_set? graphPatternNotTriples compiler_set?
    ;

graphPatternNotTriples
    : optionalGraphPattern
    | groupOrUnionGraphPattern
    | graphGraphPattern
    ;

optionalGraphPattern
    : K_OPTIONAL groupGraphPattern
    ;

graphGraphPattern
    : K_GRAPH varOrIRIref groupGraphPattern
    ;

groupOrUnionGraphPattern
    : groupGraphPattern ( K_UNION groupGraphPattern )*
    ;

filter_My
    : compiler_set? filter_ compiler_set?
    ;

filter_
    : K_FILTER constraint
    ;

constraint
    : brackettedExpression
    | builtInCall
    | functionCall
    ;

functionCall
    : iriRef argList
    ;

argList
    : ( NIL | '(' expression ( ',' expression )* ')' )
    ;

constructTemplate
    : '{' constructTriples? '}'
    ;

constructTriples
    : triplesSameSubjectMy ( '.' constructTriples? )?
    ;


triplesSameSubjectMy
    : compiler_set? triplesSameSubject compiler_set?
    ;

triplesSameSubject
    : varOrTerm propertyListNotEmpty
    | triplesNode propertyList
    ;

propertyListNotEmpty
    : verb objectList ( ';' ( verb objectList )? )*
    ;

propertyList
    : propertyListNotEmpty?
    ;

objectList
    : object_ ( ',' object_ )*
    ;

object_
    : graphNode
    ;

verb
    : varOrIRIref
    | 'a'
    ;

triplesNode
    : collection
    | blankNodePropertyList
    ;

blankNodePropertyList
    : '[' propertyListNotEmpty ']'
    ;

collection
    : '(' graphNode+ ')'
    ;

graphNode
    : varOrTerm
    | triplesNode
    ;

varOrTerm
    : var_
    | graphTerm
    ;

varOrIRIref
    : var_
    | iriRef
    ;

var_
    : VAR1
    | VAR2
    ;

graphTerm
    : iriRef
    | rdfLiteral
    | numericLiteral
    | booleanLiteral
    | blankNode
    | NIL
    ;

expression
    : conditionalOrExpression
    ;

conditionalOrExpression
    : conditionalAndExpression ( '||' conditionalAndExpression )*
    ;

conditionalAndExpression
    : valueLogical ( '&&' valueLogical )*
    ;

valueLogical
    : relationalExpression
    ;

relationalExpression
    : numericExpression ( ('=' | '!=' | '<' | '>' | '<=' | '>=') numericExpression )?
    | numericExpression K_IN '(' expression (',' expression)*  ')'
    ;

numericExpression
    : additiveExpression
    ;

additiveExpression
    : multiplicativeExpression ( '+' multiplicativeExpression | '-' multiplicativeExpression | numericLiteralPositive | numericLiteralNegative )*
    ;

multiplicativeExpression
    : unaryExpression ( '*' unaryExpression | '/' unaryExpression )*
    ;

unaryExpression
    : '!' primaryExpression
    | '+' primaryExpression
    | '-' primaryExpression
    | primaryExpression
    ;

primaryExpression
    : brackettedExpression
    | builtInCall
    | iriRefOrFunction
    | rdfLiteral
    | numericLiteral
    | booleanLiteral
    | var_
    ;

brackettedExpression
    : '(' expression ')'
    ;

builtInCall
    : K_STR '(' expression ')'
    | K_LANG '(' expression ')'
    | K_LANGMATCHES '(' expression ',' expression ')'
    | K_DATATYPE '(' expression ')'
    | K_BOUND '(' var_ ')'
    | K_SAMETERM '(' expression ',' expression ')'
    | K_ISIRI '(' expression ')'
    | K_ISURI '(' expression ')'
    | K_ISBLANK '(' expression ')'
    | K_ISLITERAL '(' expression ')'
    | regexExpression
    ;

regexExpression
    : K_REGEX '(' expression ',' expression ( ',' expression )? ')'
    ;

iriRefOrFunction
    : iriRef argList?
    ;

rdfLiteral
    : string_ ( LANGTAG | ( '^^' iriRef ) )?
    ;

numericLiteral
    : numericLiteralUnsigned
    | numericLiteralPositive
    | numericLiteralNegative
    ;

numericLiteralUnsigned
    : INTEGER
    | DECIMAL
    | DOUBLE
    ;

numericLiteralPositive
    : INTEGER_POSITIVE
    | DECIMAL_POSITIVE
    | DOUBLE_POSITIVE
    ;

numericLiteralNegative
    : INTEGER_NEGATIVE
    | DECIMAL_NEGATIVE
    | DOUBLE_NEGATIVE
    ;

booleanLiteral
    : K_TRUE
    | K_FALSE
    ;

string_
    : STRING_LITERAL1
    | STRING_LITERAL2
    /* | STRING_LITERAL_LONG('0'..'9') | STRING_LITERAL_LONG('0'..'9')*/
    ;

iriRef
    : IRI_REF
    | prefixedName
    ;

prefixedName
    : PNAME_LN
    | PNAME_NS
    ;

blankNode
    : BLANK_NODE_LABEL
    | ANON
    ;

compiler_set
    : COM_SET compiler_set_instruction
    ;

compiler_set_instruction
    : COM_SET_INSTR
    | COM_SET_AMOUNT_VALUES INTEGER
    ;

// LEXER RULES
K_BASE : B A S E;
K_PREFIX : P R E F I X;
K_SELECT : S E L E C T;
K_DISTINCT : D I S T I N C T;
K_REDUCED : R E D U C E D;
K_CONSTRUCT : C O N S T R U C T;
K_DESCRIBE : D E S C R I B E;
K_ASK : A S K;
K_FROM : F R O M;
K_NAMED : N A M E D;
K_WHERE : W H E R E;
K_ORDER : O R D E R;
K_BY : B Y;
K_ASC : A S C;
K_DESC : D E S C;
K_LIMIT : L I M I T;
K_OFFSET : O F F S E T;
K_OPTIONAL : O P T I O N A L;
K_GRAPH : G R A P H;
K_UNION : U N I O N;
K_FILTER : F I L T E R;
K_IN : I N;
K_STR : S T R;
K_LANG : L A N G;
K_LANGMATCHES : L A N G M A T C H E S;
K_DATATYPE : D A T A T Y P E;
K_BOUND : B O U N D;
K_SAMETERM : S A M E T E R M;
K_ISIRI : I S I R I;
K_ISURI : I S U R I;
K_ISBLANK : I S B L A N K;
K_ISLITERAL : I S L I T E R A L;
K_REGEX : R E G E X;
K_TRUE : T R U E;
K_FALSE : F A L S E;




fragment A : [aA];
fragment B : [bB];
fragment C : [cC];
fragment D : [dD];
fragment E : [eE];
fragment F : [fF];
fragment G : [gG];
fragment H : [hH];
fragment I : [iI];
fragment J : [jJ];
fragment K : [kK];
fragment L : [lL];
fragment M : [mM];
fragment N : [nN];
fragment O : [oO];
fragment P : [pP];
fragment Q : [qQ];
fragment R : [rR];
fragment S : [sS];
fragment T : [tT];
fragment U : [uU];
fragment V : [vV];
fragment W : [wW];
fragment X : [xX];
fragment Y : [yY];
fragment Z : [zZ];

COM_SET_INSTR
    : 'update_new'
    | 'update_end'
    ;

COM_SET_AMOUNT_VALUES
    : 'update_amount_values'
    ;

IRI_REF
    : '<' ( ~('<' | '>' | '"' | '{' | '}' | '|' | '^' | '\\' | '`' | ' ' | '\n') | (PN_CHARS))* '>'
    ;

PNAME_NS
    : PN_PREFIX? ':'
    ;

PNAME_LN
    : PNAME_NS PN_LOCAL
    ;

BLANK_NODE_LABEL
    : '_:' PN_LOCAL
    ;

VAR1
    : '?' VARNAME
    ;

VAR2
    : '$' VARNAME
    ;

LANGTAG
    : '@' PN_CHARS_BASE+ ('-' (PN_CHARS_BASE DIGIT)+)*
    ;

INTEGER
    : DIGIT+
    ;

DECIMAL
    : DIGIT+ '.' DIGIT*
    | '.' DIGIT+
    ;

DOUBLE
    : DIGIT+ '.' DIGIT* EXPONENT
    | '.' DIGIT+ EXPONENT
    | DIGIT+ EXPONENT
    ;

INTEGER_POSITIVE
    : '+' INTEGER
    ;

DECIMAL_POSITIVE
    : '+' DECIMAL
    ;

DOUBLE_POSITIVE
    : '+' DOUBLE
    ;

INTEGER_NEGATIVE
    : '-' INTEGER
    ;

DECIMAL_NEGATIVE
    : '-' DECIMAL
    ;

DOUBLE_NEGATIVE
    : '-' DOUBLE
    ;

EXPONENT
    : ('e'|'E') ('+'|'-')? DIGIT+
    ;

STRING_LITERAL1
    : '\'' ( ~('\u0027' | '\u005C' | '\u000A' | '\u000D') | ECHAR )* '\''
    ;

STRING_LITERAL2
    : '"'  ( ~('\u0022' | '\u005C' | '\u000A' | '\u000D') | ECHAR )* '"'
    ;

STRING_LITERAL_LONG1
    : '\'\'\'' ( ( '\'' | '\'\'' )? (~('\'' | '\\') | ECHAR ) )* '\'\'\''
    ;

STRING_LITERAL_LONG2
    : '"""' ( ( '"' | '""' )? ( ~('\'' | '\\') | ECHAR ) )* '"""'
    ;

ECHAR
    : '\\' ('t' | 'b' | 'n' | 'r' | 'f' | '"' | '\'')
    ;

NIL
    : '(' WS* ')'
    ;

ANON
    : '[' WS* ']'
    ;

PN_CHARS_U
    : PN_CHARS_BASE | '_'
    ;

VARNAME
    : ( PN_CHARS_U | DIGIT ) ( PN_CHARS_U | DIGIT | '\u00B7' | ('\u0300'..'\u036F') | ('\u203F'..'\u2040') )*
    ;

fragment
PN_CHARS
    : PN_CHARS_U
    | '-'
    | DIGIT
    /*| '\u00B7'
    | '\u0300'..'\u036F'
    | '\u203F'..'\u2040'*/
    ;

PN_PREFIX
    : PN_CHARS_BASE ((PN_CHARS|'.')* PN_CHARS)?
    ;

PN_LOCAL
    : ( PN_CHARS_U | DIGIT ) ((PN_CHARS|'.')* PN_CHARS)?
    ;

fragment
PN_CHARS_BASE
    : 'A'..'Z'
    | 'a'..'z'
    | '\u00C0'..'\u00D6'
    | '\u00D8'..'\u00F6'
    | '\u00F8'..'\u02FF'
    | '\u0370'..'\u037D'
    | '\u037F'..'\u1FFF'
    | '\u200C'..'\u200D'
    | '\u2070'..'\u218F'
    | '\u2C00'..'\u2FEF'
    | '\u3001'..'\uD7FF'
    | '\uF900'..'\uFDCF'
    | '\uFDF0'..'\uFFFD'
    ;

fragment
DIGIT
    : '0'..'9'
    ;
COM_SET
    : '#*';

WS:                 [ \t\r\n\u000C]+ -> channel(HIDDEN);
LINE_COMMENT:       '#' (~[\r\n*] ~[\r\n]*| ~[\r\n*]?)    -> channel(HIDDEN);