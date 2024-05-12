from sys import argv

class CLI:
    
    commandLineArguments = {}

    def __init__(self):
        sliceObj = slice(1, len(sys.argv))
        sliced = argv[sliceObj]
        for arg in sliced:
            keyValue = arg.split('=')
            keyValue[0] = keyValue[0].removeprefix('--')
            self.commandLineArguments[keyValue[0]] = keyValue[1]

    def get(self, key : str) -> str:
        return self.commandLineArguments[key]
    
