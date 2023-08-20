from abc import ABC, abstractmethod
import random
import time

class Destination(ABC):

    def __init__(self, name):
        self.name = name

    @abstractmethod
    def deliver(self, event):
        raise NotImplementedError('This method needs to be implemented')
    
class SuccessDestination(Destination):


    def deliver(self, event):
        message = {}
        print("Sleeping for 5 seconds")
        time.sleep(5)
        message['success'] = True
        message['code'] = 200

        return message
    
class FailDestination(Destination):
    def deliver(self, event):
        message = {}

        # Simulate failure with code 400
        message['success'] = False
        message['code'] = 400

        return message
    
class RandomDestination(Destination):
    def deliver(self, event):
        message = {}

        # Simulate random success or failure
        if random.random() < 0.5:  # 50% chance of success
            message['success'] = True
            message['code'] = 201
        else:
            print("Sleeping for 5 seconds")
            time.sleep(5)
            message['success'] = False
            message['code'] = 400

        return message