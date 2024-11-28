import time
import os
from threading import Thread
from queue import Queue

class TaskRunner:
    max_tasks_:int = os.cpu_count()
    queue_ = Queue()
    threads_ = []
    running_ = False

    def __init__(self, max_tasks:int = 0):
        if max_tasks > 0:
            self.max_tasks_ = max_tasks

    def start(self):
        # Management thread
        Thread(target= self.__loop).start()

    def stop(self):
        self.running_ = False

        # We wait for all the threads to terminate
        for task in self.threads_:
            if task is not None:
                task.join()

    def run_task(self, task, args):
        thread = Thread(target= task, args= args)
        self.queue_.put(thread)
        
    def __loop(self):
        self.running_ = True 

        while self.running_:            
            # We start as many threads as max_tasks
            # We join all these threads
            # If there are too many running tasks we enque             
            if self.queue_.qsize() > 0 and len(self.threads_) < self.max_tasks_:
                # We start a new thread
                thread:Thread = self.queue_.get()
                self.threads_.append(thread)
                thread.start()

                print("Running threads : {}".format(len(self.threads_)))

            # Then we join oldest thread
            if len(self.threads_) > 0:
                thread = self.threads_.pop(0)
                thread.join()
                
            time.sleep(0.1)