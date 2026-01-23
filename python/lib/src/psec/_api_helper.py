class ApiHelper:
    """
    This class provides static functions to help getting information from the API.

    The functions extract data from the payload contained in the API messaged. 
    
    Example: 
    
    ::

        def on_message_received(self, topic:str, payload:dict):
            if topic == Topics.DISK_STATE:
                disk_name = ApiHelper.get_disk_name(payload)

    """

    @staticmethod
    def get_disk_name(payload:dict) -> str:
        """
        Returns the name of the disk.

        Associated topics: :attr:`Topics.DISK_STATE`
        
        Args:
            payload: The payload received from the broker            
        """
        return payload.get("disk", "")        
        
    @staticmethod
    def get_disk_state(payload:dict) -> str:        
        """
        Returns the state of the disk (= "connected")
        
        Args:
            payload: The payload received from the broker            
        """
        return payload.get("state", "")        
        
    @staticmethod
    def is_disk_connected(payload:dict) -> str:
        """
        Returns true if the disk is connected
        
        Args:
            payload: The payload received from the broker            
        """
        return ApiHelper.get_disk_state(payload) == "connected"