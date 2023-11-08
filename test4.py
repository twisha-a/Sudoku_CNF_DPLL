import re
import argparse

# Create the parser and add arguments
parser = argparse.ArgumentParser(description='Sudoku Solver with Verbose Mode')
parser.add_argument('-v', '--verbose', action='store_true', help='Enable verbose mode')
parser.add_argument('filename', type=str, nargs='?', default='D:/D Drive/college classes/ai/lab/examples/easy.input',
                    help='The filename of the Sudoku puzzle')
args = parser.parse_args()

# Extract verbose mode and filename from parsed arguments
verbose_mode = args.verbose
filename = args.filename

if verbose_mode:
    print(f"Verbose mode is enabled. Reading Sudoku puzzle from {filename}")

# filename = 'D:/D Drive/college classes/ai/lab/examples/easy.input'
class Helper:  
    @staticmethod
    def read_input_file(filename):
        with open(filename, 'r') as infile:
            # Read the entire file, which should be one line
            line = infile.read().strip()

        # Define a pattern to match valid input lines (e.g., '11=4')
        valid_pattern = re.compile(r"^\d\d=\d$")

        # Split the line into parts and parse each part
        parts = line.split(' ')
        atoms = []
        for part in parts:
            if part and valid_pattern.match(part):  # check if part is not an empty string and matches the pattern
                row, col, val = int(part[0]), int(part[1]), int(part[3])
                # Generate a positive CNF clause for the given value
                atom = Helper.get_atom_for_square(row, col, val, False)
                atoms.append(atom)
            else:
                print(f"Skipping invalid input part: '{part}'")

        return atoms
    
    @staticmethod
    def get_atom_for_square(row, col, val, negate):
        s = f'n{val}_r{row}_c{col}'
        if negate:
            s = '!' + s
        return s
    

class CNF_Solver:
    def __init__(self):
        self.s = set()

    def insert_into_main_set(self, x, y):
        sorted_tuple = tuple(sorted((x, y)))
        self.s.add(sorted_tuple)

    def generate_cnf_for_single_digit_in_box(self):
        for i in range(1, 10):
            for j in range(1, 10):
                ss = [Helper.get_atom_for_square(i, j, k, False) for k in range(1, 10)]
                ss.sort()
                self.s.add(tuple(ss))

                for k in range(1, 10):
                    x = Helper.get_atom_for_square(i, j, k, True)
                    for l in range(1, 10):
                        if l != k:
                            y = Helper.get_atom_for_square(i, j, l, True)
                            self.insert_into_main_set(x, y)

    def generate_cnf_for_unique_row(self):
        for i in range(1, 10):
            for j in range(1, 10):
                for k in range(1, 10):
                    x = Helper.get_atom_for_square(i, j, k, True)
                    for l in range(1, 10):
                        if l != j:
                            y = Helper.get_atom_for_square(i, l, k, True)
                            self.insert_into_main_set(x, y)

    def generate_cnf_for_unique_column(self):
        for i in range(1, 10):
            for j in range(1, 10):
                for k in range(1, 10):
                    x = Helper.get_atom_for_square(i, j, k, True)
                    for l in range(1, 10):
                        if l != i:
                            y = Helper.get_atom_for_square(l, j, k, True)
                            self.insert_into_main_set(x, y)

    def generate_cnf_for_unique_three_cross_three_subgrid(self):
        for i in range(1, 10):
            for j in range(1, 10):
                ri = 3 * ((i - 1) // 3) + 1
                ci = 3 * ((j - 1) // 3) + 1
                for k in range(1, 10):
                    x = Helper.get_atom_for_square(i, j, k, True)
                    for l in range(ri, ri + 3):
                        for m in range(ci, ci + 3):
                            if l != i or m != j:
                                y = Helper.get_atom_for_square(l, m, k, True)
                                self.insert_into_main_set(x, y)

    def populate_cnf_for_input(self, atoms):
        for item in atoms:
            self.s.add((item,))

    def generate_cnf_clauses(self, atoms):
        self.generate_cnf_for_single_digit_in_box()
        self.generate_cnf_for_unique_row()
        self.generate_cnf_for_unique_column()
        self.generate_cnf_for_unique_three_cross_three_subgrid()
        self.populate_cnf_for_input(atoms)

    def cnf_to_string(self):
        # Convert each tuple to a string of space-separated literals
        return '\n'.join(' '.join(clause) for clause in self.s)

    def write_cnf_to_file(self, filename):
        # Convert the CNF clauses to a string
        cnf_string = self.cnf_to_string()
        # Write the string to a file
        with open(filename, 'w') as outfile:
            outfile.write(cnf_string)

## DPLL
# global function


class DPLL_Solver:
    def __init__(self, clauses):
        self.clauses = clauses
        self.assignment = {literal.strip('!'): 'UNBOUND' for clause in clauses for literal in clause}

    @staticmethod
    def parse_cnf(cnf_string):
        clauses = []
        for line in cnf_string.strip().split('\n'):
            clause = set(line.split())
            clauses.append(clause)
        return clauses

    def find_unit_clauses(self):
        unit_clauses = {next(iter(c)) for c in self.clauses if len(c) == 1}
        return unit_clauses

    def find_pure_literals(self):
        all_literals = set()
        for clause in self.clauses:
            if clause:  # make sure the clause is not empty
                all_literals.update(clause)

        positive_literals = {lit for lit in all_literals if not lit.startswith('!')}
        negative_literals = {lit[1:] for lit in all_literals if lit.startswith('!')}

        pure_literals = positive_literals - negative_literals
        pure_literals.update(f'!{lit}' for lit in negative_literals - positive_literals)

        return pure_literals

    def propagate(self, A):
        S = self.clauses.copy()
        V = self.assignment
        for clause in list(S):
            if (A in clause and V[A] == True) or (f"!{A}" in clause and V[A] == False):
                S.remove(clause)
            elif A in clause and V[A] == False:
                clause.remove(A)
            elif f"!{A}" in clause and V[A] == True:
                clause.remove(f"!{A}")
        self.clauses = S

    def obvious_assign(self, L):
        V = self.assignment
        if L.startswith("!"):
            A = L[1:]
            V[A] = False
        else:
            V[L] = True

    # ... Add additional methods such as assign(), dpll(), etc. ...

    @staticmethod
    def cnf_to_dpll_input(cnf_solver):
        cnf_string = cnf_solver.cnf_to_string()
        return DPLL_Solver.parse_cnf(cnf_string)
    
    def dp1(self):
        # BASE OF THE RECURSION: SUCCESS OR FAILURE
        if not self.clauses:  # Success: All clauses are satisfied
            return {atom: (True if self.assignment[atom] == 'UNBOUND' else self.assignment[atom]) for atom in self.assignment}

        elif any(not clause for clause in self.clauses):  # Failure: Some clause is unsatisfiable under self.assignment
            return None

        # EASY CASES: PURE LITERAL ELIMINATION AND FORCED ASSIGNMENT
        while True:
            pure_literals = self.find_pure_literals()
            unit_clauses = self.find_unit_clauses()
            
            if pure_literals:  # Pure literal elimination
                for literal in pure_literals:
                    self.obvious_assign(literal)
                    self.clauses = [clause for clause in self.clauses if literal not in clause]

            elif unit_clauses:  # Forced assignment
                for literal in unit_clauses:
                    self.obvious_assign(literal)
                    self.propagate(literal.strip('!'))

            else:
                break  # No easy cases found, exit loop

        # HARD CASE: PICK SOME ATOM AND TRY EACH ASSIGNMENT IN TURN
        for atom in self.assignment:
            if self.assignment[atom] == 'UNBOUND':
                for value in (True, False):
                    self.assignment[atom] = value
                    self.propagate(atom)
                    v_new = self.dp1()
                    if v_new is not None:
                        return v_new
                    self.assignment[atom] = 'UNBOUND'  # Undo the assignment and backtrack
                    self.clauses = self.clauses.copy()  # Reset clauses to original state

        return None
    
    def write_dpll_to_file(self, filename):
        with open(filename, 'w') as outfile:
            for variable, value in self.assignment.items():
                outfile.write(f'{variable}: {value}\n')

## OUTPUT GENERATION ##
# FOR CNF

cnf_solver = CNF_Solver()
initial_atoms = Helper.read_input_file(filename)
cnf_solver.generate_cnf_clauses(initial_atoms)
cnf_output_filename = './cnf_test_file.txt'
cnf_solver.write_cnf_to_file(cnf_output_filename)
if verbose_mode:
    print("CNF clauses generated and written to file.")

# FOR DPLL
dpll_input = DPLL_Solver.cnf_to_dpll_input(cnf_solver)
dpll_solver = DPLL_Solver(dpll_input)
solution = dpll_solver.dp1()
if verbose_mode:
    print(f"DPLL solution found: {solution}")
# Print the solution
# print(f"DPLL solution: {solution}")
dpll_output_filename = './dpll_test_file.txt'
dpll_solver.write_dpll_to_file(dpll_output_filename)

if verbose_mode:
    print(f"DPLL output written to {dpll_output_filename}")

## SUDOKU BOARD
positive_literals = {}

# Read the DPLL output from the file
with open(dpll_output_filename, 'r') as file:
    dpll_output = file.read()

# Split the output into lines and process each line
for line in dpll_output.strip().split('\n'):
    # Split each line into the atom and its boolean value
    atom, value = line.split(': ')
    # Only proceed if the value is True
    if value.strip() == 'True':
        # The atom is in the form 'nX_rY_cZ', we'll split it by '_' and then strip the leading characters from each part
        parts = atom.split('_')
        if len(parts) == 3:
            number = int(parts[0][1:])  # Strip the leading 'n' and convert to int
            row = int(parts[1][1:])     # Strip the leading 'r' and convert to int
            column = int(parts[2][1:])  # Strip the leading 'c' and convert to int
            # Add the number to the positive literals dictionary with the row and column as a tuple key
            positive_literals[(row, column)] = number

# Now we construct the Sudoku board
# Initialize a 9x9 board with zeros
sudoku_board = [[0 for _ in range(9)] for _ in range(9)]

# Fill the board with the numbers from the positive literals
for (row, column), number in positive_literals.items():
    sudoku_board[row - 1][column - 1] = number  # Adjust index since Sudoku indices start from 1

# Convert the board to a string for display
sudoku_board_display = "\n".join([" ".join(map(str, row)) for row in sudoku_board])
# print(sudoku_board_display)

sudoku_solution_filename = './sudoku_solution.txt'  # You can change this to your desired file path

# Write the Sudoku board display string to a file
with open(sudoku_solution_filename, 'w') as file:
    file.write(sudoku_board_display)
if verbose_mode:
    print(f"Sudoku board written to {sudoku_solution_filename}")