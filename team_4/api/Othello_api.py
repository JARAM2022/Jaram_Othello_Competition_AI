from random import shuffle
import socketio
import math
from ai.alpbeta import AI,AiBoard
import orjson
import time
PLAYER = {
    1 : 'W',
    0 : 'B',
    'W' : 1,
    'B' : 0
}


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

        self.ai = AI()
        with open("./c.json", 'r') as f:
            self.ai.cache = orjson.loads(f.read())
        print(f"{len(self.ai.cache)}")

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
            for i,name in enumerate(self.room_list):
                print(i,name)
            print("your id : ",self.socket_id,"\nroom list\n","\ncommand list\nno input: pass(update)\n1 : update room list\n2 : make room\n3 : join room (input \'3 room_index\')\n4 : fight test ai\n")
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
        # code here!!!!!
        placeable = self.game_info['placeable'][0]
        player = self.game_info['placeable'][3]

        self.ai.setup(player)

        #액션 결정
        action = self.ai.get_action(self.game_info['board'],placeable)

        self.put_stone(placeable.index([action[0],action[1]]))
        # self.put_stone(0)
        return






