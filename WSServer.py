# chat/consumers.py
import json
from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer
import asyncio
import logging
import websockets

logging.basicConfig()

STATE = {"value": 0}

USERS = []


def state_event():
    return json.dumps({"type": "state", **STATE})


def users_event():
    msg = "Websocket Objects- "

    #testMSG = '\n"websocketObjects": [' + '\n"type": "users", ' + "\n" + '"count": ' + str(len(USERS)) + ',\n'
    testMSG = '{"websocketObjects": ['
    wsMsg = ""

    #compose list of all websocket objects
    lastIndexOfUSERS = len(USERS) -1 
    print("New Connecvtion\nlast index is" + str(lastIndexOfUSERS))

    for websocket in USERS:
        #print(str(websocket))
        wsMsg = wsMsg + str(websocket) + "\n"
        testMSG = testMSG  + '{' 
        testMSG = testMSG  + '"id": ' + str(USERS.index(websocket)) + ',' 
        testMSG = testMSG  + '"latPos": ' + str(USERS[USERS.index(websocket)][1]) + ',' 
        testMSG = testMSG  + '"longPos": ' + str(USERS[USERS.index(websocket)][2]) + ',' 
        testMSG = testMSG  + '"userIDName": "' + str(USERS[USERS.index(websocket)][3]) + '",' 
        testMSG = testMSG  + '"webSocket_Tuple": "' + str(websocket) + '' 
        testMSG = testMSG + '"}'
        if(USERS.index(websocket) != lastIndexOfUSERS):
            testMSG = testMSG + ","
        
    #print(wsMsg)
    
    testMSG = testMSG + "]}"
    print('"\n"JSON test string\n\n' + testMSG + "\n")

    ######################################### currently working
    # return json.dumps({
    #     "type": "users", 
    #     "count": len(USERS),
    #     "connections" : wsMsg,
    #     })

    # test not working, doesn't seem to send as json, other end sees as a string
    # jsonDump = json.dumps(testMSG)
    # print("type of json dump is: " + str(type(jsonDump)))
    # print("\n" + jsonDump)


    ###we are now correctly passing an dict object. the string needed to be loaded as json and then returned as jsondump
    jsonDump = json.loads(testMSG)
    print("type of json dump is: " + str(type(jsonDump)))
    print(jsonDump)
    return(json.dumps(jsonDump))

async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user[0].send(message) for user in USERS])




async def notify_users():
    if USERS:  # asyncio.wait doesn't accept an empty list
        #json message returned by function
        message = users_event()
        #sends to every websocket that's openeds
        await asyncio.wait([user[0].send(message) for user in USERS])
        


async def register(websocket):
    #add new connections to set of tuples - websocket object, x, y
    list1 = (websocket, 0, 0, "null")
    USERS.append(list1)
    print("Websocket Users are: " + str(USERS))
    await notify_users()


async def unregister(websocket):
    index = [i for i, tupl in enumerate(USERS) if tupl[0] == websocket]
    print("index of websocket: " + str(index))
    USERS.pop(index[0])
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        
        async for message in websocket:
            #each incoming message is a json object
            data = json.loads(message)
            #set GPS coords - array (have to replace tuple with new typle - python limitation)
            #identify by the websocket sending the message
            indexSearch = [i for i, tupl in enumerate(USERS) if tupl[0] == websocket]
            index = indexSearch[0]
            temp = (websocket, data["xCoor"], data["yCoor"], data["userID_Name"])
            USERS.pop(index)
            USERS.append(temp)
            print("values returned are " + str(data["xCoor"]) + ", " + str(data["yCoor"]) + ", " + str(data["userID_Name"]))
            
            if data["action"] == "minus":
                STATE["value"] -= 1
                await notify_state()
            elif data["action"] == "plus":
                STATE["value"] += 1
                await notify_state()

            else:
                logging.error("unsupported event: {}", data)
            await notify_users()
    finally:
        await unregister(websocket)

print("starting web server")
#start_server = websockets.serve(counter, "localhost", 6789)
start_server = websockets.serve(counter, "127.0.0.1", 6389)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
