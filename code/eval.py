import math
import random
import re
storage = {}

integer_variables = []
string_variables = []

class LogicEval:
    symbols = {}
    functions = {}
    operators = {
        "ou": lambda args: args[0] or args[1],
        "∨": lambda args: args[0] or args[1],
        "e": lambda args: args[0] and args[1],
        "∧": lambda args: args[0] and args[1],
        "nao": lambda a: not a[0],
        "+": lambda args: args[0] + args[1],
        "-": lambda args: args[0] - args[1],
        "*": lambda args: args[0] * args[1],
        "/": lambda args: args[0] / args[1],
        "t": lambda args: args[0] ** args[1],
        ">": lambda args: args[0] > args[1],
        "<": lambda args: args[0] < args[1],
        "cos": lambda args: math.cos(args[0]),
        "sen": lambda args: math.sin(args[0]),
        "atribui": lambda args: LogicEval._atribui(args),
        "aleatorio": lambda args: LogicEval._aleatorio(*args),
        "escrever": lambda a: print(*a),
        "entrada": lambda a: input(*a),
        "se": lambda args: LogicEval._se(*args),
        "para": lambda args: LogicEval._para(*args),
        "var": lambda args: LogicEval._vars(args),
        "funcao": lambda args: LogicEval._funcao(args),
        "fim": lambda args: LogicEval._fim(),
        "call": lambda args: LogicEval._call(args)
    }

    @staticmethod
    def _para(args):
        var, start_value, end_value = args
        start_value = LogicEval.evaluate_expression(start_value)
        end_value = LogicEval.evaluate_expression(end_value)
        for i in range(start_value, end_value + 1):
            LogicEval.symbols[var] = i
        return None

    @staticmethod
    def _se(cond, entao, senao):
        return LogicEval.eval(entao if cond else senao)

    @staticmethod
    def _vars(args):
        for var in args:
            LogicEval.symbols[var] = None

    def _atribui(args):  # A=10   {'op':'atr'  'args': [ "A", 10 ]}  =>  _attrib( [ 'A', 10 ] )
        varid = args[0]  # 'A'
        value = args[1]  # 10
        LogicEval.symbols[varid] = value  # symbols { 'A':10 }
        return None

    def _aleatorio(var, limit):
        value = random.randint(0, limit)
        LogicEval.symbols[var] = value
        return value

    @staticmethod
    def _call(args):
        name, arg_list = args
        if name not in LogicEval.functions:
            raise Exception(f"Function not defined: {name}")
        if len(arg_list) != len(LogicEval.functions[name]["var_list"]):
            raise Exception(f"Function called with the wrong number of arguments: {name}")
        for var, value in zip(LogicEval.functions[name]["var_list"], arg_list):
            LogicEval.symbols[var] = value
        result = LogicEval.eval(LogicEval.functions[name]["code"])
        for var in LogicEval.functions[name]["var_list"]:
            del LogicEval.symbols[var]
        return result

    @staticmethod
    def _funcao(args):
        function_name = args[0]
        var_list = args[1]
        code = args[2]
        LogicEval.functions[function_name] = {"var_list": var_list, "code": code}

    @staticmethod
    def _fim():
        return None

    @staticmethod
    def eval(ast):
        if type(ast) is int:  # constant value, eg in (int, str)
            return ast
        if type(ast) is dict:  # { 'op': ... , 'args': ...}
            return LogicEval.eval_operator(ast)
        if type(ast) is str:
            return ast
        raise Exception(f"Unknown AST type")

    @staticmethod
    def eval_operator(ast):
        if 'op' in ast:
            op = ast["op"]
            args = [LogicEval.evaluate(a) for a in ast['args']]
            if op in LogicEval.operators:
                func = LogicEval.operators[op]
                return func(args)
            else:
                raise Exception(f"Unknown operator {op}")

        if 'var' in ast:
            varid = ast["var"]     #ast={ 'var': "A" } =>   ast["var"]   varid="A"
            if varid in LogicEval.symbols:  # "A" in symbols { 'A':10 }
                return LogicEval.symbols[varid]   # 10
            raise Exception(f"error: '{varid}' undeclared (first use in this function)")
        raise Exception('Undefined AST')

    @staticmethod
    def evaluate(instruction_sequence):
        for instruction in instruction_sequence:
            result = LogicEval.eval_operator(instruction)
            if result is not None:
                print(f"<< {result}", end="\n\n")

    @staticmethod
    def parse_instruction(instruction):
        instruction = instruction.strip()

        # Skip empty lines
        if not instruction:
            return ""

        # Skip single-line comments
        if instruction.startswith("//"):
            return ""

        # Skip multi-line comments
        if "/*" in instruction and "*/" in instruction:
            return ""

        if instruction.startswith(" "):
            return f"\t{instruction.strip()}"

        if instruction == "}":
            return "}"

        if instruction == "fim;":
            return "}"

        parts = instruction.split(" ")

        if len(parts) < 2:
            return ""
        opcode = parts[0]

        if opcode == "var":
            # Check if the instruction has the correct number of tokens
            if len(parts) != 4:
                return "Invalid variable instruction: incorrect number of tokens"

            # Extract the variable name and value tokens
            variable_name = parts[1]
            assignment_operator = parts[2]
            variable_value = parts[3]

            # Check if the variable name is valid (e.g., alphanumeric)
            if not variable_name.isalnum():
                return "Invalid variable name: must be alphanumeric"

            # Check if the assignment operator is "="
            if assignment_operator != "=" and assignment_operator != "+=":
                return "Invalid assignment operator: must be '=' or '+='"

            if variable_value.startswith("aleatorio(") and variable_value.endswith(");"):
                # Extract the range from the variable value
                range_value = variable_value[10:-2]  # Extract the range value from "aleatorio(range)"

                # Check if the range value is a valid integer
                if not range_value.isdigit():
                    return "Invalid range value: must be an integer"

                # Generate a random number within the given range
                variable_value = random.randint(0, int(range_value))
            elif variable_value.startswith('"') and variable_value.endswith('"'):
                # Text variable
                variable_value = variable_value[1:-1]
                string_variables.append(variable_name)
            else:
                # Check if the variable value is a numeric operation
                if re.match(r'^\d+(\s*[-+\/*]\s*\d+)*$', variable_value):
                    # Evaluate the numeric operation expression
                    try:
                        if assignment_operator == "+=":
                            # Retrieve the previously stored value
                            previous_value = storage.get(variable_name, 0)
                            variable_value = LogicEval.evaluate_expression(f"{previous_value} + ({variable_value})")
                        else:
                            variable_value = LogicEval.evaluate_expression(variable_value)
                            integer_variables.append(variable_name)
                    except:
                        return "Invalid variable value: unable to evaluate numeric operation"
                else:
                    # Check if the variable value is referencing another variable
                    if variable_value in storage:
                        variable_value = storage[variable_value]
                    else:
                        return "Invalid variable value: must be a number or a numeric operation"
            # Store the variable in the storage
            storage[variable_name] = variable_value
            # Return a success message
            return f"Variable '{variable_name}' set to {variable_value}"
        elif opcode == "escrever":
            message = " ".join(parts[1:]).strip(';')
            variable = parts[1].strip(";")
            if any(char.isdigit() for char in message):
                # Check if the message contains numeric operations
                if re.match(r'^\d+(\s*[-+\/*]\s*\d+)*$', message):
                    # Evaluate the numeric operation expression
                    try:
                        result = LogicEval.evaluate_expression(message)
                        return f'printf("%d", {result});'
                    except:
                        return "Invalid numeric operation in escrever instruction"
                else:
                    return f'printf("%d", {message});'
            if variable in integer_variables:
                return f'printf("%d", &{variable});'
            elif variable in string_variables:
                return f'printf("%s", {variable});'
            else:
                return f'printf({message});'
        elif opcode == "entrada":
            variable = parts[1].strip(";")

            # Check if the variable is an integer or string
            if variable in integer_variables:
                return f'scanf("%d", &{variable});'
            elif variable in string_variables:
                return f'scanf("%s", {variable});'
            else:
                return ""
        elif opcode == "se":
            condition = " ".join(parts[1:parts.index("entao")])
            entao_body = parts[parts.index("entao") + 1:parts.index("senao")] if "senao" in parts else parts[parts.index("entao") + 1:]
            senao_body = parts[parts.index("senao") + 1:] if "senao" in parts else []
            try:
                if LogicEval.evaluate_condition(condition):
                    output = 'if ' + condition + ' {\n\t'
                    output_added = False  # Flag to track if any output was added
                    message = " ".join(parts[parts.index("entao") + 2:parts.index("senao")])
                    for instruction in entao_body:
                        if instruction.startswith("escrever"):
                            if re.match(r'^\d+(\s*[-+\/*]\s*\d+)*$', message):
                                output += "printf(%d," + LogicEval.evaluate_expression(message) + '\n\t\t'
                                output_added = True  # Set the flag to True
                            else:
                                output += "printf(%s," + message + ');\n'
                                output_added = True  # Set the flag to True
                        if instruction.startswith("entrada"):
                            variable = parts[parts.index("entao") + 2:parts.index("senao")]
                            print(variable)
                            print(integer_variables)
                            print(string_variables)
                            for var in variable:
                                # Check if the variable is an integer or string
                                if var in integer_variables:
                                    output += f'scanf("%d", &{var});\n'
                                    output_added = True
                                if var in string_variables:
                                    output += f'scanf("%s", {var});\n'
                                    output_added = True
                    if not output_added:
                        output += '// Add default output or alternative instructions\n'
                    output += '\t}'
                    return output
                else:
                    output = 'else {\n\t'
                    output_added = False  # Flag to track if any output was added
                    message = " ".join(parts[parts.index("senao") + 2:])
                    for instruction in senao_body:
                        if instruction.startswith("escrever"):
                            if re.match(r'^\d+(\s*[-+\/*]\s*\d+)*$', message):
                                output += "printf(%d," + LogicEval.evaluate_expression(message) + '\n'
                                output_added = True  # Set the flag to True
                            else:
                                output += "printf(%s," + message + ');\n'
                                output_added = True  # Set the flag to True
                        if instruction.startswith("entrada"):
                            variable = parts[parts.index("senao") + 2:]
                            for var in variable:
                                # Check if the variable is an integer or string
                                if var in integer_variables:
                                    output += f'scanf("%d", &{var});\n'
                                    output_added = True
                                if var in string_variables:
                                    output += f'scanf("%s", {var});\n'
                                    output_added = True
                    if not output_added:
                        output += '\t// Add default output or alternative instructions\n'
                    output += '\t}'
                    return output
            except:
                return "Invalid condition in se instruction"
        elif opcode == "para":
            loop_variable, start_value, end_value = parts[1].strip("("), parts[3].strip("("), parts[5].strip("( )")
            instruction = " ".join(parts[8:]).strip(";")
            loop_output = f'for (int {loop_variable} = {start_value}; {loop_variable} <= {end_value}; {loop_variable}++)' + ' {\n'
            fazer_body = parts[parts.index("fazer") + 1:] if "fazer" in parts else []
            message = " ".join(parts[parts.index("fazer") + 2:])
            try:
                start_value = int(start_value)
                end_value = int(end_value)
                for i in range(start_value, end_value + 1):
                    LogicEval.symbols[loop_variable] = i
                    for instruction in fazer_body:
                        if instruction.startswith("escrever"):
                            if re.match(r'^\d+(\s*[-+\/*]\s*\d+)*$', message):
                                loop_output += "\tprintf(%d," + LogicEval.evaluate_expression(message) + '\n'
                            else:
                                loop_output += "\tprintf(%s," + message + ');\n'
                        if instruction.startswith("entrada"):
                            variable = parts[parts.index("fazer") + 2:]
                            for var in variable:
                                # Check if the variable is an integer or string
                                if var in integer_variables:
                                    loop_output += f'\tscanf("%d", &{var});\n'
                                if var in string_variables:
                                    loop_output += f'\tscanf("%s", {var});\n'
                loop_output += '\t}'
                return loop_output
            except ValueError:
                loop_output = f"Invalid start or end value in para loop: {start_value}, {end_value}"
            return loop_output
        elif opcode == "funcao":
            function_name = parts[1].strip("(")
            arguments = " ".join(parts[2:]).strip("( ){")
            return f'void {function_name}({arguments})' + '{'
        elif opcode == "call":
            function_name = parts[1].strip("(")
            arguments = ", ".join(parts[2:]).strip(");")
            return f'{function_name}{arguments});'
        elif opcode == "nao":
            condition = " ".join(parts[1:]).strip(';')
            return f'!{condition};'
        elif opcode == "fim;":
            return '}'
        else:
            if len(parts) >= 3 and parts[1] == "=":
                variable = parts[0]
                if variable not in integer_variables and variable not in string_variables:
                    return f'Error: Variable "{variable}" is not declared.'
            return ""

    @staticmethod
    def translate_instruction(instruction):
        instruction = instruction.strip()
        # Skip empty lines
        if not instruction:
            return ""
        # Skip single-line comments
        if instruction.startswith("//"):
            return ""
        # Skip multi-line comments
        if "/*" in instruction and "*/" in instruction:
            return ""
        if instruction.startswith(" "):
            return f"\t{instruction.strip()}"
        if instruction == "}":
            return "}"
        if instruction == "fim;":
            return "}"

        parts = instruction.split(" ")
        opcode = parts[0]

        if opcode == "escrever":
            message = " ".join(parts[1:]).strip(';')
            if any(char.isdigit() for char in message):
                # Add "%d" before number operations
                return f'printf("%d", {message});'
            else:
                return f'printf({message});'
        elif opcode == "entrada":
            variable = parts[1].strip(";")

            # Check if the variable is an integer or string
            if variable in integer_variables:
                return f'scanf("%d", &{variable});'
            elif variable in string_variables:
                return f'scanf("%s", {variable});'
            else:
                return ""
        elif opcode == "var":
            variables = []
            variable_list = " ".join(parts[1:]).strip(";")
            aleatorio_value = re.findall(r'\d+', parts[3])  # Extract the number inside aleatorio()
            declarations = re.split(r',\s*(?=[a-zA-Z0-9_]+)', variable_list)
            for idx, declaration in enumerate(declarations):
                var_parts = declaration.split("=")
                var_name = var_parts[0].strip()
                var_value = var_parts[1].strip() if len(var_parts) > 1 else ""
                tab = "\t" if idx > 0 else ""
                if var_value.startswith('"') and var_value.endswith('"'):
                    variable = f'{tab}char* {var_name} = {var_value};'
                    string_variables.append(var_name)
                else:
                    variable = f'{tab}int {var_name} = {var_value};'
                    integer_variables.append(var_name)
                variables.append(variable)
                if var_name == "aleatorio" and aleatorio_value:
                    limit = aleatorio_value[0]
                    return f'int aleatorio = rand() % ({limit} + 1);'
            return "\n".join(variables)
        elif opcode == "se":
            condition = " ".join(parts[1:parts.index("entao")])
            entao_body = parts[parts.index("entao") + 1:parts.index("senao")] if "senao" in parts else parts[ parts.index("entao") + 1:]
            senao_body = parts[parts.index("senao") + 1:] if "senao" in parts else []

            try:
                output = 'if ' + condition + ' {\n\t\t'
                output_added = False  # Flag to track if any output was added
                message = " ".join(parts[parts.index("entao") + 2:parts.index("senao")])
                for instruction in entao_body:
                    if instruction.startswith("escrever"):
                        if re.match(r'^\d+(\s*[-+\/*]\s*\d+)*$', message):
                            output += "printf(%d," + message + '\n\t\t'
                            output_added = True  # Set the flag to True
                        else:
                            output += "printf(%s," + message + ');\n'
                            output_added = True  # Set the flag to True
                if not output_added:
                    output += '\t// Add default output or alternative instructions\n'
                output += '\t}'
                output += 'else {\n\t\t'
                output_added = False  # Flag to track if any output was added
                message = " ".join(parts[parts.index("senao") + 2:])
                for instruction in senao_body:
                    if instruction.startswith("escrever"):
                        if re.match(r'^\d+(\s*[-+\/*]\s*\d+)*$', message):
                            output += "printf(%d," + message + '\n'
                            output_added = True  # Set the flag to True
                        else:
                            output += "printf(%s," + message + ');\n'
                            output_added = True  # Set the flag to True
                if not output_added:
                    output += '\t// Add default output or alternative instructions\n'
                output += '\t}'
                return output
            except:
                return "Invalid condition in se instruction"

        elif opcode == "para":
            loop_variable = parts[1].strip("(")
            start_value = parts[3]
            end_value = parts[5].strip(")")
            instruction = " ".join(parts[8:]).strip(";")
            message_parts = re.findall(r'\"(.+?)\"', instruction)
            if len(message_parts) > 0:
                message = message_parts[0]
                instruction = instruction.replace('"' + message + '"', f'"{message}"')
            return f'for (int {loop_variable} = {start_value}; {loop_variable} <= {end_value}; {loop_variable}++)' + '{' + f'\n\t\tprintf({instruction});\n\t{"}"}'
        elif opcode == "funcao":
            function_name = parts[2].strip("(")
            arguments = " ".join(parts[3:]).strip(" {")
            return f'void {function_name}({arguments}){"{"} '
        elif opcode == "nao":
            condition = " ".join(parts[1:]).strip(';')
            return f'!{condition};'
        elif opcode == "fim":
            return '}'
        else:
            return ""
        print(instruction)

    @staticmethod
    def evaluate_expression(expression):
        # Replace variables with their corresponding values
        for variable_name, variable_value in storage.items():
            expression = expression.replace(variable_name, str(variable_value))
        # Evaluate the expression using Python's eval() function
        result = eval(expression)
        return result

    @staticmethod
    def evaluate_condition(condition):
        pattern = r"\((.*)\)"  # Regular expression pattern to extract the condition expression
        match = re.search(pattern, condition)

        if not match:
            return False

        condition_expr = match.group(1)
        parts = re.split(r"(<=|>=|==|<|>|!=)", condition_expr)  # Split the expression based on comparison operators

        if len(parts) != 3:
            return False

        left_operand = parts[0].strip()
        operator = parts[1].strip()
        right_operand = parts[2].strip()

        left_value = None
        right_value = None

        if left_operand in storage:
            left_value = storage[left_operand]
        else:
            try:
                left_value = float(left_operand)  # Convert the left operand to a float if it's a number
            except ValueError:
                return False

        if right_operand in storage:
            right_value = storage[right_operand]
        else:
            try:
                right_value = float(right_operand)  # Convert the right operand to a float if it's a number
            except ValueError:
                return False

        if operator == ">":
            return left_value > right_value
        elif operator == "<":
            return left_value < right_value
        elif operator == "==":
            return left_value == right_value
        elif operator == ">=":
            return left_value >= right_value
        elif operator == "<=":
            return left_value <= right_value
        elif operator == "!=":
            return left_value != right_value

        return False