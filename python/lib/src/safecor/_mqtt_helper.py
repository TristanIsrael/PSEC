""" \author Tristan Israël """

class MqttHelper():
    """ This class contains helper functions for the MQTT facility """

    @staticmethod
    def check_payload(payload:dict, expected_keys:list):
        """ Verifies that the payload contains some necessary keys """
        
        for key in expected_keys:
            if payload.get(key) is None:
                return False
        
        return True