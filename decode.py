from demo_payload import webhook_data
from klax_decoder import decode as klax_decode

if __name__ == "__main__":

    payload = klax_decode(webhook_data["port"], webhook_data["payload_raw"])

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