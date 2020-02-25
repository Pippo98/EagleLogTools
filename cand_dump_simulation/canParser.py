def parseMessage(message):
    parsed_message = {}
    if type(message) == bytes:
        message = message.decode('utf-8')
    try:
        message = message.replace("\n", "")
        message = message.split(" ")
        parsed_message["timestamp"] = float(message[0].replace("(", "").replace(")", ""))
        id_ = int(message[2].split("#")[0], 16)

        payload = []
        for i in range(0,len(message[2].split("#")[1]), 2):
            payload.append(int(message[2].split("#")[1][i:i+2], 16))
        
        parsed_message["id"] = id_
        parsed_message["payload"] = payload
    except:
        parseMessage = []
    return parsed_message


def fillCarData(message, data):
    if message["id"] == 192:
        if message["payload"][0] == 0:
            data["accel"]["x"] = ((message["payload"][1] * 256 + message["payload"][2])/100 - message["payload"][7])
            data["accel"]["y"] = ((message["payload"][3] * 256 + message["payload"][4])/100 - message["payload"][7])
            data["accel"]["z"] = ((message["payload"][5] * 256 + message["payload"][6])/100 - message["payload"][7])

        if message["payload"][0] == 1:
            data["gyro"]["x"] = ((message["payload"][1] * 256 + message["payload"][2])/10 - (message["payload"][7]) * 10)
            data["gyro"]["y"] = ((message["payload"][3] * 256 + message["payload"][4])/10 - (message["payload"][7]) * 10)
            data["gyro"]["z"] = ((message["payload"][5] * 256 + message["payload"][6])/10 - (message["payload"][7]) * 10)
    if message["id"] == 208:
        if message["payload"][0] == 6:
            data["speed"] = (message["payload"][4] * 256 + message["payload"][5])*3.6 * -1 if message["payload"][3] == 1 else 1
        if message["payload"][0] == 16:
            data["GPS"]["speed"] = (message["payload"][6] * 256 + message["payload"][7])/100
            print(data["GPS"])
    return data