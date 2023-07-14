from grammar import LogicGrammar
import re
from evalC import LogicEvalC
import argparse
import random

lg = LogicGrammar()
lg.build()
COMPILATION_MODES = ["c", "console"]

def run_interactively():
    for e in iter(lambda: input(">> "), ""):
        try:
            ans = lg.parse(e)
            if ans is not None:
                print(f"<< {ans}", end="\n\n")
        except Exception as exception:
            print(exception)


def run_batch(filename, mode):
    try:
        with open(filename, "r") as f:
            content = f.read().splitlines()

        if mode == "c":
            # Generate the C code from the instruction sequence
            codigo_c = LogicEvalC.generate_c_code(content)
            # Save the generated C code to a file
            with open('programa.c', 'w') as file:
                file.write(codigo_c)
            print(f"File 'programa.c' generated successfully!")
        elif mode == "console":
            # Generate the C code from the instruction sequence
            codigo_c = LogicEvalC.compile_code(content)
            # Print the generated C code to the console
            print("Generated C code:")
            print(codigo_c)
        else:
            print("Invalid compilation mode specified.")

    except FileNotFoundError:
        print(f"The input file '{filename}' was not found.")
    except IOError as e:
        print(f"Error reading or writing file: {str(e)}")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


parser = argparse.ArgumentParser()
parser.add_argument("--file", help="Execute in batch mode with input file", type=str)
parser.add_argument("--mode", help="Compilation mode: 'c' or 'console'", type=str, default="console")
args = parser.parse_args()

if args.file is not None:
    run_batch(args.file, args.mode)
elif args.mode == "console":
    run_interactively()
else:
    print("No input file provided. Please specify a file using the --file argument.")