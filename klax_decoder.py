import math

REGISTER_RAW = False

METER_TYPES = [
  'SML',
  'IEC 62056-21 Mode B',
  'IEC 62056-21 Mode C',
  'Logarex',
]

REGISTER_UNITS = [
  'NDEF',
  'Wh',
  'W',
  'V',
  'A',
  'Hz'
]


def parse_header(data):
    version = data[0]
    batteryPerc = (data[1] & 0xf) * 10
    meterType = METER_TYPES[(data[1] & 0x30) >> 4]
    configured = (data[1] & 0x40) > 0
    connTest = (data[1] & 0x80) > 0
    return { 'version': version, 'batteryPerc': batteryPerc, 'meterType': meterType, 'configured': configured, 'connTest': connTest }


def parse_msg_info(data):
    msgIdx = data[0]
    msgCnt = data[1] & 0x0f
    msgNum = (data[1] & 0xf0) >> 4
    return { 'msgIdx': msgIdx, 'msgCnt': msgCnt, 'msgNum': msgNum }


def parseInt(bytes):
    result = 0
    for b in bytes:
        result = result * 8 + int(b)
    return result


def decodeUIntN(data, bits, be):
    val = 0
    bytes = int(bits / 8) # Fuck off python typesafe -> Cast to Int
    for i in range(0, bytes):
        index = (bytes - 1 - i) if be else i
        val += data[index] * math.pow(2, i * 8)
    return val


def decodeUInt16BE(bytes):
    return decodeUIntN(bytes, 16, True)


def decodeIntN(data, bits, be):
    val = 0
    bytes = int(bits / 8) # Fuck off python typesafe -> Cast to Int
    for i in range(0, bytes):
        val += data[i] << (( (bytes - 1 - i) if be else i ) * 8)
    return val


def decodeInt32BE(bytes):
    return decodeIntN(bytes, 32, True)


def mkRegister(data, lastValid, unitId):
    unit = None
    if unitId < len(REGISTER_UNITS):
        unit = REGISTER_UNITS[unitId]
    else:
        unit = None
    dataValid = False
    values = []
    while len(data) >= 4:
        if (REGISTER_RAW):
            raw = data[0:4]
            bytes =[]
            for i in range(0, len(raw)):
                val = raw[i]
                if (val != 0):
                    dataValid = True
                bytes.append(parseInt(val))
            values.append(bytes)
        else:
            val = decodeInt32BE(data)
            if (val != 0):
                dataValid = True
            values.append(val)
        data = data[4:]
    dataValid = dataValid | lastValid
    return {'data_valid': dataValid, 'unit': unit, 'values': values}


def decodeHistoric(data):
    regmask = data[0]
    reg1Active = (regmask & 0x01) > 0
    reg1Filter = (regmask & 0x06) >> 1
    reg1Valid = (regmask & 0x08) > 0
    reg2Active = (regmask & 0x10) > 0
    reg2Filter = (regmask & 0x60) >> 5
    reg2Valid = (regmask & 0x80) > 0
    units = data[1]
    reg1Unit = units & 0x0f
    reg2Unit = (units & 0xf0) >> 4
    data = data[2:]
    registers = []

    if (reg1Active):
        reg = mkRegister(data[0:16], reg1Valid, reg1Unit)
        reg["filterId"] = reg1Filter
        registers.append(reg)

    data = data[16:]

    if (reg2Active):
        reg = mkRegister(data[0:16], reg2Valid, reg2Unit)
        reg["filterId"] = reg2Filter
        registers.append(reg)

    return {'type': 'historic', 'registers': registers}


def decodeNow():
    pass


def uint8ToHex(data):
    pass


def decodeServerID(data):
    id = ""
    for i in range(0, len(data)):
        id = id + str(data[i])
    return {'type': 'serverID', 'id': id}


PAYLOAD_HANDLERS = [
  { 'id': 1, 'length': 34, 'decode': decodeHistoric },
  { 'id': 2, 'length': 19, 'decode': decodeNow },
  { 'id': 3, 'length': 10, 'decode': decodeServerID },
]


def getHandler(data):
    id = data[0]
    for handler in PAYLOAD_HANDLERS:
        if handler["id"] == id:
            return handler
    return None


def parsePayload(handler, bytes):
    f = handler["decode"]
    return f(bytes[0:handler["length"]])


def parse_app(bytes):
    header = parse_header(bytes)
    print(header)
    bytes = bytes[2:]
    msgInfo = parse_msg_info(bytes)
    print(msgInfo)
    bytes = bytes[2:]
    print('Got ' + str(len(bytes)) + ' bytes of payload')
    payloads = []
    while (len(bytes) > 0):
        handler = getHandler(bytes)
        if handler is None:
            print('Encountered unknown payload type ' + str(bytes[0]))
            break
        bytes = bytes[1:]
        print('Found payload type ' + str(handler["id"]) + ' with length of ' + str(handler["length"]) + ' bytes')
        payloads.append(parsePayload(handler, bytes))
        bytes = bytes[handler["length"]:]

    appData = {'type': 'app', 'header': header, 'msgInfo': msgInfo, 'payloads': payloads}

    return appData


decoders = [
  { 'port': 3,   "minLen":  4, "name": 'app',            'function': parse_app },
  { 'port': 100, "minLen":  4, "name": 'config',         'function': 0 },
  { 'port': 101, "minLen":  4, "name": 'info',           'function': 0 },
  { 'port': 103, "minLen":  4, "name": 'registerSearch', 'function': 0 },
  { 'port': 104, "minLen": 15, "name": 'registerSet',    'function': 0 },
]


def get_decoder(decoders, port):
    dict = None
    for _dict in decoders:
        if _dict["port"] == port:
            dict = _dict
            break
    return dict


def decode(port, bytes):
    dict = get_decoder(decoders, port)
    if dict is None:
        return None
    if len(bytes) < dict["minLen"]:
        print("Message to short for decoder: " + dict["name"])
        return None
    r = dict["function"](bytes)
    return r