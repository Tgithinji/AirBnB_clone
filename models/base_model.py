#!/usr/bin/python3
"""
This is the basemodel module and it defines the BaseModel class
"""
import uuid
from datetime import datetime
from . import storage


class BaseModel():
    """
    This is the class BaseModel
    It defines all common attributes and methods for other classes
    """
    def __init__(self, *args, **kwargs):
        """
        Initializes an instances
        """
        if len(kwargs) != 0:
            for key, value in kwargs.items():
                if key == '__class__':
                    continue
                elif key == 'updated_at' or key == 'created_at':
                    setattr(self, key, datetime.fromisoformat(value))
                else:
                    setattr(self, key, value)

        else:
            self.id = str(uuid.uuid4())
            self.created_at = datetime.now()
            self.updated_at = datetime.now()
            storage.new(self)

    def __str__(self):
        """
        Returns a  string representation of an instance
        """
        return "[{}] ({}) {}".format(
                self.__class__.__name__,
                self.id,
                self.__dict__)

    def save(self):
        """
        Updates the public instance attibute updated_at
        with the current date time
        """
        self.updated_at = datetime.now()
        storage.save()

    def to_dict(self):
        """
        Returns a dictionary containg all key/values of
        __dict__ instance
        """
        obj_dict = self.__dict__.copy()
        obj_dict['created_at'] = self.created_at.isoformat()
        obj_dict['updated_at'] = self.updated_at.isoformat()
        obj_dict['__class__'] = self.__class__.__name__
        return obj_dict
