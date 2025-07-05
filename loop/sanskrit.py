def compile_sanskrit_lang(source_code):
    lines = source_code.strip().split('\n')
    c_lines = [
        '#include <stdio.h>',
        'int main() {'
    ]
    
    declared_vars = set()
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        
        if line.startswith("स्थापय "):
            var = line[7:].split('=')[0].strip()
            expr = line.split('=')[1].rstrip(';').strip()
            if var in declared_vars:
                c_lines.append(f'    {var} = {expr};')  # update only
            else:
                c_lines.append(f'    int {var} = {expr};')  # declare new
                declared_vars.add(var)
            i += 1

        elif line.startswith("लेखय("):
            start = line.find('(')
            end = line.rfind(')')
            var = line[start+1:end].strip()
            c_lines.append(f'    printf("%d\\n", {var});')
            i += 1

        elif line.startswith("दौर("):
            start = line.find('(')
            end = line.rfind(')')
            condition = line[start+1:end].strip()
            c_lines.append(f'    while ({condition}) {{')

            i += 1  # move into loop body

            # loop body parsing
            while i < len(lines):
                inner_line = lines[i].strip()
                if inner_line == '}':
                    c_lines.append('    }')
                    i += 1
                    break
                elif inner_line.startswith("स्थापय "):
                    var = inner_line[7:].split('=')[0].strip()
                    expr = inner_line.split('=')[1].rstrip(';').strip()
                    if var in declared_vars:
                        c_lines.append(f'        {var} = {expr};')  # update only
                    else:
                        c_lines.append(f'        int {var} = {expr};')
                        declared_vars.add(var)
                elif inner_line.startswith("लेखय("):
                    start = inner_line.find('(')
                    end = inner_line.rfind(')')
                    var = inner_line[start+1:end].strip()
                    c_lines.append(f'        printf("%d\\n", {var});')
                else:
                    raise SyntaxError(f"अज्ञात वाक्यः: {inner_line}")
                i += 1
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
