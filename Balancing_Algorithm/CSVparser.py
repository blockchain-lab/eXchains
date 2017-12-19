class CVSparer(object):

    clientPointers = []

    def __init__(self, filepath, numClients):
        self.file = open(filepath, "r")
        # skipping header
        self.file.readline()

        for i in range(0, numClients):
            self.clientPointers.append(self.file.tell())

    def getNextRow(self, client):
        self.file.seek(self.clientPointers[client], 0)
        line = self.file.readline()
        self.clientPointers[client] = self.file.tell()
        return line.split(";")

    def skipRows(self, client, rows):
        self.file.seek(self.clientPointers[client], 0)
        for i in range(0, rows):
            self.file.readline()
        self.clientPointers[client] = self.file.tell()