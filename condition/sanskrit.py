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

        # स्थापय var = expr;
        if line.startswith("स्थापय "):
            var = line[7:].split('=')[0].strip()
            expr = line.split('=')[1].rstrip(';').strip()
            if var in declared_vars:
                c_lines.append(f'    {var} = {expr};')
            else:
                c_lines.append(f'    int {var} = {expr};')
                declared_vars.add(var)
            i += 1

        # लेखय(expr);
        elif line.startswith("लेखय("):
            start = line.find('(')
            end = line.rfind(')')
            var = line[start+1:end].strip()
            if not var:
                raise SyntaxError("लेखय के अंदर कोई मान नहीं है (empty argument in print)")
            c_lines.append(f'    printf("%d\\n", {var});')
            i += 1

        # दौर(condition) { ... }
        elif line.startswith("दौर"):
            start = line.find('(')
            end = line.rfind(')')
            if start == -1 or end == -1 or start > end:
                raise SyntaxError("गलत दौर अभिव्यक्ति (invalid while expression)")
            condition = line[start+1:end].strip()
            c_lines.append(f'    while ({condition}) {{')

            i += 1
            # Parse loop body until '}'
            while i < len(lines):
                inner_line = lines[i].strip()
                if inner_line == '}':
                    c_lines.append('    }')
                    i += 1
                    break
                # reuse parsing logic inside loop body
                if inner_line.startswith("स्थापय "):
                    var = inner_line[7:].split('=')[0].strip()
                    expr = inner_line.split('=')[1].rstrip(';').strip()
                    if var in declared_vars:
                        c_lines.append(f'        {var} = {expr};')
                    else:
                        c_lines.append(f'        int {var} = {expr};')
                        declared_vars.add(var)
                elif inner_line.startswith("लेखय("):
                    start2 = inner_line.find('(')
                    end2 = inner_line.rfind(')')
                    var2 = inner_line[start2+1:end2].strip()
                    if not var2:
                        raise SyntaxError("लेखय के अंदर कोई मान नहीं है (empty argument in print)")
                    c_lines.append(f'        printf("%d\\n", {var2});')
                else:
                    raise SyntaxError(f"अज्ञात वाक्यः: {inner_line}")
                i += 1

        # यदि (condition) { ... }
        elif line.startswith("यदि"):
            start = line.find('(')
            end = line.rfind(')')
            if start == -1 or end == -1 or start > end:
                raise SyntaxError("गलत यदि अभिव्यक्ति (invalid if expression)")
            condition = line[start+1:end].strip()
            c_lines.append(f'    if ({condition}) {{')
            i += 1

            # Parse if block until '}'
            while i < len(lines):
                inner_line = lines[i].strip()
                if inner_line == '}':
                    c_lines.append('    }')
                    i += 1
                    break
                if inner_line.startswith("स्थापय "):
                    var = inner_line[7:].split('=')[0].strip()
                    expr = inner_line.split('=')[1].rstrip(';').strip()
                    if var in declared_vars:
                        c_lines.append(f'        {var} = {expr};')
                    else:
                        c_lines.append(f'        int {var} = {expr};')
                        declared_vars.add(var)
                elif inner_line.startswith("लेखय("):
                    start2 = inner_line.find('(')
                    end2 = inner_line.rfind(')')
                    var2 = inner_line[start2+1:end2].strip()
                    if not var2:
                        raise SyntaxError("लेखय के अंदर कोई मान नहीं है (empty argument in print)")
                    c_lines.append(f'        printf("%d\\n", {var2});')
                else:
                    raise SyntaxError(f"अज्ञात वाक्यः: {inner_line}")
                i += 1

        # अन्यथा { ... }
        elif line.startswith("अन्यथा"):
            if not line.strip().endswith("{"):
                raise SyntaxError("अन्यथा के बाद '{' होना चाहिए")
            c_lines.append('    else {')
            i += 1

            # Parse else block until '}'
            while i < len(lines):
                inner_line = lines[i].strip()
                if inner_line == '}':
                    c_lines.append('    }')
                    i += 1
                    break
                if inner_line.startswith("स्थापय "):
                    var = inner_line[7:].split('=')[0].strip()
                    expr = inner_line.split('=')[1].rstrip(';').strip()
                    if var in declared_vars:
                        c_lines.append(f'        {var} = {expr};')
                    else:
                        c_lines.append(f'        int {var} = {expr};')
                        declared_vars.add(var)
                elif inner_line.startswith("लेखय("):
                    start2 = inner_line.find('(')
                    end2 = inner_line.rfind(')')
                    var2 = inner_line[start2+1:end2].strip()
                    if not var2:
                        raise SyntaxError("लेखय के अंदर कोई मान नहीं है (empty argument in print)")
                    c_lines.append(f'        printf("%d\\n", {var2});')
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
