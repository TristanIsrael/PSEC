

class MqttHelper():

    @staticmethod
    def check_payload(payload:dict, expected_keys:list):
        for key in expected_keys:
            if payload.get(key) is None:
                return False
        
        return True