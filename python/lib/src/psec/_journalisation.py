import logging

class Journal(logging.Logger):

    def __init__(self, name):
        super().__init__(name, logging.DEBUG)
        self.extra_info = None 

        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s %(levelname)-8s [%(name)-20s] %(message)s')
        handler.setFormatter(formatter)
        self.addHandler(handler)

    def info(self, msg, *args, xtra=None, **kwargs):
        extra_info = xtra if xtra is not None else self.extra_info
        super().info(msg, *args, extra=extra_info, **kwargs)

    def debug(self, msg, *args, xtra=None, **kwargs):
        extra_info = xtra if xtra is not None else self.extra_info
        super().debug(msg, *args, extra=extra_info, **kwargs)

class JournalProxy():

    def __init__(self):
        pass