# Translates Hack assembly programs into executable Hack binary code

# Source: xxx.asm
# Target: xxx.hack
# Assumes: xxx.asm is error free


import string
import sys
import SystemTable

outputPath = "/Users/mono/OneDrive/Developer/nand2tetris/output.hack"

ASSIGNMENT = "="
aInstruction = "@"
COMMENT = "//"
JUMP = ";"
LABEL = "("
NEWLINE = '\n'
SYSTEM_BIT_LENGTH = 15 # minus 15 = 16- 1 for a or c inst
symbolTable = SystemTable.SymbolTable()
LETTERS = string.ascii_lowercase + string.ascii_uppercase

def main():
    # Instantiate other modules
    parser = Parser()
    coder = Coder()
    writer = Writer()

    instructions = []
    lineNumber = 0

    # Check that command line arguments are correct.  Else, quit
    if len(sys.argv) != 2:
        showUsage()
        exit()

    # Open command line argument as file
    asmPath = sys.argv[1]
    asmFile = open(asmPath, 'r')

    # First pass
    for line in asmFile:
        line = line.strip()

        # Skip comments and newlines
        if line[0:2] == COMMENT or len(line) == 0:
            continue
        else:
            # Assign line numbers to labels
            lineNumber = parser.parseLabels(line, lineNumber)

    # Go back to beginning of file
    asmFile.seek(0)

    # Second pass
    for line in asmFile:

        # Ignore comments and newlines
        line = line.strip()
        if line[0:2] == COMMENT or len(line) == 0:
            continue

        # Else parse the line
        else:
            # Translate symbols into bits
            fields = parser.parse(line)
            if fields != None:
                instruction = coder.code(fields)
                instructions.append(instruction)


    # Write instructions to output file
    writer.write(instructions)

def showUsage():
    print("\n")
    print("Usage: hackAssembler filename.asm")
    print("\n")


# Encapsulates access to the input code.
# Reads an assembly language command, parses it,
# and provides access to
# the command’s components (fields and symbols).
# In addition, removes all white space and comments.
class Parser():

    def aInst(self, line):
        return line[0] == aInstruction

    def parse(self, line):
        """
        :argtype: string
        :rtype : list
        """
        line = self.removeInlineComments(line)

        if self.aInst(line):
           return self.parseAIsnt(line)

        elif self.lInst(line):
            return None
        else:
            return self.parseCInst(line)

    def lInst(self, line):
        return LABEL in line

    def parseAIsnt(self, line):
        return [line[0], line[1:]]

    def parseCInst(self, line):
        if ASSIGNMENT in line:
            return line.split("=")
        if JUMP in line:
            return line.split(";")

    def parseLabels(self, line, lineNumber):

        if COMMENT in line:
            # Separate out in line comments
            fields = line.split("//")
            line = fields[0]

        if LABEL in line:
            line = line.strip('()')
            symbolTable.addEntry(line, lineNumber)
            return lineNumber
        return lineNumber + 1

    def removeInlineComments(self,line):
        # Find inline comments
        if COMMENT in line:
            if line[0:2] != COMMENT:
                fields = line.split("//")
                line = fields[0]
                line = line.strip()
        return line

#
# Translates Hack assembly language mnemonics into binary codes.
#
class Coder():

    def code(self, fields):
        opCode = None
        # If a instruction
        if fields[0] == aInstruction:
            address = fields[1]
            opCode = "0"
            return opCode + self.codeAddress(address)

        # If reference to label
        elif fields[0][0] == LABEL:
            label = fields[0]
            opCode = "0"
            label = label.strip("()")
            return opCode + self.codeAddress(label)

        # If c instruction
        else:
            opCode = "1"

            # If it's a jump test
            if self.jump(fields):
                # Set dest, a, and comp bits
                destBits = self.dest(None)
                result = self.comp(fields[0])
                aBit = result[0]
                compBits = result[1]
                jumpBits = self.getJump(fields[1])

            else:
                # Set dest, a, and comp bits
                destBits = symbolTable.dest[fields[0]]
                result = symbolTable.comp(fields[1])
                aBit = result[0]
                compBits = result[1]
                jumpBits = "000"

            # Add all the bits together
            return opCode + "11" + aBit + compBits + destBits + jumpBits

    def codeAddress(self, address):
        """
        Codes the 15 bit address of an A command.
        Three cases: literal address, label, variable.
        :rtype : str
        """
        # If label
        if symbolTable.contains(address):
            address = symbolTable.getAddress(address)

        #Else, variable or literal
        else:
            if address[0] in LETTERS:
                address = symbolTable.addEntry(address, symbolTable.n)
                symbolTable.incrementN()

        # Convert number to 15 bit binary number
        binNumber = self.toBinary(address)
        bits = self.prependZeros(str(binNumber))
        return bits

    def comp(self, field):
        return symbolTable.comp(field)

    def dest(self, field):
        return symbolTable.dest[field]

    def getJump(self, field):
        return symbolTable.jump[field]

    def jump(self, fields):
        for field in fields:
            if field in symbolTable.jump:
                return True
        return False

    def toBinary(self, address):
        """
        :rtype : int
        """
        return bin(int(address))[2:] # Slice off some of Python's formatting

    def prependZeros(self, pythonBinNum):
        """
        :rtype : str
        """
        numZerosToAppend = SYSTEM_BIT_LENGTH - len(pythonBinNum)
        return ("0" * numZerosToAppend ) + pythonBinNum

#
# Writes bits to disk
#
class Writer():

    def write(self, instructions):
        try:
            f = open(outputPath, 'w')
            for instruction in instructions:
                f.write(instruction + "\n")
            f.close()
        except:
            print "Print problem writing output to file"
        print "Wrote output to file succesfully"

# Execute script
main()