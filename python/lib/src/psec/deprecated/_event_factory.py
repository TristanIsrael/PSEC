from datetime import datetime

class EventFactory():
    """Cette classe permet de générer une erreur au format JSON"""

    @staticmethod
    def create_event(level:int, module:str, description:str) -> dict :
        now = datetime.now()
        datetime = now.strftime(f"%Y-%m-%d %H:%M:%S.{now.microsecond // 1000:03d}")

        payload = {
            "level": level,
            "module": module,
            "datetime": datetime,
            "description": description
        }

        return payload