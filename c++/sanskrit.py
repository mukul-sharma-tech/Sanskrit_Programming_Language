# import re
# import sys

# # =====================================================================
# # Lexer (Tokenizer)
# # =====================================================================
# # This part breaks the code into a sequence of tokens.

# class Token:
#     """Represents a token with a type and a value."""
#     def __init__(self, type, value, line=0, col=0):
#         self.type = type
#         self.value = value
#         self.line = line
#         self.col = col

#     def __repr__(self):
#         return f"Token({self.type}, {repr(self.value)})"

# # Token types
# TT_KEYWORD    = 'KEYWORD'
# TT_IDENTIFIER = 'IDENTIFIER'
# TT_NUMBER     = 'NUMBER'
# TT_LPAREN     = 'LPAREN'      # (
# TT_RPAREN     = 'RPAREN'      # )
# TT_LBRACE     = 'LBRACE'      # {
# TT_RBRACE     = 'RBRACE'      # }
# TT_EQ         = 'EQ'          # =
# TT_SEMICOLON  = 'SEMICOLON'   # ;
# TT_OPERATOR   = 'OPERATOR'
# TT_EOF        = 'EOF'         # End of File

# # Mapping of keywords to their Sanskrit representation
# KEYWORDS = {
#     'स्थापय': 'STAPAYA', # Assign/Declare
#     'लेखय': 'LEKHAYA',   # Print
#     'यदि': 'YADI',       # If
#     'अन्यथा': 'ANYATHA', # Else
#     'दौर': 'DAUR',       # While
# }

# class Lexer:
#     """
#     The lexer, responsible for breaking the source code
#     into a stream of tokens.
#     """
#     def __init__(self, text):
#         self.text = text
#         self.pos = 0
#         self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

#     def advance(self):
#         """Advance the position pointer and set the current character."""
#         self.pos += 1
#         self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

#     def skip_whitespace(self):
#         """Skips over whitespace characters."""
#         while self.current_char is not None and self.current_char.isspace():
#             self.advance()

#     def number(self):
#         """Return a multidigit integer consumed from the input."""
#         result = ''
#         while self.current_char is not None and self.current_char.isdigit():
#             result += self.current_char
#             self.advance()
#         return int(result)

#     def identifier(self):
#         """Handle identifiers and keywords."""
#         result = ''
#         # Sanskrit characters are not in isalnum, so we define a valid range
#         while self.current_char is not None and (self.current_char.isalnum() or '\u0900' <= self.current_char <= '\u097F'):
#             result += self.current_char
#             self.advance()
        
#         # Check if it's a keyword
#         if result in KEYWORDS:
#             return Token(TT_KEYWORD, result)
#         return Token(TT_IDENTIFIER, result)

#     def get_next_token(self):
#         """Lexical analyzer (also known as scanner or tokenizer)"""
#         while self.current_char is not None:
#             if self.current_char.isspace():
#                 self.skip_whitespace()
#                 continue

#             if self.current_char.isdigit():
#                 return Token(TT_NUMBER, self.number())

#             # Check for identifiers and keywords
#             if self.current_char.isalnum() or '\u0900' <= self.current_char <= '\u097F':
#                 return self.identifier()
            
#             if self.current_char == '(':
#                 self.advance()
#                 return Token(TT_LPAREN, '(')
            
#             if self.current_char == ')':
#                 self.advance()
#                 return Token(TT_RPAREN, ')')

#             if self.current_char == '{':
#                 self.advance()
#                 return Token(TT_LBRACE, '{')

#             if self.current_char == '}':
#                 self.advance()
#                 return Token(TT_RBRACE, '}')
            
#             if self.current_char == '=':
#                 self.advance()
#                 # Check for '=='
#                 if self.current_char == '=':
#                     self.advance()
#                     return Token(TT_OPERATOR, '==')
#                 return Token(TT_EQ, '=')

#             if self.current_char == ';':
#                 self.advance()
#                 return Token(TT_SEMICOLON, ';')

#             if self.current_char in ['+', '-', '*', '/', '%', '<', '>']:
#                 op = self.current_char
#                 self.advance()
#                 # Check for <= or >=
#                 if self.current_char == '=':
#                     op += self.current_char
#                     self.advance()
#                 return Token(TT_OPERATOR, op)

#             raise Exception(f"Invalid character: '{self.current_char}'")

#         return Token(TT_EOF, None)

# # =====================================================================
# # Parser and Transpiler (Combined for simplicity for now)
# # =====================================================================
# # This part understands the grammar and generates C++ code.

# class Compiler:
#     def __init__(self, source_code):
#         self.lexer = Lexer(source_code)
#         self.tokens = []
#         # Prime the token list
#         while True:
#             token = self.lexer.get_next_token()
#             self.tokens.append(token)
#             if token.type == TT_EOF:
#                 break
        
#         self.token_index = 0
#         self.current_token = self.tokens[self.token_index]
#         self.cpp_code = []
#         self.declared_vars = set()

#     def advance(self):
#         """Advance the token pointer."""
#         self.token_index += 1
#         if self.token_index < len(self.tokens):
#             self.current_token = self.tokens[self.token_index]
#         else:
#             self.current_token = Token(TT_EOF, None)

#     def eat(self, token_type, token_value=None):
#         """
#         Consume the current token if it matches the expected type and value.
#         Throws an error if it doesn't match.
#         """
#         if self.current_token.type == token_type and \
#            (token_value is None or self.current_token.value == token_value):
#             self.advance()
#         else:
#             expected = f"'{token_value}'" if token_value else token_type
#             raise Exception(f"Invalid syntax: Expected {expected}, got {self.current_token}")

#     def parse_expression(self):
#         """Parses a simple arithmetic or boolean expression."""
#         expr_tokens = []
#         while self.current_token.type not in [TT_SEMICOLON, TT_RPAREN, TT_LBRACE, TT_EOF]:
#             expr_tokens.append(str(self.current_token.value))
#             self.advance()
#         return " ".join(expr_tokens)

#     def parse_statement(self, indentation="    "):
#         """Parses a single statement."""
#         token = self.current_token

#         # स्थापय (Assignment)
#         if token.type == TT_KEYWORD and token.value == 'स्थापय':
#             self.eat(TT_KEYWORD, 'स्थापय')
#             var_name = self.current_token.value
#             self.eat(TT_IDENTIFIER)
#             self.eat(TT_EQ)
#             expr = self.parse_expression()
#             self.eat(TT_SEMICOLON)

#             if var_name in self.declared_vars:
#                 self.cpp_code.append(f"{indentation}{var_name} = {expr};")
#             else:
#                 self.cpp_code.append(f"{indentation}int {var_name} = {expr};")
#                 self.declared_vars.add(var_name)
        
#         # लेखय (Print)
#         elif token.type == TT_KEYWORD and token.value == 'लेखय':
#             self.eat(TT_KEYWORD, 'लेखय')
#             self.eat(TT_LPAREN)
#             expr = self.parse_expression()
#             self.eat(TT_RPAREN)
#             self.eat(TT_SEMICOLON)
#             self.cpp_code.append(f'{indentation}std::cout << {expr} << std::endl;')

#         # यदि (If statement)
#         elif token.type == TT_KEYWORD and token.value == 'यदि':
#             self.eat(TT_KEYWORD, 'यदि')
#             self.eat(TT_LPAREN)
#             condition = self.parse_expression()
#             self.eat(TT_RPAREN)
#             self.cpp_code.append(f"{indentation}if ({condition}) {{")
#             self.eat(TT_LBRACE)
#             self.parse_block(indentation + "    ")
#             self.eat(TT_RBRACE)
            
#             # अन्यथा (Else statement)
#             if self.current_token.type == TT_KEYWORD and self.current_token.value == 'अन्यथा':
#                 self.eat(TT_KEYWORD, 'अन्यथा')
#                 self.cpp_code.append(f"{indentation}}} else {{")
#                 self.eat(TT_LBRACE)
#                 self.parse_block(indentation + "    ")
#                 self.eat(TT_RBRACE)
#                 self.cpp_code.append(f"{indentation}}}")
#             else:
#                  self.cpp_code.append(f"{indentation}}}")

#         # दौर (While loop)
#         elif token.type == TT_KEYWORD and token.value == 'दौर':
#             self.eat(TT_KEYWORD, 'दौर')
#             self.eat(TT_LPAREN)
#             condition = self.parse_expression()
#             self.eat(TT_RPAREN)
#             self.eat(TT_LBRACE)
#             self.cpp_code.append(f"{indentation}while ({condition}) {{")
#             self.parse_block(indentation + "    ")
#             self.eat(TT_RBRACE)
#             self.cpp_code.append(f"{indentation}}}")
        
#         else:
#             raise Exception(f"Unexpected token: {token}")

#     def parse_block(self, indentation="    "):
#         """Parses a block of statements inside {}."""
#         while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
#             self.parse_statement(indentation)

#     def compile(self):
#         """Main compilation method."""
#         self.cpp_code.append("#include <iostream>")
#         self.cpp_code.append("\nint main() {")

#         while self.current_token.type != TT_EOF:
#             self.parse_statement()
            
#         self.cpp_code.append("    return 0;")
#         self.cpp_code.append("}")
#         return "\n".join(self.cpp_code)

# # =====================================================================
# # Main Driver
# # =====================================================================

# def main():
#     """Main function to run the compiler."""
#     # Create a sample program.skt file
#     sanskrit_code = """
# स्थापय x = 10;
# स्थापय y = 0;

# दौर (x > 0) {
#     यदि (x % 2 == 0) {
#         लेखय(x);
#         स्थापय y = y + x;
#     } अन्यथा {
#         स्थापय y = y - 1;
#     }
#     स्थापय x = x - 1;
# }

# लेखय(y);
# """
#     with open("program.skt", "w", encoding="utf-8") as f:
#         f.write(sanskrit_code)
    
#     print("📜 Created sample 'program.skt'.")
    
#     # Read the source file
#     try:
#         with open("program.skt", "r", encoding="utf-8") as src:
#             code = src.read()
#     except FileNotFoundError:
#         print("Error: 'program.skt' not found. Please create it.")
#         sys.exit(1)

#     # Compile the code
#     try:
#         compiler = Compiler(code)
#         cpp_code = compiler.compile()
#     except Exception as e:
#         print(f"❌ Compilation Error: {e}")
#         sys.exit(1)

#     # Write the output C++ file
#     with open("program.cpp", "w", encoding="utf-8") as out:
#         out.write(cpp_code)

#     print("\n✅ Compilation complete! C++ code written to 'program.cpp'.")
#     print("To run the compiled program, execute the following commands:")
#     print("\n  g++ program.cpp -o program && ./program\n")
#     print("--- Generated C++ Code ---")
#     print(cpp_code)
#     print("--------------------------")


# if __name__ == "__main__":
#     main()



import re
import sys

# =====================================================================
# Lexer (Tokenizer)
# =====================================================================
# This part breaks the code into a sequence of tokens.

class Token:
    """Represents a token with a type and a value."""
    def __init__(self, type, value, line=0, col=0):
        self.type = type
        self.value = value
        self.line = line
        self.col = col

    def __repr__(self):
        return f"Token({self.type}, {repr(self.value)})"

# Token types
TT_KEYWORD    = 'KEYWORD'
TT_IDENTIFIER = 'IDENTIFIER'
TT_NUMBER     = 'NUMBER'
TT_LPAREN     = 'LPAREN'      # (
TT_RPAREN     = 'RPAREN'      # )
TT_LBRACE     = 'LBRACE'      # {
TT_RBRACE     = 'RBRACE'      # }
TT_EQ         = 'EQ'          # =
TT_SEMICOLON  = 'SEMICOLON'   # ;
TT_OPERATOR   = 'OPERATOR'
TT_EOF        = 'EOF'         # End of File

# Mapping of keywords to their Sanskrit representation
KEYWORDS = {
    'स्थापय': 'STAPAYA', # Assign/Declare
    'लेखय': 'LEKHAYA',   # Print
    'यदि': 'YADI',       # If
    'अन्यथा': 'ANYATHA', # Else
    'दौर': 'DAUR',       # While
}

class Lexer:
    """
    The lexer, responsible for breaking the source code
    into a stream of tokens.
    """
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def advance(self):
        """Advance the position pointer and set the current character."""
        self.pos += 1
        self.current_char = self.text[self.pos] if self.pos < len(self.text) else None

    def skip_whitespace(self):
        """Skips over whitespace characters."""
        while self.current_char is not None and self.current_char.isspace():
            self.advance()

    def number(self):
        """Return a multidigit integer consumed from the input."""
        result = ''
        while self.current_char is not None and self.current_char.isdigit():
            result += self.current_char
            self.advance()
        return int(result)

    def identifier(self):
        """Handle identifiers and keywords."""
        result = ''
        # Sanskrit characters are not in isalnum, so we define a valid range
        while self.current_char is not None and (self.current_char.isalnum() or '\u0900' <= self.current_char <= '\u097F'):
            result += self.current_char
            self.advance()
        
        # Check if it's a keyword
        if result in KEYWORDS:
            return Token(TT_KEYWORD, result)
        return Token(TT_IDENTIFIER, result)

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char.isdigit():
                return Token(TT_NUMBER, self.number())

            # Check for identifiers and keywords
            if self.current_char.isalnum() or '\u0900' <= self.current_char <= '\u097F':
                return self.identifier()
            
            if self.current_char == '(':
                self.advance()
                return Token(TT_LPAREN, '(')
            
            if self.current_char == ')':
                self.advance()
                return Token(TT_RPAREN, ')')

            if self.current_char == '{':
                self.advance()
                return Token(TT_LBRACE, '{')

            if self.current_char == '}':
                self.advance()
                return Token(TT_RBRACE, '}')
            
            if self.current_char == '=':
                self.advance()
                # Check for '=='
                if self.current_char == '=':
                    self.advance()
                    return Token(TT_OPERATOR, '==')
                return Token(TT_EQ, '=')

            if self.current_char == ';':
                self.advance()
                return Token(TT_SEMICOLON, ';')

            if self.current_char in ['+', '-', '*', '/', '%', '<', '>']:
                op = self.current_char
                self.advance()
                # Check for <= or >=
                if self.current_char == '=':
                    op += self.current_char
                    self.advance()
                return Token(TT_OPERATOR, op)

            raise Exception(f"Invalid character: '{self.current_char}'")

        return Token(TT_EOF, None)

# =====================================================================
# Parser and Transpiler (Combined for simplicity for now)
# =====================================================================
# This part understands the grammar and generates C++ code.

class Compiler:
    def __init__(self, source_code):
        self.lexer = Lexer(source_code)
        self.tokens = []
        # Prime the token list
        while True:
            token = self.lexer.get_next_token()
            self.tokens.append(token)
            if token.type == TT_EOF:
                break
        
        self.token_index = 0
        self.current_token = self.tokens[self.token_index]
        self.cpp_code = []
        self.declared_vars = set()

    def advance(self):
        """Advance the token pointer."""
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = Token(TT_EOF, None)

    def eat(self, token_type, token_value=None):
        """
        Consume the current token if it matches the expected type and value.
        Throws an error if it doesn't match.
        """
        if self.current_token.type == token_type and \
           (token_value is None or self.current_token.value == token_value):
            self.advance()
        else:
            expected = f"'{token_value}'" if token_value else token_type
            raise Exception(f"Invalid syntax: Expected {expected}, got {self.current_token}")

    def parse_expression(self):
        """Parses a simple arithmetic or boolean expression."""
        expr_tokens = []
        while self.current_token.type not in [TT_SEMICOLON, TT_RPAREN, TT_LBRACE, TT_EOF]:
            expr_tokens.append(str(self.current_token.value))
            self.advance()
        return " ".join(expr_tokens)

    def parse_statement(self, indentation="    "):
        """Parses a single statement."""
        token = self.current_token

        # स्थापय (Assignment)
        if token.type == TT_KEYWORD and token.value == 'स्थापय':
            self.eat(TT_KEYWORD, 'स्थापय')
            var_name = self.current_token.value
            self.eat(TT_IDENTIFIER)
            self.eat(TT_EQ)
            expr = self.parse_expression()
            self.eat(TT_SEMICOLON)

            if var_name in self.declared_vars:
                self.cpp_code.append(f"{indentation}{var_name} = {expr};")
            else:
                self.cpp_code.append(f"{indentation}int {var_name} = {expr};")
                self.declared_vars.add(var_name)
        
        # लेखय (Print)
        elif token.type == TT_KEYWORD and token.value == 'लेखय':
            self.eat(TT_KEYWORD, 'लेखय')
            self.eat(TT_LPAREN)
            expr = self.parse_expression()
            self.eat(TT_RPAREN)
            self.eat(TT_SEMICOLON)
            self.cpp_code.append(f'{indentation}cout << {expr} << endl;')

        # यदि (If statement)
        elif token.type == TT_KEYWORD and token.value == 'यदि':
            self.eat(TT_KEYWORD, 'यदि')
            self.eat(TT_LPAREN)
            condition = self.parse_expression()
            self.eat(TT_RPAREN)
            self.cpp_code.append(f"{indentation}if ({condition}) {{")
            self.eat(TT_LBRACE)
            self.parse_block(indentation + "    ")
            self.eat(TT_RBRACE)
            
            # अन्यथा (Else statement)
            if self.current_token.type == TT_KEYWORD and self.current_token.value == 'अन्यथा':
                self.eat(TT_KEYWORD, 'अन्यथा')
                self.cpp_code.append(f"{indentation}}} else {{")
                self.eat(TT_LBRACE)
                self.parse_block(indentation + "    ")
                self.eat(TT_RBRACE)
                self.cpp_code.append(f"{indentation}}}")
            else:
                 self.cpp_code.append(f"{indentation}}}")

        # दौर (While loop)
        elif token.type == TT_KEYWORD and token.value == 'दौर':
            self.eat(TT_KEYWORD, 'दौर')
            self.eat(TT_LPAREN)
            condition = self.parse_expression()
            self.eat(TT_RPAREN)
            self.eat(TT_LBRACE)
            self.cpp_code.append(f"{indentation}while ({condition}) {{")
            self.parse_block(indentation + "    ")
            self.eat(TT_RBRACE)
            self.cpp_code.append(f"{indentation}}}")
        
        else:
            raise Exception(f"Unexpected token: {token}")

    def parse_block(self, indentation="    "):
        """Parses a block of statements inside {}."""
        while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
            self.parse_statement(indentation)

    def compile(self):
        """Main compilation method."""
        self.cpp_code.append("#include <iostream>")
        self.cpp_code.append("using namespace std;")
        self.cpp_code.append("\nint main() {")

        while self.current_token.type != TT_EOF:
            self.parse_statement()
            
        self.cpp_code.append("    return 0;")
        self.cpp_code.append("}")
        return "\n".join(self.cpp_code)

# =====================================================================
# Main Driver
# =====================================================================

def main():
    """Main function to run the compiler."""
    # Create a sample program.skt file
    sanskrit_code = """
स्थापय x = 10;
स्थापय y = 0;

दौर (x > 0) {
    यदि (x % 2 == 0) {
        लेखय(x);
        स्थापय y = y + x;
    } अन्यथा {
        स्थापय y = y - 1;
    }
    स्थापय x = x - 1;
}

लेखय(y);
"""
    with open("program.skt", "w", encoding="utf-8") as f:
        f.write(sanskrit_code)
    
    print("📜 Created sample 'program.skt'.")
    
    # Read the source file
    try:
        with open("program.skt", "r", encoding="utf-8") as src:
            code = src.read()
    except FileNotFoundError:
        print("Error: 'program.skt' not found. Please create it.")
        sys.exit(1)

    # Compile the code
    try:
        compiler = Compiler(code)
        cpp_code = compiler.compile()
    except Exception as e:
        print(f"❌ Compilation Error: {e}")
        sys.exit(1)

    # Write the output C++ file
    with open("program.cpp", "w", encoding="utf-8") as out:
        out.write(cpp_code)

    print("\n✅ Compilation complete! C++ code written to 'program.cpp'.")
    print("To run the compiled program, execute the following commands:")
    print("\n  g++ program.cpp -o program && ./program\n")
    print("--- Generated C++ Code ---")
    print(cpp_code)
    print("--------------------------")


if __name__ == "__main__":
    main()
