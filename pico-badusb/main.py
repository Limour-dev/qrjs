from badusb.command import Command
import storage

class MyCommand(Command):
    def myexecute(self, path: str) -> None:
        with open(path, "r", encoding="utf-8") as f:
            payload = f.readlines()
        storage.umount('/')
        for string in payload:
            self.__string = string.rstrip('\n\r')
            if self.__string.startswith('STRING'):
                self.__arguments = ['STRING']
            else:
                self.__arguments = self.__string.split(" ")
            if len(self.__arguments) > 0:
                command = self.__arguments.pop(0).lower()
                
                if hasattr(Command, command):
                    self.__string = self.__string[len(command) + 1:]
                    
                    try:       
                        getattr(Command, command)(self)
                    
                    except Exception as e:
                        self.__keyboard.release()
    
if __name__ == "__main__":
    MyCommand().myexecute("payload.txt")