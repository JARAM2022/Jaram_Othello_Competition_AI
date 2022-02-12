from __future__ import absolute_import
from copy import deepcopy
import random

import socketio

class Othello_api:
    sio = socketio.Client()
    def __init__(self, server = 'http://othello-api.jaram.net/'):
        self.server = server
        self.socket_id = ''
        # 0 : lobby / 1: in game
        self.status = 0
        self.room_list = []
        self.room_info = []
        self.game_info = []
        
        self.count=0
        self.canFin=True
        self.__directions = [(1,1),(1,0),(1,-1),(0,-1),(-1,-1),(-1,0),(-1,1),(0,1)]

        self.square_weights = [
            [120, -20,  20,   20,   20,  20, -20, 120],
            [-20, -10,  -5,  -5,  -5,  -5, -10, -20],
            [20,  -5,  15,   3,   3,  15,  -5,  20],
            [20,  -5,   3,   3,   3,   3,  -5,   20],
            [20,  -5,   3,   3,   3,   3,  -5,   20],
            [20,  -5,  15,   3,   3,  15,  -5,  20],
            [-20, -10,  -5,  -5,  -5,  -5, -10, -20],
            [120, -20,  20,   20,   20,  20, -20, 120]
        ]
        self._corner = [[0,0],[7,0],[7,7],[0,7]]
        self._csquare = [
            [0,1],[1,0],[1,1],
            [7,6],[6,7],[6,6],
            [6,0],[7,1],[6,1],
            [0,6],[1,6],[1,7]
        ]
    
    def setup(self):
        self.call_backs()
        self.sio.connect(self.server)
        
    def call_backs(self):
        @self.sio.event
        def connect():
            print("I'm connected!")
            self.lobby_loop()

        @self.sio.event
        def connect_error(data):
            print("The connection failed!")

        @self.sio.event
        def disconnect():
            print("I'm disconnected!")

        @self.sio.on('command')
        def handle_command(data):
            # print("command")
            if(data['command'] == 'update_room'):
                self.update_room(data['room_list'])
                return
            elif(data['command'] == 'room_info'):
                self.handle_room_info(data['room_info'], data['game_info'])
                self.status = 1
                return
            elif((data['command'] == 'send_id')):
                self.set_socket_id(data['socket_id'])
                return
            print(data)

        @self.sio.on('*')
        def catch_all(event, data):
            print("event : ",event," data : ",data)
            pass


    def set_socket_id(self, id):
        self.socket_id = id

    def update_room(self, room_list_server):
        # print("Room List")
        self.room_list = room_list_server
    
    def game_end(self):
        score = self.game_info['placeable'][1]
        if(score[0] > score[1]):
            if(self.game_info['player'][0] == self.socket_id):
                print("You WIN")
            else:
                print("You LOSE")
        elif(score[1] > score[0]):
            if(self.game_info['player'][1] == self.socket_id):
                print("You WIN")
            else:
                print("You LOSE")
        else:
            print("Draw")
        print("Score ",score)
        return

    def handle_room_info(self, room_info, game_info):
        self.room_info = room_info
        self.game_info = game_info
        # print(self.room_info)
        # print(self.game_info)
        if(len(self.game_info['placeable']) != 0):
            if(self.game_info['placeable'][3] == -1):
                self.game_end()
                return
            elif(self.game_info['turn'] == self.socket_id):
                self.ai_put_stone()
                return

    def get_socket_id(self):
        self.sio.emit('get_id')

    def get_room(self):
        self.sio.emit('get_room')

    def join_room(self,room_id):
        self.sio.emit("join_room", { 'room_id' : room_id })

    def ready(self):
        self.sio.emit("ready")

    def create_room(self):
        self.sio.emit("create_room")

    def print_board(self,board):
        for i in range(8):
            for j in range(8):
                print(board[i][j]+1," ",end = '')
            print()
        print()

    def mk_test_ai_room(self):
        self.sio.emit("join_ai")

    def put_stone(self, index):
        if(self.game_info['turn'] == self.socket_id):
            print("put stone ",self.game_info['placeable'][0][index])
            self.sio.emit("put_stone", { 'index' : index })




    def game_loop(self):
        while(self.status):
            print("room id ",self.room_info['room_id'])
            if (self.room_info['room_status'] == "waiting"):
                for player_info in self.room_info['player']:
                    if(player_info[1] == 0):
                        print("player ",player_info[0]," is not ready", end = '')
                    else:
                        print("player ",player_info[0]," is ready", end = '')
                    if(self.socket_id == player_info[0]):
                        print(" (you)")
                    else:
                        print()
                print("command list\nno input: pass(update)\n1 : ready")
                command = input()
                if (len(command.split()) == 0):
                    continue
                elif command.split()[0] == '1':
                    self.ready()
                print()
            elif (self.room_info['room_status'] == "playing"):
                for i in range(2):
                    print(self.game_info['player'][i],"[stone ",i+1,"]", end = '')
                    if(self.socket_id == self.game_info['player'][i]):
                        print(" (you)", end='')
                    print(" has ",self.game_info['placeable'][1][i]," stone onboard")
                self.print_board(self.game_info['board'])
                if(self.game_info['placeable'][3] != -1):
                    if(self.game_info['turn'] == self.socket_id):
                        print("your turn!!!!\n you can place here")
                        for i in range(len(self.game_info['placeable'][0])):
                            print(i," :",self.game_info['placeable'][0][i])
                        print("press index to put")
                
                command = input()
                if (len(command.split()) == 0):
                    continue
                elif (int(command) < len(self.game_info['placeable'][0])):
                    self.put_stone(int(command))

        
        self.lobby_loop()
        return


    def lobby_loop(self):
        while(not self.status):
            print("your id : ",self.socket_id,"\nroom list\n",self.room_list,"\ncommand list\nno input: pass(update)\n1 : update room list\n2 : make room\n3 : join room (input \'3 room_index\')\n4 : fight test ai\n")
            command = input()
            if (len(command.split()) == 0):
                continue
            elif command.split()[0] == '1':
                self.get_room()
            elif command.split()[0] == '2':
                self.create_room()
            elif command.split()[0] == '3':
                if (len(command.split()) > 1):
                    self.join_room(self.room_list[int(command.split()[1])]['room_id'])
                else:
                    print("\n\ninput room index!!!!!!!")
            elif command.split()[0] == '4':
                self.mk_test_ai_room()
            else:
                pass
            print()

        self.game_loop()
        return

    def run(self):
        self.setup()
        self.get_socket_id()
    
    def ai_put_stone(self):
        print("----------------------------------")
        print(self.count)
        self.count+=1
        placeable=self.game_info['placeable'][0]
        self.print_board(self.game_info['board'])
        print("placeable : ",placeable)
        color=0
        if self.game_info['turn']==self.game_info['player'][1]:
            color=1
        
        # code here!!!!!
        temp=self.isCorner(placeable)
        if temp!=-1:
            print("is corner!")
            self.put_stone(temp)
            return
        target=0
        res=-1
        res=self.do_minimax_with_alpha_beta(self.game_info['board'],color,30,-100000,100000)
        for i in range(0,len(placeable)):
            if (placeable[i][0],placeable[i][1])==res[1]:
                break
            else:
                target+=1

        if target<len(placeable):
            if placeable[target] in self._csquare:
                print(res,"is not good place")
                cnt=0
                while placeable[target] in self._csquare:
                    target=(target+1)%len(placeable)
                    cnt+=1
                    if cnt>64:
                        break
                self.put_stone(target)
            else :    
                print(res,target)
                self.put_stone(target)
        else:
            print(res,"random")
            self.put_stone(random.randrange(0,len(placeable)))
        return

    def isCorner(self, placeable):
        for i in range(0,len(placeable)):
            if placeable[i] in self._corner:
                return i
        return -1
    def isCornerGet(self, square):
        for i in range(0,len(self._csquare)):
            print(square)
            if square==self._csquare[i]:
                if i<3:
                    return [0,0]
                if i<6:
                    return [7,7]
                if i<9:
                    return [7,0]
                if i<12:
                    return [0,7]

    #Evalutes the weighted score of the board for a color
    def evaluate(self, board, color): #나는 0 상대는 1
        total = 0
        count=[0,0]
        for x in range(0,len(board)):
            for y in range(0,len(board[x])):
                square=board[x][y]
                if square==color:
                    count[color]+=1
                    total+=self.square_weights[x][y]
                elif square!=-1:
                    total-=self.square_weights[x][y]
        #Return the total weighted score    
        return total

    def get_legal_moves(self, board, color):
        """ Return all the legal moves for the given color.
        (1 for white, -1 for black) """
        # Store the legal moves
        moves = []
        # Get all the squares with pieces of the given color.
        for x in range(0,len(board)):
            for y in range(0,len(board[x])):
                square=board[x][y]
                if square==color:
                    newmoves=self.get_moves_for_square(board,(x,y))
                    if newmoves!=None:
                        moves+=newmoves
        res=[]
        for i in moves:
            if i not in res:
                res.append(i)
        #print(res)
        return res

    def get_moves_for_square(self, board, square):
        """ Return all the legal moves that use the given square as a base 
        square. That is, if the given square is (3,4) and it contains a black 
        piece, and (3,5) and (3,6) contain white pieces, and (3,7) is empty, 
        one of the returned moves is (3,7) because everything from there to 
        (3,4) can be flipped. """
        (x,y) = square
        # Determine the color of the piece
        color = board[x][y]

        # Skip empty source squares
        if color==-1: 
            return None

        # Search all possible directions
        moves = []
        for direction in self.__directions:
            move = self._discover_move(board, square, direction)
            if move != None:
                moves.append(move)
        # Return the generated list of moves
        return moves

    def _discover_move(self, board, origin, direction):
        """ Return the endpoint of a legal move, starting at the given origin,
        and moving in the given direction. """
        x,y = origin
        color = board[x][y]
        other = 0
        current=(x,y)
        if color==0:
            other=1
        flips = []
        while 0<=current[0] and current[0]<8 and 0<=current[1] and current[1]<8 :
            current=(current[0]+direction[0],current[1]+direction[1])
            x=current[0]
            y=current[1]
            if 0<=current[0] and current[0]<8 and 0<=current[1] and current[1]<8:
                if board[x][y] == -1 and len(flips)>0:
                    return (x,y)
                elif (board[x][y] == color or (board[x][y] == -1 and len(flips)<=0)):
                    return None 
                elif board[x][y] == other:
                    flips.append((x,y))
            else :
                break
        return None

    def execute_move(self, board, move, color):
        """ Perform the given move on the board, and flips pieces as necessary.
        color gives the color of the piece to play (1 for white, -1 for black) """
        # Start at the new piece's square and follow it on all 8 directions
        # to look for pieces allowing flipping

        # Add the piece to the empty square
        flips = (flip for direction in self.__directions
                      for flip in self._get_flips(board, move, direction, color))

        for x,y in flips:
            board[x][y] = color
        return board

    def _get_flips(self, board, origin, direction, color):
        """ Get the list of flips for a vertex and a direction to use within 
        the execute_move function. """
        # Initialize variable
        flips = [origin]
        other = 0
        current=(origin[0],origin[1])
        if color==0:
            other=1

        while 0<=current[0] and current[0]<8 and 0<=current[1] and current[1]<8 :
            current=(current[0]+direction[0],current[1]+direction[1])
            x=current[0]
            y=current[1]
            if 0<=current[0] and current[0]<8 and 0<=current[1] and current[1]<8:
                if board[x][y] ==other:
                    flips.append((x, y))
                elif (board[x][y] == -1 or (board[x][y] == color and len(flips) == 1)):
                    break
                elif board[x][y] == color and len(flips) > 1:
                    return flips
            else :
                break
        return []

    def calculate_distance(self,put,current):
        return abs(put[0]-current[0])+abs(put[1]-current[1])

    #Minimax with alpha-beta, based on lecture slides
    def do_minimax_with_alpha_beta(self, board, color, depth, my_best, opp_best):
        if depth == 0:
            return (self.evaluate(board,color), None)

        move_list = self.get_legal_moves(board,color)

        #This was for the statistics section. Commented it out now
        #self.branches.append(len(move_list))

        if not move_list:
            return (self.evaluate(board,color),None)

        best_score = my_best
        best_move = None
        if (self.game_info['turn']==self.game_info['player'][0] and color==0) or (self.game_info['turn']==self.game_info['player'][1] and color==1):
            best_score = my_best
            best_move = None
            for move in move_list:
                new_board = self.execute_move(board, move, color)
                try_tuple = self.do_minimax_with_alpha_beta(new_board, (color+1)%2, depth-1, best_score,opp_best)
                try_score = try_tuple[0]
                if self.count<20:
                    try_score+=10*(64-len(self.get_legal_moves(new_board,(color+1)%2)))

                if try_score > best_score:
                    best_score = try_score
                    best_move = move
                if opp_best<=best_score:
                    break
        else:
            best_score = opp_best
            best_move = None
            for move in move_list:
                new_board = self.execute_move(board, move, color)
                try_tuple = self.do_minimax_with_alpha_beta(new_board, (color+1)%2, depth-1, my_best, best_score)
                try_score = try_tuple[0]
                if self.count<20:
                    try_score+=10*(64-len(self.get_legal_moves(new_board,(color+1)%2)))

                if try_score < best_score:
                    best_score = try_score
                    best_move = move
                if opp_best<=best_score:
                    break
        return (best_score, best_move)
        



api = Othello_api()
api.run()








