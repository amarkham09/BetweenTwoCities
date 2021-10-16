from random import sample
import time
import re
from os.path import exists
import json


memoization_dict = {tuple(['ssss']): 16,
                            tuple(['sss']): 10,
                            tuple(['ss']): 5,
                            tuple(['s']): 2,
                            tuple(['s.s']): 4,
                            tuple(['s..s']): 4,
                            tuple(['ss.s']): 7,
                            tuple(['s.ss']): 7,
                            tuple([]): 0
                        }


def random_board():
    """Generates a new random 4x4 list by sampling a list containing the following tiles:
                    s:          shopping districts
                    f:          factories
                    1/2/3/4:    entertainment venues (pub, restaurant, music, hotel)
                    o:          office
                    p:          park
                    h:          housing
                """
    all_tiles = (['s'] * 16) + (['f'] * 16) + (['1', '2', '3', '4'] * 7) + (['o'] * 16) + (['p'] * 16) + (
            ['h'] * 16)
    random_sample = sample(all_tiles, 16)
    return [''.join(random_sample[i:i + 4]) for i in range(0, 16, 4)]  # stacks the board


def checkNonNegIndex(num):
    """If the passed number is negative, returns None. Else, the number is returned.
    This deliberately raises an index error when the value None is passed as the index of the board."""
    if num < 0:
        return None
    else:
        return num


def substr_in_list(lst, string):
    if string in lst:
        return True
    for element in lst:
        if string in element:
            return True
    return False


def evaluate_node(sub_board, run_length):
    # This does not correctly evaluate boards where removing a sequence of multiple runs of 3 is preferable to removing
    # a single run of 4.
    # Example A: ['sss.', '.sss', '.s..', 'sss.'] scores 29 for 4,2,1,1,1,1 or 31 for 3,3,3,1
    # Example B: ['.sss', '..s.', '..s.', '.sss'] scores 24 for 4,1,1,1,1 or 25 for 3,3,2
    """Passed list of strings. NB: parent function must have trimmed the input"""

    if (tuple_board := tuple(sub_board)) in memoization_dict:  # if this sub_board calculation cached
        return memoization_dict[tuple_board]
    transp_board = transpose(sub_board)
    if (transp_tuple_board := tuple(transp_board)) in memoization_dict:  # if this sub_board calculation cached
        return memoization_dict[transp_tuple_board]

    # are there any remaining shopping districts on the board? if not, return 0
    while (searches := [substr_in_list(sub_board, search_str := 's' * run_length),
                        substr_in_list(transp_board, search_str)]) == [False, False]:
        run_length -= 1
        if run_length == 0:  # Should never run as a blank grid will be trimmed to the empty list and scored as zero.
            raise Exception("Auto-exiting from infinite loop")

    # There is at least one run of length == run_length
    # check each possible removal, and call recursion on each one after trimming whitespace
    branch_scores = []
    # check horizontal, then vertical
    if n := searches.index(True) == 1:
        sub_board = transpose(sub_board)
    for dimension in range(n, 2):
        for i in range(len(sub_board)):
            if sub_board[i].count(
                    search_string := ('s' * run_length)) > 0:
                temp_board = sub_board.copy()  # create temporary copy of board for testing
                temp_board[i] = temp_board[i].replace(search_string, '.' * run_length)
                branch_scores.append(memoization_dict[tuple([search_string])] + evaluate_node(trim_board(temp_board),
                                                                                              run_length))  # call function recursively
        sub_board = transpose(sub_board)
    memoization_dict[tuple_board] = (max_node := max(branch_scores))
    return max_node


def trim_board(grid):
    trim_matches = ['....', '...', '..', '.']
    for dimension in range(2):  # trim, transpose, trim, transpose
        if not grid:  # if empty list passed
            return []
        while grid and grid[0] in trim_matches:
            grid = grid[1:]  # trim top
        if not grid:  # if empty list passed
            return []
        while grid[-1] in trim_matches:
            grid = grid[:-1]
        if len(grid) > 2:  # is there a middle row to consider?
            i = 1  # set index to middle row
            while i < len(grid) - 1:  # while considering middle rows
                # check whether it is safe to delete this row (does it preserve runs correctly)
                safe_to_delete = not any([grid[i - 1][j] == 's' and grid[i + 1][j] == 's' for j in range(len(grid[0]))])
                if grid[i] in trim_matches and safe_to_delete:
                    # safe to delete unneeded middle row. i not incremented as row deletion instead
                    grid = grid[:i] + grid[i + 1:]
                else:
                    # not safe to delete middle row. i incremented
                    i += 1
        grid = transpose(grid)
    return grid  # transposed twice


def transpose(str_list):
    """Transposes (exchanges columns and rows) of the board layout."""
    # takes list of strings of dimensions n x m
    if (n := len(str_list)) == 0:
        return []
    if (m := len(str_list[0])) == 1 and n == m:
        return str_list
    transposed_board = []
    for j in range(m):
        transposed_board.append('')
        for i in range(n):
            transposed_board[j] += str_list[i][j]
    return transposed_board


class Board:
    def __init__(self, board):
        self._as_list = board
        self.__as_str = ''.join(self.as_list)

    def to_dict(self):
        dump = {
            '__board__': True,
            'board': self.as_list,
            'points': self.points,
            'sub_totals':
                {'entertainment': self.entertainment,
                 'factories': self.factories,
                 'houses': self.houses,
                 'offices': self.offices,
                 'parks': self.parks,
                 'shopping': self.shopping}
        }
        return dump

    @property
    def as_list(self):
        return self._as_list

    @property
    def entertainment(self):
        """Determines the number of points scored for entertainment venues.
            Points are scored for the number of different kinds of venue present.
                    N  Points
                    1       2
                    2       4
                    3       9
                    4       17
            """
        num = 0
        if "1" in self.__as_str:
            num += 1
        if "2" in self.__as_str:
            num += 1
        if "3" in self.__as_str:
            num += 1
        if "4" in self.__as_str:
            num += 1
        point_dict = {0: 0, 1: 1, 2: 4, 3: 9, 4: 17}
        return point_dict[num]

    @property
    def factories(self):
        """Determines the number of points scored for factories.
            In a normal game of Between Two Cities, the player with most factories scores 4 points per factory.
            Second and third place score 3 and 2 points per factory respectively.
            Since this code only attempts to determine the maximum score of a given board, the maximum multiplier is used.
            """
        return self.__as_str.count("f") * 4

    @property
    def houses(self):
        """Determines the number of points scored for houses.
        Each house has value equal to the number of types of districts on the board (1-5).
        However, a house next to a factory only scores one point."""
        num = 0
        points = 0
        # TODO: add pattern matching
        if "s" in self.__as_str:
            num += 1
        if "f" in self.__as_str:
            num += 1
        if "1" in self.__as_str or "2" in self.__as_str or "3" in self.__as_str or "4" in self.__as_str:
            num += 1
        if "o" in self.__as_str:
            num += 1
        if "p" in self.__as_str:
            num += 1
        for i in range(4):
            for j in range(4):
                if self.as_list[i][j] == 'h':
                    if 'f' in self.neighbours(i, j):
                        points += 1
                    else:
                        points += num
        return points

    def neighbours(self, i, j):
        """Return a list of length 2-4 containing the tiles
        which share an edge with the specified tile with coordinates i, j. """
        nearest = []
        for x_offset, y_offset in [(0, -1), (0, 1), (1, 0), (-1, 0)]:
            try:
                nearest.append(self.as_list[checkNonNegIndex(i + x_offset)][checkNonNegIndex(j + y_offset)])
            except IndexError:
                continue
            except TypeError:
                continue
        return nearest

    @property
    def offices(self):
        """Determines the number of points scored for offices.
            Points are scored for the number of offices present:
                    Number  Points
                    1       1
                    2       3
                    3       6
                    4       10
                    5       15
                    6+       21
            There is an additional point scored for each office that shares an edge with an entertainment venue."""
        point_dict = [0, 1, 3, 6, 10, 15, 21]
        if (num_offices := self.__as_str.count('o')) > 6:
            points = 21
        else:
            points = point_dict[num_offices]
        for i in range(4):
            for j in range(4):
                if self.as_list[i][j] == 'o':
                    nearest = self.neighbours(i, j)
                    if '1' in nearest or '2' in nearest or '3' in nearest or '4' in nearest:
                        points += 1
        return points

    @property
    def parks(self):
        """Determines the number of points scored for parks.
            Each contiguous park scores the following number of points depending on their size:
                    Size  Points
                    1       2
                    2       8
                    3       12
                    4       13
                    5       14
            """
        point_array = [0, 2, 8, 12, 13, 14, 14, 14, 14, 14, 14, 14, 14, 14, 14]
        park_coords = []
        parks_sorted = []
        for i in range(4):
            for j in range(4):
                if self.as_list[i][j] == 'p':
                    park_coords.append(tuple([i, j]))
        while len(park_coords) > 0:
            x, y = park_coords.pop(0)
            if len(parks_sorted) == 0:
                parks_sorted.append([(x, y)])
            else:
                borders_bool = []
                for block_no, park_block in enumerate(parks_sorted):
                    borders_bool.append(False)
                    for i, j in park_block:
                        if abs(x - i) + abs(y - j) == 1:
                            borders_bool[block_no] = True
                if (num_true := borders_bool.count(True)) == 1:
                    parks_sorted[borders_bool.index(True)].append((x, y))
                elif num_true > 1:
                    new_parks_sorted = []
                    i_mega_park = None
                    for block_no, park_block in enumerate(parks_sorted):
                        if borders_bool[block_no]:  # If it is bordering
                            if i_mega_park is None:
                                i_mega_park = block_no
                                new_parks_sorted.append(park_block)
                            else:
                                new_parks_sorted[i_mega_park] += park_block
                                new_parks_sorted[i_mega_park] += [(x, y)]
                                parks_sorted = new_parks_sorted
                        else:
                            new_parks_sorted.append(park_block)
                            parks_sorted = new_parks_sorted
                else:
                    parks_sorted.append([(x, y)])

        return sum([point_array[len(block)] for block in parks_sorted])

    @property
    def points(self):
        return sum([self.entertainment, self.factories, self.houses, self.offices, self.parks, self.shopping])

    @property
    def shopping(self):
        board = [re.sub(r'[foph1-4]', '.', ''.join(row)) for row in self.as_list]
        return evaluate_node(trim_board(board), 4)

    def __str__(self):
        return '\n'.join([' '.join(char) for char in self.as_list])


def as_board(dct):
    if '__board__' in dct:
        return Board(dct['board'])
    return dct


if __name__ == '__main__':
    if exists('best_boards.json'):
        with open('best_boards.json', 'r') as read_file:
            best_boards = json.load(read_file, object_hook=as_board)
            best_score = best_boards[0].points
    else:
        best_boards = []
        best_score = 0
    x = 10000000 # 20 minutes
    length = len(memoization_dict)
    tic = time.perf_counter()
    toc = tic
    try:
        for i in range(x + 1):
            if i >= (n := 10000) and i % n == 0:
                print(f'{i} solutions tested in another {(0 - toc + (toc := time.perf_counter())):.4f} seconds with {0 - length + (length := len(memoization_dict))} entries added to dict')
            if (new_score := (new_board := Board(random_board())).points) >= best_score:
                if new_score > best_score:
                    best_boards = []
                    best_score = new_score
                    print(f'New best score: {best_score}')
                else:
                    print(f'Another board found with best score: {best_score}')
                best_boards.append(new_board)

    except KeyboardInterrupt:
        i -= 1

    print(f'\nCalculation took {time.perf_counter() - tic} seconds')
    print(f'Tested {i} solutions')
    print(f'Optimal score: {best_score}')
    print(f'Number of solutions for this score: {len(best_boards)}')
    print(f'Best board:\n{best_boards[0]}')
    print(f'{len(memoization_dict)} entries in dict')
    print(memoization_dict)

    with open('best_boards.json', 'w') as f:
        f.write(json.dumps([b.to_dict() for b in best_boards], sort_keys=True, indent=4))
