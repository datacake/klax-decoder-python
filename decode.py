from demo_payload import webhook_data
from klax_decoder import decode as klax_decode
import base64


def make_bytes(input):
    decoded = base64.b64decode(input)
    return decoded


if __name__ == "__main__":

    port = webhook_data["port"]
    payload = webhook_data["payload_raw"]

    # Wenn Payload über TTN kommt, sieht es meist so aus:
    # AGoKEQMAAAAAAAAANQ/OAbkRAy1oNAMtZvwDLWXAAy1k2AAAAAAAAAAAAAAAAAAAAAABdQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==
    # Base64 Encoded Hex-Bytestring, wird dekodiert nach:
    # b'\x00j\n\x11\x03\x00\x00\x00\x00\x00\x00\x005\x0f\xce\x01\xb9\x11\x03-h4\x03-f\xfc\x03-e\xc0\x03-d\xd8\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01u\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    # Dafür wird benötigt:
    payload = make_bytes(payload)

    # Und dann:
    payload = klax_decode(port, payload)

    print(payload)
    print()

    payloads = payload["payloads"]
    for payload in payloads:
        type = payload["type"]
        if type == "historic":
            registers = payload["registers"]
            for register in registers:
                if register["data_valid"] is True:
                    unit = register["unit"]
                    values = register["values"]
                    for value in values:
                        print(value)



    # Wenn Payload über Wanesy oder andere Quelle kommt, sieht es manchmal so aus:
    # 004a1511030a01445a470003975d7801b91100003a9800003a9800003a9800003a98000000000000000000000000000000000175000000000000000000000000000000000000000000000000000000000000000000
    # Damit kann der Python Decoder aber nicht umgehen (der Javascript Decoder schon)

    # Daher müssen wir hier vorerst:
    payload = bytes.fromhex("004a1511030a01445a470003975d7801b91100003a9800003a9800003a9800003a98000000000000000000000000000000000175000000000000000000000000000000000000000000000000000000000000000000")

    # und können dann direkt:
    payload = klax_decode(port, payload)

    print(payload)
    print()

    payloads = payload["payloads"]
    for payload in payloads:
        type = payload["type"]
        if type == "historic":
            registers = payload["registers"]
            for register in registers:
                if register["data_valid"] is True:
                    unit = register["unit"]
                    values = register["values"]
                    for value in values:
                        print(value)
