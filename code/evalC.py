from eval import LogicEval


class LogicEvalC:
    @staticmethod
    def generate_c_code(instructions):
        codigo_c = ""

        # Add the main function
        codigo_c += "#include <stdio.h>\n\n"
        codigo_c += "int main() {\n"

        # Add the instructions as C code
        codigo_c += "\t/* Generated instructions */\n"
        for instruction in instructions:
            c_instruction = LogicEval.translate_instruction(instruction)
            codigo_c += f"\t{c_instruction}\n"

        # Close the main function
        codigo_c += "\treturn 0;\n"
        codigo_c += "}\n"
        return codigo_c

    @staticmethod
    def compile_code(instructions):
        codigo_c = ""

        # Add the instructions as C code
        codigo_c += "\* Generated instructions */\n"
        for instruction in instructions:
            c_instruction = LogicEval.parse_instruction(instruction)
            codigo_c += f"{c_instruction}\n"

        return codigo_c
