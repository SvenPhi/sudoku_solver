"""This program can solve Sudoku puzzles. Enter the numbers given and the
algorithm will solve the Sudoku.

The algorithm is an optimistic berserc:
    (1) Try to solve the sudoku by logic, if this does not work
    (2) brute force it.

Somehow the algorithm must know whether some conclusions have been made in one
logical iteration. Therefore every function that fills in numbers returns the
number of operations performed.

The algorithm solves the puzzle as follows:
    First, for each group, go through all fielda and check whether some
        potential values are already taken by another field in the group. If
        so, remove that value form the list of possible values.
    Second, if a value can be removed, check whether there is only possible
        value left; if this is the case, set the field to that value. Jump back
        to the first step to check for the consequences for the rest of the
        group.
"""

#Define classes for each part of the sudoku
class Field:
    """This class refers to the basic unit of the sudoku puzzle, the field in
    which a number between 1 and 9 is placed.
    
    It takes the argument max_digit, which is the biggest digit in the
    sudoku. Usually this is 9, but some games have only 6 digit."""
    
    def __init__(self, max_digit = 9, known_value = 0):
        self.digit = 0
        self.possibilities = [x for x in range(1, max_digit + 1)]
        self.solved = False
        #Define the group-register to which the field belongs:
        self.groups = list() 
        
        if known_value != 0: #Then the field is known.
            self.set_value(known_value)
            
    def __repr__(self):
        """__repr__ shows all relevant values of the field."""
        print('The field belongs to {0} groups:'.format(self.groups.__len__()))
        if self.solved:
            return print('it is solved, its value is {0}.'.format(self.digit))
        else:
            unsolved_str = 'it is unsolved, its possible values are ('
            for v in self.possibilities:
                unsolved_str +=' {0} '.format(v)
            unsolved_str += ').'
            print(unsolved_str)
    
    def add_group(self, group_address):
        """The method add_group simply adds a group to the group register of
        the field."""
        self.groups.append(group_address)    
        
    def set_value(self, value):
        """In case a value is known set_value() sets the field to this value
        and marks the field as a known field."""
        self.digit = value
        self.possibilities = list() #empty list
        self.solved = True
        
    
    def fill_check(self):
        """The method fill_check checks whether there is only one possible
        value left, setting the field to this value if true."""
        if (self.possibilities.__len__() == 1) and (not self.solved):
            #If there is only one possibility left, than set this one as value,
            self.digit = self.possibilities.pop() #returns the last value of the list and empties the list
            self.solved = True
            operations = 1 #omdat 1 actie is uitgevoerd
            
            #and check for the consequences in the rest of the group.
            operations += self.check_in_groups()

            return operations 
        else:
            return 0
            #raise ValueError('field-error: Inconsistency: {0} possible values and solved-bool is {1}.'.format(self.possibilities.__len__(), self.solved))
    
    def remove_possibility(self, value):
        """This method removes a value from the possibilities and checks whether
        the field can filled in."""
        if (not self.solved) and (self.possibilities.count(value) > 0):
            self.possibilities.remove(value)
            operations = self.fill_check()
            return operations + 1 #+1 for the removal of the value
        else:
            return 0
        
    def check_in_groups(self):
        """The check in groups method loops over all groups of the field to
        check for the consequences of the field value for the rest of the
        fields in the groups."""
        operations = 0
        for grp in self.groups:
            operations += grp.check_known_values(self)
            
        return operations


class Group:
    """All fields are grouped in rows, columns or blocks. This class is used to
    form such groups, being intialized with each sudoku board."""
    
    def __init__(self, group_fields, max_digit):
        """The argument group_fields is a list of fields that belong to the
        group."""
        self.fields = group_fields
        self.unknown_digits = range(1, max_digit + 1)
        self.digits_known = list() #empty list
        for f in self.fields:
            f.add_group(self)
        
    def __repr__():
        print('The unknown digits are:')
        print(self.unknown_digits)
        print('The fields are:')
        for f in self.fields:
            f.__repr__()
    
    def check_known_values(self, field_to_chk = None):
        """The method check_known_values looks for fields that are known and
        deletes these known digits from the possible digits of all other
        fields in the group."""
        operations = 0
        
        if field_to_chk is None:
            for f_s in self.fields: #Check for every field
                if f_s.solved: #whether the field is known
                    for f_u in self.fields:
                        operations += f_u.remove_possibility(f_s.digit)
        else: #field is given
            if field_to_chk.solved:
                for f_u in self.fields:
                    operations += f_u.remove_possibility(field_to_chk.digit)
        
        return operations
            

class Puzzle:
    """This class defines the board on which the sudoku is played. Two versions
    of the board can be played: the standard version with 9 digits and the easy
    version with 6 digits."""
    
    def __init__(self, max_digit = 9, initial_numbers = None):
        """This initializes the sudoku board. There are two options:
        - in case of 9 digits a 9x9 board,
        - in case of 6 digits a 6x9 board."""        
        self.board = list() #Define the board
        
        """On each board, the fields are grouped in rows, columns and blocks.
        These groups are catched by just one list of the class Group."""
        self.groups = list()
        
        if initial_numbers is not None: #Determine the size of the board.
            max_digit = int(initial_numbers.__len__())
        
        if max_digit in (6,9):
            #Define the fields
            for row in range(max_digit): #make the right number of rows
                fields = list()
                for col in range(max_digit): #for the number of columns
                    fields.append(Field(max_digit = max_digit)) #[Field()]*9 would creat a list of the same field, therefore it is per element.
                self.board.append(fields)
                
            #Sort the fields into groups
            #First the rows,
            for row_of_fields in self.board:
                self.groups.append(Group(row_of_fields, max_digit = max_digit))
            #second the columns,
            for col in range(max_digit):
                col_of_fields = list()
                for row in range(max_digit):
                    col_of_fields.append(self.board[row][col])
                self.groups.append(Group(col_of_fields, max_digit = max_digit))
            #third, and finally, the blocks.
            puzzle_fac = int(max_digit / 3) #Deze factor is nodig om dat blocken bij 6er sudoku het formaat 2x3 hebben.
            for block_row in range(puzzle_fac):
                for block_col in range(3):
                    block_of_fields = list()
                    for row in range(block_row * 3, (block_row + 1) * 3):
                        for col in range(block_col * puzzle_fac, (block_col + 1) * puzzle_fac):
                            block_of_fields.append(self.board[row][col])
                    self.groups.append(Group(block_of_fields, max_digit = max_digit))
        else:
            print('Error, wrong number of digits: {0}! A sudoku game must have 6 or 9 digits.'.format(max_digit))
         
        if initial_numbers is not None: #Set the values known:
            for row in range(max_digit):
                for col in range(max_digit):
                    if initial_numbers[row][col] in range(1,10):
                        print(row)
                        print(col)
                        print(initial_numbers[row][col])
                        self.board[row][col].set_value(initial_numbers[row][col])
            
        print('The puzzle has been set up.')


    def __repr__(self):
        for rows in range(self.board.__len__()):
            print('-------------------------------------')
            print_str = '|'
            for fields in self.board[rows]:
                print_str += ' {0} |'.format(fields.digit)
            print(print_str)
        print('-------------------------------------')
        
    def solve(self):
        """The method solve() initiates the next iteration of the solution of
        the puzzle."""
        
        operations = 0
        
        for grp in self.groups:
            operations += grp.check_known_values()
        
        return operations

def write_down_puzzle():
    """This function ask to fill in a sudoku and is returning the input as list
    of n lists with n elements each. n is either 6 or 9, depending on the
    sudoku at hand."""
    print(('This function allows to fill in a sudoku easily. After your has '
          'been made the puzzle will be solved automatically.\nLife can be so'
          ' easy!\n\nPlease enter the sudoku row by row, pressing the Enter '
          'button at the end of each row. Fill in the digits you know; enter a'
          ' 0 for all fields that are left blank in your puzzle.'))
    known_values = list()
    
    return known_values

def __main__():
    
    sudoku_puzzle = [[0,0,1,5,0,9,4,0,2],
                     [0,9,0,1,0,4,5,0,0],
                     [3,5,0,0,0,8,0,9,0],
                     [0,8,3,2,5,1,0,7,0],
                     [0,2,9,7,0,0,3,4,0],
                     [5,0,0,9,0,0,0,0,8],
                     [0,0,0,0,6,0,0,5,0],
                     [0,0,0,0,9,0,2,0,6],
                     [0,4,2,8,0,0,0,0,7]]
    
    super_die_hard_sudoku = Puzzle(initial_numbers = sudoku_puzzle)
    super_die_hard_sudoku.__repr__()

    operations = 1
    
    while operations > 0:
        operations = super_die_hard_sudoku.solve()
        print('{0} operations performed'.format(operations))
    
    super_die_hard_sudoku.__repr__()
    
__main__()


"""Tests:

    f_val = 1
    for grp in super_die_hard_sudoku.row_groups:
        for f in grp.fields:
            f.set_value(f_val)
        f_val += 1
    
    super_die_hard_sudoku.__repr__()    
    
"""

#======= Here starts the uselsss, old code==============================



    #Sudoku 1
    # Spielbrett.aender_feld(1,1,1)
    # Spielbrett.aender_feld(1,3,3)
    # Spielbrett.aender_feld(1,4,8)
    # Spielbrett.aender_feld(1,6,5)
    # Spielbrett.aender_feld(1,7,7)
    # Spielbrett.aender_feld(1,9,6)
    # Spielbrett.aender_feld(2,2,2)
    # Spielbrett.aender_feld(2,5,4)
    # Spielbrett.aender_feld(2,8,1)
    # Spielbrett.aender_feld(3,1,7)
    # Spielbrett.aender_feld(3,6,1)
    # Spielbrett.aender_feld(3,9,9)
    # Spielbrett.aender_feld(4,1,8)
    # Spielbrett.aender_feld(4,3,2)
    # Spielbrett.aender_feld(4,9,7)
    # Spielbrett.aender_feld(5,2,6)
    # Spielbrett.aender_feld(5,8,9)
    # Spielbrett.aender_feld(6,1,5)
    # Spielbrett.aender_feld(6,7,3)
    # Spielbrett.aender_feld(6,9,8)
    # Spielbrett.aender_feld(7,1,6)
    # Spielbrett.aender_feld(7,4,4)
    # Spielbrett.aender_feld(7,9,5)
    # Spielbrett.aender_feld(8,2,1)
    # Spielbrett.aender_feld(8,5,8)
    # Spielbrett.aender_feld(8,8,3)
    # Spielbrett.aender_feld(9,1,3)
    # Spielbrett.aender_feld(9,3,4)
    # Spielbrett.aender_feld(9,4,6)
    # Spielbrett.aender_feld(9,6,7)
    # Spielbrett.aender_feld(9,7,9)
    # Spielbrett.aender_feld(9,9,1)

    # Sudoku 2:
    Spielbrett.aender_feld(1,2,7)
    Spielbrett.aender_feld(1,5,4)
    Spielbrett.aender_feld(1,8,5)
    Spielbrett.aender_feld(2,1,1)
    Spielbrett.aender_feld(2,4,3)
    Spielbrett.aender_feld(2,6,7)
    Spielbrett.aender_feld(2,7,9)
    Spielbrett.aender_feld(2,9,6)
    Spielbrett.aender_feld(3,2,9)
    Spielbrett.aender_feld(4,2,4)
    Spielbrett.aender_feld(4,8,1)
    Spielbrett.aender_feld(5,1,7)
    Spielbrett.aender_feld(5,5,8)
    Spielbrett.aender_feld(5,9,2)
    Spielbrett.aender_feld(6,2,5)
    Spielbrett.aender_feld(6,8,9)
    Spielbrett.aender_feld(7,8,2)
    Spielbrett.aender_feld(8,1,3)
    Spielbrett.aender_feld(8,3,5)
    Spielbrett.aender_feld(8,4,2)
    Spielbrett.aender_feld(8,6,9)
    Spielbrett.aender_feld(8,9,1)
    Spielbrett.aender_feld(9,2,6)
    Spielbrett.aender_feld(9,5,1)
    Spielbrett.aender_feld(9,8,8)

