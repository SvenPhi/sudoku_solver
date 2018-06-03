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
        if not self.solved:
            self.digit = value
            self.possibilities = list() #empty list
            self.solved = True
        else:
            raise Exception("The value for this field has already been set.")
        
    
    def fill_check(self):
        """The method fill_check checks whether there is only one possible
        value left, setting the field to this value if true."""
        if (self.possibilities.__len__() == 1) and (not self.solved):
            #If there is only one possibility left, than set this one as value,
            self.digit = self.possibilities.pop() #returns the last value of the list and empties the list
            self.solved = True
            operations = 1 #because one action has been performed
            
            #Check in all groups whether the value has already been taken by
            #another field, ...
            self.check_for_double_values(method_name = "fill_check", just_figured_out = True)
                        
            #... and check for the consequences in the rest of the group.
            operations += self.check_in_groups()

            return operations 
        else:
            return 0

    
    def check_for_double_values(self, method_name, just_figured_out = False):
        """This method raises an error is a value is taken twice in a group."""
        if self.solved:
            for grp in self.groups:
                if just_figured_out and (self.digit not in grp.unknown_values):
                    error_str = method_name + ": The value {0} has been concluded on twice.".format(self.digit)
                    raise ValueError(error_str)
                for f in grp.fields:
                    if (f != self) and (f.digit == self.digit):
                        error_str = method_name + ": The value {0} has been concluded on twice.".format(self.digit)
                        raise ValueError(error_str)
    
    def remove_possibility(self, value):
        """This method removes a value from the possibilities and checks whether
        the field can filled in."""
        if (not self.solved) and (value in self.possibilities):
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
        #The list of fields of which the group is comprised.
        self.fields = group_fields
        for f in self.fields:
            f.add_group(self)
            
        #The list with all values that are unknown within the group.
        self.unknown_values = [x for x in range(1, max_digit + 1)]
        self.unsolved = True #this is set False, when the group is solved.
        
        
    def __repr__(self):
        print('The fields are:')
        for f in self.fields:
            f.__repr__()
        prt_str = "The subsets of unknown values are ["
        for p in self.subsets_of_unknown():
            prt_str += "{0}, ".format(p)
        prt_str += "]."
        print(prt_str)
        
        
    def get_to_know_value(self, digit):
        """This method sets a value to known for the group"""
        if (self.unknown_values.count(digit) > 0) and self.unsolved:
            self.unknown_values.remove(digit)
            if self.unknown_values.__len__() == 0:
                self.unsolved = False
                
                
    def check_known_values(self, field_to_chk = None):
        """The method check_known_values looks for fields that are known and
        deletes these known digits from the possible digits of all other
        fields in the group."""
        
        operations = 0
        
        if self.unsolved:
            if field_to_chk is None:
                for f_s in self.fields: #Check for every field
                    if f_s.solved: #whether the field is known
                        self.get_to_know_value(f_s.digit)
                        for f_u in self.fields:
                            operations += f_u.remove_possibility(f_s.digit)
                    else:
                        for v in f_s.possibilities: #If v is in the possible values of the field,
                            if v not in self.unknown_values: #but not in the possible values of the group
                                operations += f_s.remove_possibility(v) #then remove it form the possible values of the field. 
            else: #field is given
                if field_to_chk.solved:
                    self.get_to_know_value(field_to_chk.digit)
                    for f_u in self.fields: #from the possibilities of all fields in the group.
                        if not f_u.solved:
                            operations += f_u.remove_possibility(field_to_chk.digit)
            
            #And a check whether a field still believes that a value is possible
            #that actually is not:
            for f in self.fields:
                if not f.solved:
                    for p in f.possibilities:
                        if p not in self.unknown_values:
                            operations += f.remove_possibility(p)
        return operations
        
    def naked_siblings(self):
        """This method is the generalization of the naked twins method: If
        there are n fields that can take exclusively only n of the same values,
        than all other fields cannot take these values."""
        
        operations = 0
        
        if self.unsolved:
            for n in range (2,5): #1 is the trivial case adressed in fill_check, higher than 4 is equivalent to cases with lower n.
                for f in self.fields:
                    if f.possibilities.__len__() == n: #Look for fields with exactly n possible values.
                        siblings = [f]
                        for f_other in self.fields: #If the fields differ, but their possibilities are the same, than these are siblings.
                            if (f_other != f) and (f_other.possibilities == f.possibilities):
                                siblings.append(f_other)
                    
                        if siblings.__len__() == n: #check whether it's really n,
                            for f_rest in self.fields:
                                if f_rest not in siblings:
                                    for p in f.possibilities:
                                        operations += f_rest.remove_possibility(p)
                        elif siblings.__len__() > n: #otherwise it's an error.
                            print('Error: Too many siblings ({0}), it should be {1}.'.format(siblings.__len__(),n))                        
                    if not self.unsolved: #then it is solved and the loop can be broken
                        break
        return operations

    def subsets_of_unknown(self):
        """This method returns a powerset of the set of unknown values. The
        powerset is restricted to the sets relevant for the soulmates method,
        which requires only sets of length between 1 and 4 or 3 (depending on
        the max-digit of 9 or 6 respectively)."""
        ps = set()
        for i in range(2**len(self.unknown_values)):
            subset = tuple([x for (j,x) in enumerate(self.unknown_values) if (i >> j) & 1])
            if subset.__len__() > 0: #no empy set
                ps.add(subset)
        return ps
    
    def soulmates(self):
        """If there is a set of n numbers comprised of numbers that can only be
        taken on n fields, than these numbers can be excluded from all other
        fields.
        
        The loop through all subsets can be quite large and nasty. Since the 
        small sets are more interesting, and the big sets should only be used
        later, the first for-loop restricts the length of the subsets."""
        
        operations = 0
        
        for l in range(1, self.unknown_values.__len__() + 1):
            if self.unsolved:
                for subset in self.subsets_of_unknown():
                    
                    check_subset = set() #empty set to check
                    
                    if (subset.__len__() == l) and self.unsolved:
                        value_fields = set() #Here a set is used instead of a list, because a set has unique elements and this is what I need.
                        for f in self.fields: #For each field, this loop checks whether the subset values are part of the field's possible values.
                            for s in subset:
                                if s in f.possibilities:
                                    value_fields.add(f) # If the subset value is in the possible values, the field is added to the set.
                                    check_subset.add(s) #Do not forget to check that all values of subset are actually in the possibilites of the fields remembered.
                        if (value_fields.__len__() == l) and (subset == check_subset): #number of fields equals length of the subset and all subset values are required.
                        #then, the fields with the values in the subset cannot
                        #have any other values. So all other
                        #values can be removed from the possibilities.
                            for f in value_fields:
                                for v in f.possibilities:
                                    if v not in subset:
                                        operations += f.remove_possibility(v)
                    elif not self.unsolved:
                        break
            else:
                break
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
                        self.board[row][col].set_value(initial_numbers[row][col])
            
        print('The puzzle has been set up.')


    def __repr__(self, missing = False, groups = False):
        for rows in range(self.board.__len__()):
            if rows % 3 == 0:
                print('=====================================')
            else:    
                print('-------------------------------------')
            print_str = '|'
            for fields in self.board[rows]:
                if fields.digit != 0:
                    print_str += ' {0} |'.format(fields.digit)
                else:
                    print_str += '   |'
            print(print_str)
        print('=====================================')
        
        if missing:
            row_num = 0
            output_str = '\nThe missing fields have the possibilities:\n\n'
            for row_of_fields in self.board:
                row_num += 1
                for f in row_of_fields:
                    if not f.solved:
                        output_str += '{0} - ( '.format(row_num)
                        for p in f.possibilities:
                            output_str += '{0}, '.format(p)
                        output_str += ')\n'
            print(output_str)
        
        if groups:
            for grp in self.groups:
                grp.__repr__()
                
    
    def check_board_set_up(self):
        """This method checks the setup of all values, after init."""
        for row_of_fields in self.board:
            for f in row_of_fields:
                f.check_for_double_values(method_name = "check-setup")
    
    
    def export_board(self):
        """This method enables to export the sudoku board to another instance
        of the Puzzle class."""
        board_values = list()
        for row_of_fields in self.board:
            row_values = list()
            for f in row_of_fields:
                row_values.append(f.digit)
            board_values.append(row_values)
        return board_values
    
    
    def solve(self):
        """The method solve() initiates the next iteration of the solution of
        the puzzle."""
        
        operations = 0
        
        for grp in self.groups:
            operations += grp.check_known_values()
        
        if operations == 0:
            for grp in self.groups:
                operations += grp.naked_siblings()
                
        if operations == 0:
            for grp in self.groups:
                operations += grp.soulmates()
                
#        if operations == 0:
#            operations += self.brute_force()
            
        return operations

    def check_solved(self):
        """This method checks whether the sudoku has been solved."""
        puzzle_solved = True
        
        for row_of_fields in self.board:
            for fld in row_of_fields:
                if not fld.solved:
                    puzzle_solved = fld.solved
                    break
                    break
        return puzzle_solved
    
    def brute_force(self):
        """Some puzzles are really hard. In this case we just brute force the
        solution."""
        print("--- Und bist Du nicht willig, so brauch' ich Gewalt! ---")
        operations = 0
        
        #First, search for the field with the least possible values:
        f_min = self.board[0][0]
        
        for row_of_fields in self.board:
            for f in row_of_fields:
                if (not f.solved) and (f.possibilities.__len__() < f_min.possibilities.__len__()):
                    f_min = f
        
        #Then make the puzzle and set the new value.
        iter_puzzle = Puzzle()
        #operations += iter_puzzle.solve
        
        return operations
        

def write_down_puzzle():
    """This function ask to fill in a sudoku and is returning the input as list
    of n lists with n elements each. n is either 6 or 9, depending on the
    sudoku at hand."""
    print(('This function allows to fill in a sudoku easily. After your has '
          'been made the puzzle will be solved automatically.\nLife can be so'
          ' easy!\n\nPlease enter the sudoku row by row, pressing the Enter '
          'button at the end of each row. Fill in the digits you know; enter a'
          ' 0 for all fields that are unknown / left blank in your puzzle.'))
    known_values = list()
    value_row = list()
    
    text = input('row #1: ')
    for w in text:
        value_row.append(int(w))
    known_values.append(value_row)
    
    for n in range(2,value_row.__len__()+1):
        value_row = list()
        text = input('row #{0}: '.format(n))
        for w in text:
            value_row.append(int(w))
        known_values.append(value_row)
    
    return known_values


def __main__():
    import puzzle_library
    
    #sudoku_puzzle = write_down_puzzle()
    
#    sudoku_puzzle = [[0,0,1,5,0,9,4,0,2],
#                     [0,9,0,1,0,4,5,0,0],
#                     [3,5,0,0,0,8,0,9,0],
#                     [0,8,3,2,5,1,0,7,0],
#                     [0,2,9,7,0,0,3,4,0],
#                     [5,0,0,9,0,0,0,0,8],
#                     [0,0,0,0,6,0,0,5,0],
#                     [0,0,0,0,9,0,2,0,6],
#                     [0,4,2,8,0,0,0,0,7]]
    
#    sudoku_puzzle = [[1,0,3,8,0,5,7,0,6],
#                     [0,2,0,0,4,0,0,1,0],
#                     [7,0,0,0,0,1,0,0,9],
#                     [8,0,2,0,0,0,0,0,7],
#                     [0,6,0,0,0,0,0,9,0],
#                     [5,0,0,0,0,0,3,0,8],
#                     [6,0,0,4,0,0,0,0,5],
#                     [0,1,0,0,8,0,0,3,0],
#                     [3,0,4,6,0,7,9,0,1]]
 

    #hard:
#    sudoku_puzzle = [[0,7,0,0,4,0,0,5,0],
#                     [1,0,0,3,0,7,9,0,6],
#                     [0,9,0,0,0,0,0,0,0],
#                     [0,4,0,0,0,0,0,1,0],
#                     [7,0,0,0,8,0,0,0,2],
#                     [0,5,0,0,0,0,0,9,0],
#                     [0,0,0,0,0,0,0,2,0],
#                     [3,0,5,2,0,9,0,0,0],
#                     [0,6,0,0,0,1,0,8,0]]
    
    puzzles_solved = 0
    puzzles_unsolved = 0
    
    for puzz_num in range(0,96): #96 possible
        
        print("<<< Puzzle number {0}. >>>".format(puzz_num))
        sudoku_puzzle  = puzzle_library.select_puzzle(puzz_num) #14 is cracked, 4 is not.
        super_die_hard_sudoku = Puzzle(initial_numbers = sudoku_puzzle)
        #super_die_hard_sudoku.__repr__()
        super_die_hard_sudoku.check_board_set_up()
        
        operations = 1
    
        while operations > 0:
            operations = super_die_hard_sudoku.solve()
            print('{0} operations performed'.format(operations))
            #super_die_hard_sudoku.__repr__(missing = False)
#    if not super_die_hard_sudoku.check_solved():
#        super_die_hard_sudoku.brute_force()
    
        if super_die_hard_sudoku.check_solved():
            #print('The puzzle has been solved!')
            puzzles_solved += 1
        else:
            puzzles_unsolved += 1
            #print('The puzzle has not been solved. What a sad day...')
        super_die_hard_sudoku.__repr__(missing = False)
        super_die_hard_sudoku.check_board_set_up()
    print("{0} puzzles have been solved, {1} could not be solved.".format(puzzles_solved, puzzles_unsolved))
#    easy_peasy = Puzzle(initial_numbers = super_die_hard_sudoku.export_board())
#    
#    easy_peasy.__repr__()
    
__main__()


    
    