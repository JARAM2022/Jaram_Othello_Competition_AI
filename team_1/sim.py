 
def isValid(board,tile,xstart,ystart):
#tile 값      0: 흑돌       1: 백돌
    if (board[xstart][ystart] != -1 or not isOnBoard(xstart, ystart)):    
        # print("occupied")
        return 0
    
    board[xstart][ystart] = tile

    if tile == 0:
        otherTile = 1
    else:
        otherTile = 0

    tilesToFlip = []
    for xdirection, ydirection in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
        x,y = xstart, ystart
        x += xdirection
        y += ydirection

        if isOnBoard(x, y) and board[x][y] == otherTile:
            x += xdirection
            y += ydirection

            if not isOnBoard(x,y):
                continue

            while board[x][y] == otherTile:
                x += xdirection
                y += ydirection
                
                if not isOnBoard(x,y):
                    break

            if not isOnBoard(x,y):
                continue

            if board[x][y] == tile:

                while True:
                    x-=xdirection
                    y-=ydirection
                    if x == xstart and y == ystart:
                        break
                    tilesToFlip.append([x,y])


    board[xstart][ystart] = -1
    if len(tilesToFlip) == 0:
        # print("no flip").
        
        return 0
    # print("ok")
    return [xstart,ystart,tilesToFlip]


def isOnBoard(x,y):
    # coordinates board limit
    return x>=0 and x<= 7 and y>=0 and y<=7

def getvalidcoordination(board,player):
    val = []
    for x in range(0,8):
        for y in range(0,8):
            temp = isValid(board,player,x,y)
        # print(type(temp))
            if temp == 0:
                continue
            val.append(temp)
    return val


def ai_stone(placeable,board):
    possible_position = getvalidcoordination(board,0)
    max = -1
    num = 0
    for i in range(len(possible_position)):
        check=0
        xpos,ypos = possible_position[i][0],possible_position[i][1]
        if([xpos,ypos] == ([1,0]or[0,1]or[1,1]or[6,0]or[7,0]or[6,1]or[6,7]or[0,6]or[1,6]or[1,7]or[6,6]or[7,6]or[6,7])):
           continue
        
        elif([xpos, ypos] == ([0,0]or[0,7]or[7,0]or[7,7])):
           return [xpos,ypos]
        
        elif (max <= len(possible_position[i][2])):
            max = len(possible_position[i][2])
            num = i
            check=1
    if(check==0):
        for i in range(len(possible_position)):
            if (max <= len(possible_position[i][2])):
                max = len(possible_position[i][2])
                num = i
            
    xpos,ypos = possible_position[i][0],possible_position[i][1]
    return [xpos,ypos]
