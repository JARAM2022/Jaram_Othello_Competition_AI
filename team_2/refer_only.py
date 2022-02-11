# 참고용 코드
class Node:
    def __init__(self, depth, playerNum, stickRemaining, value):
        # 깊이는 루트가 뭐 대충 10이상이고 끝 차일드가 0
        self.depth = depth
        self.playerNum = playerNum
        self.stickRemaining = stickRemaining
        self.value = value
        self.children = []
        self.CreateChildren()

    def CreateChildren(self):
        if self.depth >= 0:
            for i in range(1, 3):
                v = self.stickRemaining-i
                self.children.append(
                    Node(self.depth-1, -self.playerNum, v, self.RealVal(v)))

    def RealVal(self, value):
        if value == 0:
            return maxsize*self.playerNum
        elif value < 0:
            return maxsize * -self.playerNum
        return 0


def MinMax(node, depth, playerNum):
    # 마지막 차일드이거나 이길확률 크면 밸류 리턴
    if (depth == 0) or (abs(node.value) == maxsize):
        return node.value

    # 일단 최소값으로 설정
    bestValue = maxsize * -playerNum
    for i in range(len(node.children)):
        child = node.children[i]
        # 바닥까지
        val = MinMax(child, depth-1, -playerNum)
        if (abs(maxsize*playerNum-val) < abs(maxsize*playerNum-bestValue)):
            bestValue = val
    return bestValue

    # max flip values


def createChildren(self, player):
    if self.depth < 0:
        return
    maxval = 0
    playerNum = 0
    newBoard = copyBoard(self.board)
    # print(newBoard)
    for legal in legalPlaySpots(newBoard, player):
        newBoard = copyBoard(self.board)

        if self.playerNum == 1:
            playerNum = 2
        elif self.playerNum == 2:
            playerNum = 1

        node = OthelloNode(newBoard, self.depth-1, playerNum)
        node.flip(legal[0], legal[1], player)

        # 최대로 뒤집는 수 알고리즘
        if node.countStones(player) > maxval:
            self.children = [node]
            maxval = node.countStones(player)
        elif node.countStones(player) == maxval:
            self.children.append(node)
        else:
            pass
        # print(maxval)
    for n in self.children:
        n.printBoard()
