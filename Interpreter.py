import re

class RobotParser:
    def __init__(self):
        self.variables = {}
        self.procedures = {}

    def parse_program(self, filename):
        with open(filename, 'r') as f:
            program_lines = f.readlines()

        program_lines = [line.strip() for line in program_lines]
        program_lines = [line for line in program_lines if line]  

        try:
            self.parse_variables(program_lines)
            self.parse_procedures(program_lines)
            self.parse_main_block(program_lines)
            return True  
        except SyntaxError as e:
            print(f"Syntax Error: {e}")
            return False

    def parse_variables(self, lines):
        for line in lines:
            if line.startswith("|"):
                var_names = line.strip('|').split()
                for var_name in var_names:
                    if not re.match(r"^[a-z][a-zA-Z0-9]*$", var_name):
                        raise SyntaxError(f"Invalid variable name: {var_name}")
                    self.variables[var_name] = None  
            else:
                break 

    def parse_procedures(self, lines):
      proc_pattern = r"^proc\s+([a-z][a-zA-Z0-9]*):\s*((?:[a-z][a-zA-Z0-9]*\s*:\s*[a-z][a-zA-Z0-9]*\s*)*)\[(.*?)\]$"
      proc_no_param_pattern = r"^proc\s+([a-z][a-zA-Z0-9]*)\s*\[(.*?)\]$"
      i = 0
      while i < len(lines):
          line = lines[i]
          match = re.match(proc_pattern, line)
          if match:
              proc_name = match.group(1)
              params_str = match.group(2).strip()
              params = []
              if params_str:
                param_pairs = params_str.split("and")
                for pair in param_pairs:
                  parts = pair.split(":")
                  if len(parts) != 2:
                    raise SyntaxError(f"Invalid Parameters for procedure: {proc_name}")
                  param_name = parts[0].strip()
                  params.append(param_name)
              block = match.group(3)
              self.procedures[proc_name] = {"params": params, "block": block}
              i += 1
          else:
            match = re.match(proc_no_param_pattern, line)
            if match:
              proc_name = match.group(1)
              block = match.group(2)
              self.procedures[proc_name] = {"params": [], "block": block}
              i += 1
            else:
              i += 1

    def parse_main_block(self, lines):
        start_block = False
        for line in lines:
          if line.startswith("["):
            start_block = True
          elif start_block and line.startswith("]"):
            return 
          elif start_block:
            self.parse_statement(line) 

    def parse_statement(self, statement):
        assignment_match = re.match(r"^([a-z][a-zA-Z0-9]*)\s*:=\s*(#?[a-zA-Z0-9]+)\s*\.$", statement)
        if assignment_match:
            var_name = assignment_match.group(1)
            value = assignment_match.group(2)
            if var_name not in self.variables:
                raise SyntaxError(f"Variable '{var_name}' not defined.")
        proc_call_match = re.match(r"^([a-z][a-zA-Z0-9]*):((?:\s*[a-z][a-zA-Z0-9]*\s*:\s*(#?[a-zA-Z0-9]+)\s*)*)\.$", statement)
        if proc_call_match:
          proc_name = proc_call_match.group(1)
          args_str = proc_call_match.group(2).strip()
          args = []
          if args_str:
            arg_pairs = args_str.split("and")
            for pair in arg_pairs:
              parts = pair.split(":")
              if len(parts) != 2:
                raise SyntaxError(f"Invalid Arguments for procedure: {proc_name}")
              arg_val = parts[1].strip()
              args.append(arg_val)
          if proc_name not in self.procedures:
            raise SyntaxError(f"Procedure '{proc_name}' not defined.")
          defined_params = self.procedures[proc_name].get("params", [])
          if len(args) != len(defined_params):
            raise SyntaxError(f"Procedure '{proc_name}' called with incorrect number of arguments.")

parser = RobotParser()
filename = input("Ingresa la direccion del archivo usando / como signo de jerarquia")
if parser.parse_program(filename):
    print("Program syntax is correct.")
else:
    print("Program syntax is incorrect.")