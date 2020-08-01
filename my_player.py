import random
import sys
import timeit
import math
import argparse
from copy import deepcopy

def parseInput(n, loc="input.txt"):
    with open(loc, 'r') as f:
        rules = f.readlines()
        piece_type = int(rules[0])
        previous_board = [[int(x) for x in rule.rstrip('\n')] for rule in rules[1:n+1]]
        board = [[int(x) for x in rule.rstrip('\n')] for rule in rules[n+1: 2*n+1]]
        return piece_type, previous_board, board

def output(result, loc="output.txt"):
    opt = ""
    if result == "PASS":
    	opt = "PASS"
    else:
	    opt += str(result[0]) + ',' + str(result[1])
    with open(loc, 'w') as f:
        f.write(opt)

class MYGAME:
    def __init__(self, n):
        self.size = n
        self.died_pieces = []
        self.n_move = 0
        self.max_move = n * n - 1
        self.komi = n/2 

    def init_board(self, n):
        board = [[0 for x in range(n)] for y in range(n)]  
        self.board = board
        self.previous_board = deepcopy(board)

    def board_setup(self, piece_type, previous_board, board):
        for i in range(self.size):
            for j in range(self.size):
                if previous_board[i][j] == piece_type and board[i][j] != piece_type:
                    self.died_pieces.append((i, j))
        self.previous_board = previous_board
        self.board = board

    def board_comparison(self, first_board, second_board):
        for i in range(self.size):
            for j in range(self.size):
                if first_board[i][j] != second_board[i][j]:
                    return False
        return True

    def board_copy(self):
        return deepcopy(self)

    def find_neighbor(self, i, j):
        board = self.board
        neighbors = []
        if i > 0: neighbors.append((i-1, j))
        if i < len(board) - 1: neighbors.append((i+1, j))
        if j > 0: neighbors.append((i, j-1))
        if j < len(board) - 1: neighbors.append((i, j+1))
        return neighbors

    def find_diagonal_neighbor(self, i, j):
        board = self.board
        diagonal_neighbors = []
        if i > 0 and i-1 >= 0 and j+1 <= len(board) - 1: diagonal_neighbors.append((i-1, j+1))
        if i < len(board) - 1 and i+1 <= len(board) - 1 and j+1 <= len(board) - 1: diagonal_neighbors.append((i+1, j+1))
        if j > 0 and i-1 >= 0 and j-1 >= 0: diagonal_neighbors.append((i-1, j-1))
        if j < len(board) - 1 and i+1 <= len(board) - 1 and j-1 >= 0: diagonal_neighbors.append((i+1, j-1))
        return diagonal_neighbors


    def find_neighbor_ally(self, i, j):
        board = self.board
        neighbors = self.find_neighbor(i, j)  
        allies_group = []
        for piece in neighbors:
            if board[piece[0]][piece[1]] == board[i][j]:
                allies_group.append(piece)
        return allies_group

    def ally_depth_first_search(self, i, j):
        stack = [(i, j)]  
        members_ally = []  
        while stack:
            piece = stack.pop()
            members_ally.append(piece)
            allies_neighbor = self.find_neighbor_ally(piece[0], piece[1])
            for ally in allies_neighbor:
                if ally not in stack and ally not in members_ally:
                    stack.append(ally)
        return members_ally

    def detect_liberty(self, i, j):
        board = self.board
        members_ally = self.ally_depth_first_search(i, j)
        for member in members_ally:
            neighbors = self.find_neighbor(member[0], member[1])
            for piece in neighbors:
                if board[piece[0]][piece[1]] == 0:
                    return True
        return False

    def detect_died_pieces(self, piece_type):
        board = self.board
        died_pieces = []
        for i in range(len(board)):
            for j in range(len(board)):
                if board[i][j] == piece_type:
                    if not self.detect_liberty(i, j):
                        died_pieces.append((i,j))
        return died_pieces

    def delete_died_pieces(self, piece_type):
        died_pieces = self.detect_died_pieces(piece_type)
        if not died_pieces: return []
        self.delete_certain_pieces(died_pieces)
        return died_pieces

    def delete_certain_pieces(self, positions):
        board = self.board
        for piece in positions:
            board[piece[0]][piece[1]] = 0
        self.board_updation(board)


    def validity(self, i, j, piece_type):
        board = self.board
        if not (i >= 0 and i < len(board)):
            return False
        if not (j >= 0 and j < len(board)):
            return False
        if board[i][j] != 0:
            return False
        
        test_go = self.board_copy()
        test_board = test_go.board

        test_board[i][j] = piece_type
        test_go.board_updation(test_board)
        if not test_go.detect_liberty(i, j):
            return False
        test_go.delete_died_pieces(3 - piece_type)
        if not test_go.detect_liberty(i, j):
            return False
        else:
            if self.died_pieces and self.board_comparison(self.previous_board, test_go.board):
                return False
        return True
        if self.died_pieces and self.board_comparison(self.previous_board, test_go.board):
            return False
        return True
        
    def board_updation(self, new_board):
        self.board = new_board

    def agressive_mode(self, piece_type, possible_placements):
        sample_go = self.board_copy()
        sample_board = sample_go.board
        opposition_piece_type = 3 - piece_type
        board = self.board
        allies_group = []
        for i in range(sample_go.size):
            for j in range(sample_go.size):
                if board[i][j] == opposition_piece_type:
                    neighbors = self.find_neighbor(i, j)
                    for piece in neighbors:
                        if possible_placements.count((piece[0],piece[1])):
                            sample_board[piece[0]][piece[1]] = piece_type
                            died_pieces = sample_go.detect_died_pieces(opposition_piece_type)
                            if died_pieces:
                                if board[piece[0]][piece[1]] < 10 + len(died_pieces):
                                    board[piece[0]][piece[1]] = 10 + len(died_pieces)
                            sample_board[piece[0]][piece[1]] = 0

    def defensive_mode(self, piece_type, possible_placements):
        sample_go = self.board_copy()
        sample_board = sample_go.board
        opposition_piece_type = 3 - piece_type
        board = self.board
        allies_group = []
        for i in range(sample_go.size):
            for j in range(sample_go.size):
                if sample_board[i][j] == piece_type:
                    neighbors = self.find_neighbor(i, j)
                    for piece in neighbors:
                        if possible_placements.count((piece[0],piece[1])):
                            sample_board[piece[0]][piece[1]] = opposition_piece_type
                            died_pieces = sample_go.detect_died_pieces(piece_type)
                            if died_pieces:
                                if board[piece[0]][piece[1]] < 10 + len(died_pieces):
                                    board[piece[0]][piece[1]] = 10 + len(died_pieces)
                            sample_board[piece[0]][piece[1]] = 0
"""
    def defense_mode(self, piece_type, aggressive_possible_list, possible_placements):
        sample_go = self.board_copy()
        sample_board = sample_go.board
        opposition_piece_type = 3 - piece_type
        board = self.board
        died = 0
        allies_group = []
        for position in aggressive_possible_list:
            if possible_placements.count((position[0], position[1])):
                possible_placements.remove((position[0], position[1]))
            temp = sample_board[position[0]][position[1]]
            sample_board[position[0]][position[1]] = piece_type
            neighbors = sample_go.find_neighbor(position[0], position[1])
            for piece in neighbors:
                temp2 = sample_board[piece[0]][piece[1]]
                sample_board[piece[0]][piece[1]] = opposition_piece_type
                died_pieces = sample_go.detect_died_pieces(piece_type)
                if died_pieces:
                    print('Darsh died pieces', position[0], position[1], piece[0], piece[1], died_pieces)
                    board[position[0]][position[1]] = -1
                    sample_board[piece[0]][piece[1]] = temp2
                    break
                sample_board[piece[0]][piece[1]] = temp2
            sample_board[position[0]][position[1]] = temp
        for position in possible_placements:
            temp = sample_board[position[0]][position[1]]
            sample_board[position[0]][position[1]] = piece_type
            neighbors = sample_go.find_neighbor(position[0], position[1])
            for piece in neighbors:
                temp2 = sample_board[piece[0]][piece[1]]
                sample_board[piece[0]][piece[1]] = opposition_piece_type
                died_pieces = sample_go.detect_died_pieces(piece_type)
                if died_pieces:
                    print('Darsh died pieces', position[0], position[1], piece[0], piece[1], died_pieces)
                    board[position[0]][position[1]] = -1
                    sample_board[piece[0]][piece[1]] = temp2
                    break
                sample_board[piece[0]][piece[1]] = temp2
            sample_board[position[0]][position[1]] = temp
"""

class AggressivePlayer():
    def __init__(self):
        self.type = 'random'

    def get_input(self, go, piece_type):
        liberty_d_go = go.board_copy()
        liberty_board = liberty_d_go.board
        orig_board_go = go.board_copy()
        orig_board = orig_board_go.board
        possible_placements = []
        all_possible_placements = []
        aggressive_possible_list = []
        defensive_possible_list = []
        MAX = 10
        for i in range(go.size):
            for j in range(go.size):
                if go.validity(i, j, piece_type):
                    possible_placements.append((i,j))
                    all_possible_placements.append((i,j))
        go.agressive_mode(piece_type, possible_placements)
        liberty_d_go.defensive_mode(piece_type, possible_placements)

        for i in range(go.size):
            for j in range(go.size):
                if board[i][j] > 10:
                    index_i = i
                    index_j = j
                    MAX = board[i][j]
                    aggressive_possible_list.append((i,j))
                if liberty_board[i][j] > board[i][j]:
                    board[i][j] = liberty_board[i][j]
                    aggressive_possible_list.append((i,j))
        '''
        for i in range(liberty_d_go.size):
            for j in range(liberty_d_go.size):
                if liberty_board[i][j] == -1:
                    if possible_placements.count((i,j)):
                        possible_placements.remove((i,j))
                    if aggressive_possible_list.count((i,j)):
                        aggressive_possible_list.remove((i,j))
                    defensive_possible_list.append((i,j))
                print(liberty_board[i][j]),
            print
        '''
        if not all_possible_placements:
            return "PASS"
        else:
            if len(aggressive_possible_list):
                current_max = 0
                maxlist = []
                for piece in aggressive_possible_list:
                    if board[piece[0]][piece[1]] > current_max:
                        current_max = board[piece[0]][piece[1]]
                for piece in aggressive_possible_list:
                    if  board[piece[0]][piece[1]] == current_max:
                        maxlist.append((piece[0],piece[1]))
                max_neighbors = 0
                for piece in maxlist:
                    neighbors = orig_board_go.find_neighbor(piece[0], piece[1])
                    if len(neighbors) > max_neighbors:
                        max_neighbors = len(neighbors)
                        ouput_i = piece[0]
                        output_j = piece[1]
                return ouput_i,output_j
            if orig_board[2][2] == 0:
                neighbors = orig_board_go.find_neighbor(2, 2)
                if len(neighbors) == 4:
                    return 2,2
            if len(possible_placements):
                max_neighbors = 0
                min_diagonal_neighbors = 5
                max_neighbors_list = []
                for piece in possible_placements:
                    neighbors = orig_board_go.find_neighbor(piece[0], piece[1])
                    if len(neighbors) > max_neighbors:
                        max_neighbors = len(neighbors)
                        ouput_i = piece[0]
                        output_j = piece[1]
                if piece_type == 1:
                    for piece in possible_placements:
                        neighbors = orig_board_go.find_neighbor(piece[0], piece[1])
                        if len(neighbors) == max_neighbors:
                            max_neighbors_list.append((piece[0],piece[1]))
                    for piece in max_neighbors_list:
                        diagonal_neighbors = orig_board_go.find_diagonal_neighbor(piece[0], piece[1])
                        if len(diagonal_neighbors) < min_diagonal_neighbors:
                            min_diagonal_neighbors = len(diagonal_neighbors)
                            ouput_i = piece[0]
                            output_j = piece[1]
                return ouput_i,output_j
            if len(all_possible_placements):
                max_neighbors = 0
                for piece in all_possible_placements:
                    neighbors = orig_board_go.find_neighbor(piece[0], piece[1])
                    if len(neighbors) > max_neighbors:
                        max_neighbors = len(neighbors)
                        ouput_i = piece[0]
                        output_j = piece[1]
                return ouput_i,output_j

if __name__ == "__main__":
    N = 5
    piece_type, previous_board, board = parseInput(N)
    go = MYGAME(N)
    go.board_setup(piece_type, previous_board, board)
    player = AggressivePlayer()
    action = player.get_input(go, piece_type)
    output(action)
