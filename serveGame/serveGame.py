from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
import threading
import socket
import time

clients = []
ballPos = [0,0]
padelPos = [0,0]
s = ""
ballPosX = '000.00000000000000'
ballPosY = '000.00000000000000'
padelPos1 = '000.00000000000000'

#let's say my co-ordinates are of the format = NNN.FFFFFFFFFFFFFF


def stopServer():
    global s
    while(1):
        flag = int(input())
        if flag == 0:
            s.close()
            s = 0
            break

def getStr(ballPos, padelPos):
    global ballPosX
    global ballPosY
    global padelPos1
    try:
        ballPosX = "%.14f" % ballPos[0]
        ballPosY = "%.14f" % ballPos[1]
        ballPosX = "0"*(18 - len(ballPosX)) + ballPosX
        ballPosY = "0"*(18 - len(ballPosY)) + ballPosY
        padelPos1 = "%.14f" % padelPos
        padelPos1 = "0"*(18 - len(padelPos1)) + padelPos1
        return ballPosX+","+ballPosY+","+padelPos1
    except:
        return ballPosX+","+ballPosY+","+padelPos1



def sendPosition():
    #for now sending position to 2 clients
    global clients
    global ballPos
    global padelPos
    while(1):
        if len(clients) == 2:
            #print("ballPos",ballPos,"padelPos",padelPos)
            data = {clients[0][0] : getStr(ballPos, padelPos[1]), clients[1][0] : getStr(ballPos, padelPos[0])}
            """
            if (len(data[clients[0][0]]) == 56 or len(data[clients[1][0]]) == 56):
                print(data[clients[0][0]])
                print(data[clients[1][0]])
            """
            clients[0][0].send(data[clients[0][0]].encode())
            clients[1][0].send(data[clients[1][0]].encode())
            time.sleep(0.01)
            #print("sent",data)

def receivePadelPos():
    global clients
    global padelPos
    while(1):
        if len(clients) == 2:
            padelPos[0] = float(clients[0][0].recv(18).decode())
            padelPos[1] = float(clients[1][0].recv(18).decode())
        #time.sleep(0.01)

class PongPaddle(Widget):
    score = NumericProperty(0)

    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        global ballPos
        self.pos = Vector(*self.velocity) + self.pos
        ballPos = self.pos
        #print("ballPos",self.pos)


class PongGame(Widget):
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        global padelPos
        self.ball.move()

        # bounce of paddles
        self.player1.bounce_ball(self.ball)
        self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))
        #updating player positions
        self.player1.center_y = padelPos[0]
        self.player2.center_y = padelPos[1]

    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y
        #print("player1Pos",self.player1.center_y)
        #print("player2Pos",self.player2.center_y)


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 30.0)
        return game



host = socket.gethostbyname('0.0.0.0')
port = 8006
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((host,port))
s.listen(5)
#for now we are working with 2 players

threadSendPos = threading.Thread(target = sendPosition, args = ())
threadReceivePadelPos = threading.Thread(target = receivePadelPos, args = ())
threadStopServer = threading.Thread(target = stopServer, args = ())


try:
    c1,addr1 = s.accept()
    print(addr1,"connected to server")
    clients.append([c1,addr1])
    globalClients = clients
except:
    print("Error in connecting to client1")
try:
    c2,addr2 = s.accept()
    print(addr2,"connected to server")
    clients.append([c2,addr2])
    globalClients = clients
except:
    print("Error in connecting to client2")

clients[0][0].send("1".encode())
clients[1][0].send("1".encode())
threadSendPos.start()
threadReceivePadelPos.start()
PongApp().run()

"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
import socket
import threading

ballPos = 0
padelInfo = []
globalClients = []

def sendPos():
    global globalClients
    while(1):
        if len(globalClients) == 2:
            data = {globalClients[0][0]:[ballPos,padelInfo[1]], globalClients[1][0] : [ballPos, padelInfo[0]]}
            globalClients[0][0].send(data[globalClients[0][0]].encode())
            globalClients[1][0].send(data[globalClients[1][0]].encode())

class PongPaddle(Widget):
    score = NumericProperty(0)
    def bounce_ball(self, ball):
        if self.collide_widget(ball):
            vx, vy = ball.velocity
            offset = (ball.center_y - self.center_y) / (self.height / 2)
            bounced = Vector(-1 * vx, vy)
            vel = bounced * 1.1
            ball.velocity = vel.x, vel.y + offset


class PongBall(Widget):
    velocity_x = NumericProperty(0)
    velocity_y = NumericProperty(0)
    velocity = ReferenceListProperty(velocity_x, velocity_y)

    def move(self):
        global ballPos
        self.pos = Vector(*self.velocity) + self.pos
        ballPos = self.pos


class PongGame(Widget):
    host = socket.gethostbyname('0.0.0.0')
    port = 8006
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    clients = []

    def connect_to_client(self):
        global globalClients
        self.s.bind((host,port))
        self.s.listen(5)
        try:
            c,addr = self.s.accept()
            print(addr,"connected to server")
            self.clients.append([c,addr])
            globalClients = self.clients
        except:
            print("Error in connecting to client")
        
        
    ball = ObjectProperty(None)
    player1 = ObjectProperty(None)
    player2 = ObjectProperty(None)

    def serve_ball(self, vel=(4, 0)):
        self.ball.center = self.center
        self.ball.velocity = vel

    def update(self, dt):
        self.ball.move()

        # bounce of paddles
        #self.player1.bounce_ball(self.ball)
        #self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
        if (self.ball.y < self.y) or (self.ball.top > self.top):
            self.ball.velocity_y *= -1

        # went of to a side to score point?
        if self.ball.x < self.x:
            self.player2.score += 1
            self.serve_ball(vel=(4, 0))
        if self.ball.x > self.width:
            self.player1.score += 1
            self.serve_ball(vel=(-4, 0))

    



class PongApp(App):
    def build(self):
        game = PongGame()
        game.connect_to_client()
        game.connect_to_client()
        sendPosThread = threading.Thread(target = sendPos, args = ())
        game.serve_ball()
        sendPosThread.start()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game

if __name__ == '__main__':
    PongApp().run()
    """