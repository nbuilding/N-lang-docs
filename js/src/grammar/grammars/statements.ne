@lexer lexer

block -> (statement blockSeparator):* statement {% from(ast.Block) %}

statement -> "import" _ identifier {% from(ast.ImportStmt) %}
	| letStatement {% id %}
	| varStatement {% id %}
	| enumDeclaration {% id %}
	| aliasDefinition {% id %}
	| classDeclaration {% id %}
	| oldForLoop {% id %}
	| forLoop {% id %}
	| postfixExpressionImpure {% id %}
	| returnExpression {% id %}

letStatement -> ("let" _) ("pub" _):? declaration (_ "=" _) expression {% from(ast.LetStmt) %}

varStatement -> ("var" _) identifier (_ "=" _) expression {% from(ast.VarStmt) %}

enumDeclaration -> ("type" _) ("pub" _):? typeSpec (_ "=" _) enumDefinition {% from(ast.EnumDeclaration) %}

enumDefinition -> enumVariant ((_ "|" _) enumVariant):*

enumVariant -> ("<" _) identifier (_ typeValue):* (_ ">")
	| identifier

aliasDefinition -> ("alias" _) ("pub" _):? typeSpec (_ "=" _) type {% from(ast.AliasDeclaration) %}

classDeclaration -> ("class" _) ("pub" _):? identifier _ arguments (_ "{" _) block (_ "}") {% from(ast.ClassDeclaration) %}

oldForLoop -> ("for" _) declaration _ value (_ "{" _) block (_ "}") {% from(ast.OldFor) %}

forLoop -> ("for" _ "(" _) declaration (_ "in" _) expression (_ ")" _ "{" _) block (_ "}") {% from(ast.For) %}

ifStatement -> ("if" _) expression (_ "{" _) block (_ "}") ((_ "else" _) elseStatement):? {% from(ast.IfStmt) %}

elseStatement -> "{" _ block _ "}" {% includeBrackets %}
	| ifStatement {% id %}

typeSpec -> identifier typeVarsDeclaration:? {% from(ast.TypeSpec) %}

typeVarsDeclaration -> ("[" _) (identifier (_ "," _)):* identifier ((_ ","):? _ "]")
