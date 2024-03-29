import json,sys,socket

#server code can sometimes produce a [WinError 10053] An established connection was aborted by the software in your host machine, depending on firewall things. i am unaware if this will happen on the HYDRA machines but can test when we get back in class

class Server:
    def __init__(self,port):
        self.port = port
        self.player1 = None
        self.player2 = None
        #ids are just username+ip, helps server di stinguish people with the same ip
        self.player1ID = None
        self.player2ID = None
    def createServer(self):
        #create new socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #bind the port
        self.serverSocket.bind(('',self.port))
        self.serverSocket.listen(20)
        print(f"socket created on {socket.gethostbyname(socket.gethostname())} with port: {self.port}\n")
        while True:
            self.listenForConn()
            #break
        
    def listenForConn(self):
        self.serverSocket.listen(2)
        connectedClient,clientAddr = self.serverSocket.accept()
        #decode json

        try:
            decodedJson = json.loads(connectedClient.recv(4096).decode())
        except ConnectionRefusedError as e:
            print(f"ERROR: {e} \n Pytris encountered an error. This commonly is caused to do network firewall settings.")
            input("Press any key to quit")
            sys.exit()

        print(decodedJson.get("signalType"))
        

            #store data for each new player
        self.storePlayerData(decodedJson,connectedClient)


    #store player data and return the data for the opponent of the connected client
    def storePlayerData(self,jsonData,connectedClient):

        #build the id
        currentPlayerID = (str(jsonData.get("username")+"@"+jsonData.get("ip")))

        #store player data for 2 people, if a third person connects send an error
        if self.player1 == None or self.player1ID == currentPlayerID:
            self.player1 = jsonData
            self.player1ID = currentPlayerID
            try:
                self.sendData(self.player2,connectedClient)
                if self.player2 != None:
                    if self.player2["send_garbage"] > 0:
                        self.player2["send_garbage"] = 0
            except AttributeError as e:
                pass
        elif self.player2 == None or self.player2ID == currentPlayerID:
            self.player2 = jsonData
            self.player2ID = currentPlayerID
            try:
                self.sendData(self.player1,connectedClient)
                if self.player1 != None:
                    if self.player1["send_garbage"] > 0:
                        self.player1["send_garbage"] = 0
            except AttributeError as e:
                pass
        else:
            print("MAX PLAYERS REACHED")
            self.sendSignal(connectedClient,"ERROR","ERROR: GAME IS FULL!")

    #send data back to a client
    def sendData(self, playerJsonData,connectedClient):
        print(playerJsonData)
        if(playerJsonData.get("signalType") == "gameover-loss"):

            print("Gameover")
            self.sendSignal(connectedClient,playerJsonData.get("signalType"),"gameover player")
        else:    
            connectedClient.send(json.dumps(playerJsonData).encode())

    #send a game related signal that is not a game board such as gameover
    #replace with sendsignal dans thing
    def sendSignal(self,connectedClient,signalType,signalContent):

        jsonData = {
            "signalContent":signalContent,
            "signalType":signalType,       
        }
        connectedClient.send(json.dumps(jsonData).encode())
        

#create a new Server server on port 8888
server = Server(8888)


#create the server and listen for connections
server.createServer()


