# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import asyncio
#import websockets

#When a user posts a message, a JavaScript function will: 
#-transmit the message over WebSocket to a ChatConsumer. 
#-The ChatConsumer will receive that message and forward it to the group corresponding to the room name. 
#--Every ChatConsumer in the same group (and thus in the same room) will then:
#----receive the message from the group and forward it over WebSocket back to JavaScript, where it will be appended to the chat log.


class ChatConsumer(WebsocketConsumer):
    #have each consumer layer communicate to other webserver running
    def connect(self):

        #Obtains the 'room_name' from  URL route in chat/routing.py that opened the WebSocket connection to consumer.
        #Every consumer has a scope that contains information about its connection, including in particular:
        # any positional or keyword arguments from the URL route 
        # and 
        #the currently authenticated user if any
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        


        #Constructs a Channels group name directly from the user-specified room name, without any quoting or escaping.
        # Group names may only contain letters, digits, hyphens, and periods. 
        # Therefore this example code will fail on room names that have other characters.
        self.room_group_name = 'chat_%s' % self.room_name

        # Join room group
        # The async_to_sync(…) wrapper is required because 
        # ChatConsumer is a synchronous WebsocketConsumer but it is calling an asynchronous channel layer method. 
        # (All channel layer methods are asynchronous.)
        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )

        #Accepts the WebSocket connection.
        # If you do not call accept() within the connect() method then the connection will be rejected and closed. 
        # You might want to reject a connection for example because the requesting user is not authorized to perform the requested action.
        self.accept()
        welcomeMsg = "Welcome New User - " + str(self.channel_layer)
        
        self.send(text_data=json.dumps({
            'message': welcomeMsg,
            'socketID': str(self.channel_layer),
            'userID': str(self.channel_name),
        }))



        # Send message to room group
        welcomeString = "User '" + str(self.channel_layer) + "' Just Joined"
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': welcomeString
            }
        )

        print("self is " + str(self))
        #print("self scope is " + str(self.scope))
        print("self room is " + str(self.room_name))
        #channel layer is an object
        print ("self layer is " + str(self.channel_layer))
        print ("self channel name is " + self.channel_name)





        


    def disconnect(self, close_code):
        # Leave room group
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': "User Just Left"
            }
        )

        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        x = text_data_json['xCoord']
        y = text_data_json['yCoord']
        chatUserName = text_data_json['chatUser']
        print("x coord is " + str(x))
        print("y coord is " + str(y))
        print("chatUserName is " + str(chatUserName))
        
        #print(message)
        # Send message to room group
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'chatterName': str(chatUserName),
            }
            
        )
        print ("Msg receieeeeeeeved from Websocket")

    # Receive message from room group
    def chat_message(self, event):
        message = event['message']
        
        print("length of dict is: " + str(len(event)))
        if(len(event) == 3):
            socketUser = event['chatterName']
        else:
            socketUser = "Undefined"

        print(socketUser)
      

        # Send message to WebSocket
        self.send(text_data=json.dumps({
            'message': message,
            'socketUser': socketUser,
            
        }))
        print ("Msg received from Websocket room group")

    #backend socket 

