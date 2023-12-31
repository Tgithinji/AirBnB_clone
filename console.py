#!/usr/bin/python3
"""module of the entry point of the command interpreter"""
import cmd
import re
import json
from models.base_model import BaseModel
from models import storage
from models.user import User
from models.state import State
from models.city import City
from models.amenity import Amenity
from models.place import Place
from models.review import Review


class HBNBCommand(cmd.Cmd):
    """
    Command intepreter for the application
    """
    prompt = '(hbnb) '
    class_dict = {
        'BaseModel': BaseModel,
        'User': User,
        'State': State,
        'City': City,
        'Amenity': Amenity,
        'Place': Place,
        'Review': Review
    }

    def do_create(self, class_name):
        """
        Creates a new instance of a class and saves it
        and prints its id
        """
        if class_name == "":
            print("** class name missing **")
        else:
            try:
                instance = self.class_dict[class_name]()
                print(instance.id)
                instance.save()
            except KeyError:
                print("** class doesn't exist **")

    def do_show(self, args):
        """
        Prints the string representation of an instance based on class and id
        """
        if args == "":
            print("** class name missing **")
        else:
            args = args.split()
            name = args[0]
            if len(args) != 1:
                obj_id = args[1]
            else:
                obj_id = ""
            if name not in self.class_dict:
                print("** class doesn't exist **")
            elif obj_id == "":
                print("** instance id missing **")
            else:
                id_exists = False
                objects = storage.all()
                obj_key = f"{name}.{obj_id}"
                for key, obj in objects.items():
                    if key == obj_key:
                        id_exists = True
                        print(obj)

                if id_exists is False:
                    print("** no instance found **")

    def do_destroy(self, args):
        """
        Deletes an instance based on class name and id
        """
        if args == "":
            print("** class name missing **")
        else:
            args = args.split()
            name = args[0]
            if len(args) == 1:
                obj_id = ""
            else:
                obj_id = args[1]

            if name not in self.class_dict:
                print("** class doesn't exist **")
            elif obj_id == "":
                print("** instance id missing **")
            else:
                id_exists = False
                objects = storage.all()
                obj_key = f"{name}.{obj_id}"
                for key, obj in objects.items():
                    if obj_key == key:
                        id_exists = True
                        to_delete = key

                if id_exists is False:
                    print("** no instance found **")
                else:
                    del objects[to_delete]
                    storage.save()

    def do_all(self, args):
        """
        Prints all string representations of all instances
        based on or not the class name
        """
        object_list = []
        objects = storage.all()
        if args == "":
            for key, obj in objects.items():
                object_list.append(obj.__str__())
            print(object_list)
        elif args in self.class_dict:
            for key, obj in objects.items():
                class_name, obj_id = key.split('.')
                if args == class_name:
                    object_list.append(obj.__str__())
            print(object_list)
        else:
            print("** class doesn't exist **")

    def do_update(self, arg):
        """
        Updates an instance based on class name and id
        """
        args = arg.split()

        if arg == "":
            print("** class name missing **")
        else:
            args = arg.split()

            if args[0]:
                name = args[0]
                if name not in self.class_dict:
                    print("** class doesn't exist **")
                    return
            try:
                obj_id = args[1]
                objects = storage.all()
                id_exists = False
                obj_key = f"{name}.{obj_id}"
                for key, obj in objects.items():
                    if obj_key == key:
                        id_exists = True
                        instance = obj
                if id_exists is False:
                    print("** no instance found **")
                    return
            except IndexError:
                print("** instance id missing **")
                return

            try:
                attribute_name = args[2]
            except IndexError:
                print("** attribute name missing **")
                return

            try:
                attribute_value = args[3]
            except IndexError:
                print("** value missing **")
                return

            # strip attribute value to remove unnecessary quotes
            attribute_value = attribute_value.strip('"')
            try:
                attr_type = type(getattr(instance, attribute_name))
                # cast the attribute value to its data type
                value = attr_type(attribute_value)
                setattr(instance, attribute_name, value)
            except AttributeError:
                if re.match(r'^\d+\.\d+$', attribute_value):
                    value = float(attribute_value)
                elif re.search(r'[a-zA-Z]', attribute_value):
                    value = str(attribute_value)
                elif re.search(r'\d', attribute_value):
                    value = int(attribute_value)
                setattr(instance, attribute_name, value)
            instance.save()

    def count_instances(self, arg):
        """
        retrieve the number of instances of a class
        """
        count = 0
        objects = storage.all()
        for key, obj in objects.items():
            class_name, obj_id = key.split('.')
            if class_name == arg:
                count += 1
        return count

    def default(self, command):
        """
        Handle Unrecognized command syntax commands
        """
        commands = command.split('.', 1)
        if len(commands) < 2:
            print("** Unknown syntax:", commands[0])
            return
        else:
            class_name, method = commands[0], commands[1]

        methods = method.split('(')
        if len(methods) < 2:
            print("** Unknown syntax:", command)
            return
        method_name = methods[0]
        if method_name not in ['all', 'count', 'show', 'destroy', 'update']:
            print("Unknown method:", command)
            return
        args = methods[1].rstrip(')')

        if method_name == 'all':
            self.do_all(class_name)
        if method_name == 'count':
            count = self.count_instances(class_name)
            print(count)
        if method_name == 'show':
            args = args.strip('"')
            self.do_show(f"{class_name} {args}")
        if method_name == 'destroy':
            args = args.strip('"')
            self.do_destroy(f"{class_name} {args}")
        if method_name == 'update':
            if '{' in args and '}' in args:
                args = args.split(', ', 1)
                obj_id = args[0].strip('"')
                attr_args = json.loads(args[1])
                for key, value in attr_args.items():
                    self.do_update(f'{class_name} {obj_id} {key} "{value}"')
            else:
                args = args.split(', ')
                obj_id = args[0].strip('"')
                attr_name = args[1].strip('"')
                attr_value = args[2]
                self.do_update(f"{class_name} {obj_id} {attr_name} {attr_value}")

    def do_quit(self, arg):
        """
        Quits and exits the program
        """
        return True

    def do_EOF(self, arg):
        """
        Exits on EOF (Ctrl+D)
        """
        print("")
        return True

    def emptyline(self):
        """
        Ignore an empty input
        """
        pass

    # custom help commands
    def help_show(self):
        """
        Help command for show method
        """
        print("Prints the string representation of an instance")
        print("Usage: show <class_name> <id>")

    def help_create(self):
        """
        Custom help command for create method
        """
        print("Creates an new instance of a class and saves it to JSON file")
        print("Usage: create <class_name>")

    def help_destroy(self):
        """
        Shows description od destroy command
        """
        print("Deletes an instance based on class name and id")
        print("Usage: destroy <class_name> <id>")

    def help_all(self):
        """
        Shows a description of all command
        """
        print("Prints all string representation based or not on class name")
        print("Usage: all / all <class_name>")

    def help_update(self):
        """
        Description of the update command
        """
        print("Updates an instance based on the class name and id")
        print('Usage: update <class name> <id> <attribute name> ' +
              '"<attribute value>"')

    def help_quit(self):
        """
        Custom Help guide for quit
        """
        print("Quit command to exit the program")
        print("")

    def help_EOF(self):
        """
        Custom help guide for EOF
        """
        print("Exits on EOF")
        print("Usage: ctrl+D")


if __name__ == '__main__':
    HBNBCommand().cmdloop()
