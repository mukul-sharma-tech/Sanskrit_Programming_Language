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
TT_COMMA      = 'COMMA'       # ,
TT_SEMICOLON  = 'SEMICOLON'   # ;
TT_OPERATOR   = 'OPERATOR'
TT_EOF        = 'EOF'         # End of File

# Mapping of keywords to their Sanskrit representation
KEYWORDS = {
    'स्थापय': 'STAPAYA',     # Assign/Declare
    'लेखय': 'LEKHAYA',       # Print
    'यदि': 'YADI',           # If
    'अन्यथा': 'ANYATHA',     # Else
    'दौर': 'DAUR',           # While
    'कार्यम्': 'KARYAM',     # Function
    'प्रतिफलम्': 'PRATIPHALAM', # Return
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

    def skip_comment(self):
        """Skips a single-line comment starting with '#'."""
        while self.current_char is not None and self.current_char != '\n':
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
        
        if result in KEYWORDS:
            return Token(TT_KEYWORD, result)
        return Token(TT_IDENTIFIER, result)

    def get_next_token(self):
        """Lexical analyzer (also known as scanner or tokenizer)"""
        while self.current_char is not None:
            if self.current_char.isspace():
                self.skip_whitespace()
                continue

            if self.current_char == '#':
                self.skip_comment()
                continue

            if self.current_char.isdigit():
                return Token(TT_NUMBER, self.number())

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
            
            if self.current_char == ',':
                self.advance()
                return Token(TT_COMMA, ',')

            if self.current_char == '=':
                self.advance()
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
                if self.current_char == '=':
                    op += self.current_char
                    self.advance()
                return Token(TT_OPERATOR, op)

            raise Exception(f"Invalid character: '{self.current_char}'")

        return Token(TT_EOF, None)

# =====================================================================
# Parser and Transpiler
# =====================================================================
# This part understands the grammar and generates C++ code.

class Compiler:
    def __init__(self, source_code):
        self.lexer = Lexer(source_code)
        self.tokens = []
        while True:
            token = self.lexer.get_next_token()
            self.tokens.append(token)
            if token.type == TT_EOF:
                break
        
        self.token_index = 0
        self.current_token = self.tokens[self.token_index]
        self.cpp_code = []
        self.translit_map = {}

    def _transliterate(self, word):
        """A simple transliteration to create valid C++ identifiers."""
        mapping = {
            'अ': 'a', 'आ': 'aa', 'इ': 'i', 'ई': 'ii', 'उ': 'u', 'ऊ': 'uu',
            'ऋ': 'ri', 'ए': 'e', 'ऐ': 'ai', 'ओ': 'o', 'औ': 'au', 'ं': 'm', 'ः': 'h',
            'क': 'k', 'ख': 'kh', 'ग': 'g', 'घ': 'gh', 'ङ': 'ng',
            'च': 'ch', 'छ': 'chh', 'ज': 'j', 'झ': 'jh', 'ञ': 'ny',
            'ट': 't', 'ठ': 'th', 'ड': 'd', 'ढ': 'dh', 'ण': 'n',
            'त': 't', 'थ': 'th', 'द': 'd', 'ध': 'dh', 'न': 'n',
            'प': 'p', 'फ': 'ph', 'ब': 'b', 'भ': 'bh', 'म': 'm',
            'य': 'y', 'र': 'r', 'ल': 'l', 'व': 'v',
            'श': 'sh', 'ष': 'sh', 'स': 's', 'ह': 'h',
            'क्ष': 'ksh', 'त्र': 'tr', 'ज्ञ': 'gy',
            'ा': 'aa', 'ि': 'i', 'ी': 'ii', 'ु': 'u', 'ू': 'uu',
            'ृ': 'ri', 'े': 'e', 'ै': 'ai', 'ो': 'o', 'ौ': 'au',
            '्': ''
        }
        # This is a simplified transliteration logic
        res = ""
        for char in word:
            res += mapping.get(char, char)
        
        ascii_name = re.sub(r'[^a-zA-Z0-9_]', '', res)
        if ascii_name and ascii_name[0].isdigit():
            return '_' + ascii_name
        return ascii_name or "unnamed"

    def advance(self):
        """Advance the token pointer."""
        self.token_index += 1
        if self.token_index < len(self.tokens):
            self.current_token = self.tokens[self.token_index]
        else:
            self.current_token = Token(TT_EOF, None)

    def eat(self, token_type, token_value=None):
        """Consume the current token if it matches the expected type and value."""
        if self.current_token.type == token_type and \
           (token_value is None or self.current_token.value == token_value):
            self.advance()
        else:
            expected = f"'{token_value}'" if token_value else token_type
            raise Exception(f"Invalid syntax: Expected {expected}, got {self.current_token}")

    def parse_expression(self):
        """Parses an expression, transliterating identifiers."""
        expr_parts = []
        paren_depth = 0
        while self.current_token.type != TT_EOF:
            if self.current_token.type in [TT_SEMICOLON, TT_RPAREN, TT_LBRACE] and paren_depth == 0:
                break
            if self.current_token.type == TT_COMMA and paren_depth == 0:
                 break

            if self.current_token.type == TT_LPAREN:
                paren_depth += 1
            elif self.current_token.type == TT_RPAREN:
                paren_depth -= 1
            
            token_value = self.current_token.value
            if self.current_token.type == TT_IDENTIFIER:
                # Use the already transliterated name if available
                expr_parts.append(self.translit_map.get(token_value, token_value))
            else:
                expr_parts.append(str(token_value))
            
            self.advance()
        return " ".join(expr_parts)

    def parse_statement(self, declared_vars, indentation="    "):
        """Parses a single statement within a block."""
        token = self.current_token

        if token.type == TT_KEYWORD and token.value == 'स्थापय':
            self.eat(TT_KEYWORD, 'स्थापय')
            var_name_skt = self.current_token.value
            self.eat(TT_IDENTIFIER)
            
            var_name_ascii = self._transliterate(var_name_skt)
            self.translit_map[var_name_skt] = var_name_ascii

            self.eat(TT_EQ)
            expr = self.parse_expression()
            self.eat(TT_SEMICOLON)

            if var_name_skt in declared_vars:
                self.cpp_code.append(f"{indentation}{var_name_ascii} = {expr};")
            else:
                self.cpp_code.append(f"{indentation}int {var_name_ascii} = {expr};")
                declared_vars.add(var_name_skt)
        
        elif token.type == TT_KEYWORD and token.value == 'लेखय':
            self.eat(TT_KEYWORD, 'लेखय')
            self.eat(TT_LPAREN)
            expr = self.parse_expression()
            self.eat(TT_RPAREN)
            self.eat(TT_SEMICOLON)
            self.cpp_code.append(f'{indentation}cout << {expr} << endl;')

        elif token.type == TT_KEYWORD and token.value == 'प्रतिफलम्':
            self.eat(TT_KEYWORD, 'प्रतिफलम्')
            expr = self.parse_expression()
            self.eat(TT_SEMICOLON)
            self.cpp_code.append(f'{indentation}return {expr};')

        elif token.type == TT_KEYWORD and token.value == 'यदि':
            self.eat(TT_KEYWORD, 'यदि')
            self.eat(TT_LPAREN)
            condition = self.parse_expression()
            self.eat(TT_RPAREN)
            self.cpp_code.append(f"{indentation}if ({condition}) {{")
            self.eat(TT_LBRACE)
            self.parse_block(declared_vars.copy(), indentation + "    ")
            self.eat(TT_RBRACE)
            
            if self.current_token.type == TT_KEYWORD and self.current_token.value == 'अन्यथा':
                self.eat(TT_KEYWORD, 'अन्यथा')
                self.cpp_code.append(f"{indentation}}} else {{")
                self.eat(TT_LBRACE)
                self.parse_block(declared_vars.copy(), indentation + "    ")
                self.eat(TT_RBRACE)
                self.cpp_code.append(f"{indentation}}}")
            else:
                 self.cpp_code.append(f"{indentation}}}")

        elif token.type == TT_KEYWORD and token.value == 'दौर':
            self.eat(TT_KEYWORD, 'दौर')
            self.eat(TT_LPAREN)
            condition = self.parse_expression()
            self.eat(TT_RPAREN)
            self.eat(TT_LBRACE)
            self.cpp_code.append(f"{indentation}while ({condition}) {{")
            self.parse_block(declared_vars.copy(), indentation + "    ")
            self.eat(TT_RBRACE)
            self.cpp_code.append(f"{indentation}}}")
        
        else:
            # Handle function calls as statements
            expr = self.parse_expression()
            if self.current_token.type == TT_SEMICOLON:
                self.eat(TT_SEMICOLON)
                self.cpp_code.append(f"{indentation}{expr};")
            else:
                raise Exception(f"Unexpected statement: {token}")

    def parse_block(self, declared_vars, indentation="    "):
        """Parses a block of statements inside {}."""
        while self.current_token.type != TT_RBRACE and self.current_token.type != TT_EOF:
            self.parse_statement(declared_vars, indentation)

    def parse_function_definition(self):
        """Parses a function definition."""
        self.eat(TT_KEYWORD, 'कार्यम्')
        func_name_skt = self.current_token.value
        func_name_ascii = 'main' if func_name_skt == 'मुख्य' else self._transliterate(func_name_skt)
        self.translit_map[func_name_skt] = func_name_ascii
        
        self.eat(TT_IDENTIFIER)
        self.eat(TT_LPAREN)
        
        params_skt = []
        if self.current_token.type == TT_IDENTIFIER:
            params_skt.append(self.current_token.value)
            self.eat(TT_IDENTIFIER)
            while self.current_token.type == TT_COMMA:
                self.eat(TT_COMMA)
                params_skt.append(self.current_token.value)
                self.eat(TT_IDENTIFIER)
        self.eat(TT_RPAREN)
        
        cpp_params = []
        for p_skt in params_skt:
            p_ascii = self._transliterate(p_skt)
            self.translit_map[p_skt] = p_ascii
            cpp_params.append(f"int {p_ascii}")

        self.cpp_code.append(f"int {func_name_ascii}({', '.join(cpp_params)}) {{")
        
        self.eat(TT_LBRACE)
        
        function_scope_vars = set(params_skt)
        self.parse_block(function_scope_vars, "    ")
        
        self.eat(TT_RBRACE)
        self.cpp_code.append("}\n")

    def compile(self):
        """Main compilation method."""
        self.cpp_code.append("#include <iostream>")
        self.cpp_code.append("using namespace std;")
        self.cpp_code.append("")

        while self.current_token.type != TT_EOF:
            if self.current_token.type == TT_KEYWORD and self.current_token.value == 'कार्यम्':
                self.parse_function_definition()
            else:
                if self.current_token.type != TT_EOF:
                    raise Exception("Only function definitions are allowed at the top level.")
        
        return "\n".join(self.cpp_code)

# =====================================================================
# Main Driver
# =====================================================================

def main():
    """Main function to run the compiler."""
    # Create a sample program.skt file demonstrating functions and recursion
    sanskrit_code = """
# Recursive factorial function
कार्यम् भाज्यम्(n) {
    यदि (n <= 1) {
        प्रतिफलम् 1;
    }
    
    प्रतिफलम् n * भाज्यम्(n - 1);
}

# Main entry point of the program
कार्यम् मुख्य() {
    स्थापय संख्या = 5;
    स्थापय परिणाम = भाज्यम्(संख्या);
    
    लेखय(परिणाम); # Expected output: 120
    
    प्रतिफलम् 0; # Return 0 from main
}
"""
    with open("program.skt", "w", encoding="utf-8") as f:
        f.write(sanskrit_code)
    
    print("📜 Created sample 'program.skt' with a recursive function.")
    
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
