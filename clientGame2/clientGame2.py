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


ballPos = [0,0]
padelPos = [0,0]
s = ""

def sendPadelPosition():
    #sending my padel position
    global ballPos
    global padelPos
    while(1):
        tempPadelPos = "%.14f" % padelPos[1]
        tempPadelPos = "0"*(18 - len(tempPadelPos)) + tempPadelPos
        s.send(tempPadelPos.encode())
        #print("sent",tempPadelPos)
        time.sleep(0.01)



def receivePos():
    global padelPos
    global ballPos
    while(1):
        #print("in r")
        dataReceived = s.recv(56).decode()
        #print("received", dataReceived)
        ballPosX,ballPosY,padelPosStr = dataReceived[:56].split(',')
        try:
            ballPos = [float(ballPosX), float(ballPosY)]
            #ballPos = dataReceived[0]
            #for client1 i am player 0
            #print(padelPosStr)
            padelPos[0] = float(padelPosStr[:18])
            #print(ballPos,padelPos)
        except:
            1==1
        time.sleep(0.01)


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
        #updating ball pos from server
        global ballPos
        self.pos = ballPos
        """
        self.pos = Vector(*self.velocity) + self.pos
        ballPos = self.pos
        """
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
        #updating 2nd player positions
        self.player1.center_y = padelPos[0]
        #updating my player position to the variable that i send to the server
        padelPos[1] = self.player2.center_y

    def on_touch_move(self, touch):
        #you can only move player 2 by clicking on it
        """
        if touch.x < self.width / 3:
            self.player2.center_y = touch.y
        
        """
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y
        #print("player1Pos",self.player1.center_y)
        #print("player2Pos",self.player2.center_y)


class PongApp(App):
    def build(self):
        game = PongGame()
        game.serve_ball()
        Clock.schedule_interval(game.update, 1.0 / 60.0)
        return game


host = '127.0.0.1' #'ServerIP'
port = 8006
s = socket.socket()
s.connect((host,port))

flag = int(s.recv(2048).decode())

#for now we are working with 2 players

threadSendPadelPos = threading.Thread(target = sendPadelPosition, args = ())
threadReceivePos = threading.Thread(target = receivePos, args = ())

threadSendPadelPos.start()
threadReceivePos.start()


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
import json
import threading

ballpos_x = 0
ballpos_y = 0
Player_1 = 0
Player_2 = 0
Score_1 = 0
Score_2 = 0
On = True

def sending(con,player):
	global On
	global Player_1
	global Player_2
	global ballpos_x
	global ballpos_y
	global Score_1,Score_2
	while(On):
		if player == 1:
			data = {
				"ball_x": ballpos_x,
				"ball_y": ballpos_y,
				"Player_O": Player_2,
				"Player_id": player,
				"Score_1": Score_1,
				"Score_2": Score_2
			}
		else:
			data = {
				"ball_x": ballpos_x,
				"ball_y": ballpos_y,
				"Player_O": Player_1,
				"Player_id": player,
				"Score_1": Score_1,
				"Score_2": Score_2
			}
		

			'''data["ball_x"] = ballpos_x
			data["ball_y"] = ballpos_x
			data["Score_1"] = Score_1
			data["Score_2"] = Score_2
			if player == 1:
				data["Player_O"] = Player_2
			else:
				data["Player_O"] = Player_1'''
		data = json.dumps(data)
		#print(data)
		con.send(data.encode())
		

def getting(con,player):
	#print("hey")
	global On
	global Player_1
	global Player_2
	while(On):
			data = con.recv(2048).decode()
			data = json.loads(data)
			if player == 1:
				Player_1 = data["Player_O"]
			else:
				Player_2 = data["Player_O"]


class Connection:
	host = socket.gethostbyname('0.0.0.0')
	port = 8006
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
	s.bind((host,port))
	s.listen(5)
	def __init__(self,player):
		self.con= ''
		self.player = player
	def connect_to_client(self):
		self.con,addr = self.s.accept()
		print(addr," connected to server")
		
	def SendGetPos(self):
		sending_ = threading.Thread(target = sending, args = (self.con,self.player))
		getting_ = threading.Thread(target = getting, args = (self.con,self.player))
		sending_.start()
		getting_.start()
 
 
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
		self.pos = Vector(*self.velocity) + self.pos


class PongGame(Widget):
	global Player_1
	global Player_2
	global ballpos_x
	global ballpos_y
	global Score_1
	global Score_2
	ball = ObjectProperty(None)
	player1 = ObjectProperty(None)
	player2 = ObjectProperty(None)

	def serve_ball(self, vel=(4, 0)):
		global ballpos_x
		global ballpos_y
		ballpos_x,ballpos_y = self.center
		self.ball.center = self.center
		self.ball.velocity = vel

	def update(self, dt):
        
		self.player1.center_y = Player_1
		self.player2.center_y = Player_2
		self.ball.move()

        # bounce of paddles
		self.player1.bounce_ball(self.ball)
		self.player2.bounce_ball(self.ball)

        # bounce ball off bottom or top
		if (self.ball.y < self.y) or (self.ball.top > self.top):
			self.ball.velocity_y *= -1

		ballpos_x = self.ball.x
		ballpos_y = self.ball.y
        # went of to a side to score point?
		if self.ball.x < self.x:
			self.player2.score += 1
			Score_2 = self.player2.score
			self.serve_ball(vel=(4, 0))
		if self.ball.x > self.width:
			self.player1.score += 1
			Score_1 = self.player1.score
			self.serve_ball(vel=(-4, 0))
'''
    def on_touch_move(self, touch):
        if touch.x < self.width / 3:
            self.player1.center_y = touch.y
        if touch.x > self.width - self.width / 3:
            self.player2.center_y = touch.y
'''

class PongApp(App):
	def build(self):
		con1 = Connection(1)
		con2 = Connection(2)
		con1.connect_to_client()
		con2.connect_to_client()
		con1.SendGetPos()
		con2.SendGetPos()
		game = PongGame()
		game.serve_ball()
		Clock.schedule_interval(game.update, 1.0 / 60.0)
		return game

if __name__ == '__main__':
	#global On
	PongApp().run()
	On = False
"""

"""
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import (
    NumericProperty, ReferenceListProperty, ObjectProperty
)
from kivy.vector import Vector
from kivy.clock import Clock
import socket
import json
import threading

ball_x = 0
ball_y = 0
Player_O = 0
Player_id = 0
Score_1 = 0
Score_2 = 0 
Player_My = 0
On = True

def sending(s):
	global On
	global Player_My
	while(On):
		data = {
		"Player_O": Player_My
		}
		data = json.dumps(data)
		s.send(data.encode())

def getting(s):
	global On
	global ball_x
	global ball_y
	global Player_O
	global Score_1
	global Score_2
	global Player_id
	while(On):
		data = s.recv(1024).decode()
		data = json.loads(data)
		ball_x = data["ball_x"]
		ball_y = data["ball_y"]
		Player_O = data["Player_O"]
		Player_id = data["Player_id"]
		Score_1 = data["Score_1"]
		Score_2 = data["Score_2"]
class Connection:
	global Player_id
	host = '127.0.0.1'
	port = 8006
	s = socket.socket()
	def __init__(self):
		self.player = Player_id

	def connect_to_server(self):
		self.s.connect((self.host, self.port))
		print("Connected to server")
	
	def SendGetPos(self):
		sending_ = threading.Thread(target = sending, args = (self.s,))
		getting_ = threading.Thread(target = getting, args = (self.s,))
		sending_.start()
		getting_.start()
 
class PongPaddle(Widget):
	score = NumericProperty(0)



class PongBall(Widget):
	pass


class PongGame(Widget):
	global ball_x
	global ball_y
	global Player_O
	global Score_1
	global Score_2
	global Player_id
	ball = ObjectProperty(None)
	player1 = ObjectProperty(None)
	player2 = ObjectProperty(None)

	def update(self, dt):
		self.ball.x = ball_x
		self.ball.y = ball_y
		self.player1.score = Score_1
		self.player2.score = Score_2
		if Player_id == 1:
			self.player2.center_y = Player_O
		else:
			self.player1.center_y = Player_O

	def on_touch_move(self, touch):
		if touch.x < self.width / 3 and Player_id == 1:
			self.player1.center_y = touch.y
		elif touch.x > self.width - self.width / 3 and Player_id == 2:
			self.player2.center_y = touch.y


class PongApp(App):
	def build(self):
		con = Connection()
		con.connect_to_server()
		con.SendGetPos()
		game = PongGame()
		Clock.schedule_interval(game.update, 1.0 / 60.0)
		return game

if __name__ == '__main__':
	#global On
	PongApp().run()
	On = False
"""