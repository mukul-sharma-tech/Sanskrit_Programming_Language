def compile_sanskrit_lang(source_code):
    lines = source_code.strip().split('\n')
    c_lines = [
        '#include <stdio.h>',
        'int main() {'
    ]

    for line in lines:
        line = line.strip()
        if line.startswith("स्थापय "):
            var = line[7:].split('=')[0].strip()
            expr = line.split('=')[1].rstrip(';').strip()
            c_lines.append(f'    int {var} = {expr};')
        elif line.startswith("लेखय("):
            start = line.find('(')
            end = line.rfind(')')
            if start == -1 or end == -1 or end <= start:
                raise SyntaxError("लेखय के अंदर सही पैरामीटर नहीं है (invalid print syntax)")
            var = line[start+1:end].strip()
            if not var:
                raise SyntaxError("लेखय के अंदर कोई मान नहीं है (empty argument in print)")
            c_lines.append(f'    printf("%d\\n", {var});')
        else:
            raise SyntaxError(f"अज्ञात वाक्यः: {line}")

    c_lines.append('    return 0;')
    c_lines.append('}')

    return '\n'.join(c_lines)

if __name__ == "__main__":
    with open("program.skt", "r", encoding="utf-8") as src:
        code = src.read()

    c_code = compile_sanskrit_lang(code)

    with open("program.c", "w", encoding="utf-8") as out:
        out.write(c_code)

    print("✅ Compilation complete! Run:")
    print("   gcc program.c -o program && ./program")
