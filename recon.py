# ______________________________ dependencies ______________________________

# Written in Python 3.9.1
from enum import Enum
from os   import listdir, path


# ______________________________ classes ______________________________

class Transaction:
    def __init__(self, s, a, q, ca):
        self.symbol     = str(s)     # String
        self.action     = Action[a]  # Enum Action
        self.quantity   = float(q)   # Float
        self.cashAmount = float(ca)  # Float


class Action(Enum):
    BUY      = 0
    SELL     = 1
    DEPOSIT  = 2
    WITHDRAW = 3
    FEE      = 4
    DIVIDEND = 5

    def addsQuantity(self):
        return self == Action.BUY

    # def subsQuantity(self):
    #     return self == Action.SELL

    def addsCashAmount(self):
        return self in { Action.SELL, Action.DEPOSIT, Action.DIVIDEND }

    # def subsCashAmount(self):
    #     return self in { Action.BUY, Action.WITHDRAW, Action.FEE }


# ______________________________ functions ______________________________

def findFinalPosition(files):
    files.sort()
    files.reverse()
    for file in files:
        if file.endswith('-POS.txt'):
            return file


def parsePositionFile(filePath):
    with open(filePath, 'r') as file:
        symbols = {}
        for line in file:
            line = line.split()
            symbols[line[0]] = float(line[1])

    return symbols


def parseTransactionFile(filePath):
    with open(filePath, 'r') as file:
        transactions = []
        for line in file:
            line = line.split()
            transactions.append(Transaction(line[0], line[1], line[2], line[3]))

    return transactions


def performTest(dir):
    myFiles = listdir(dir)

    start            = parsePositionFile(path.join(dir, 'D0-POS.txt'))
    end              = parsePositionFile(path.join(dir, findFinalPosition(myFiles)))
    expectedReconOut = parsePositionFile(path.join(dir, 'expected-recon-out.txt'))
    myReconOut = {}

    for file in myFiles:
        # Only need to evaluate transactions between start and end positions
        if not file.endswith('-TRN.txt'):
            continue

        # Iteratively apply transactions to start
        # We don't need to go in chronological order to get the diff
        for trn in parseTransactionFile(path.join(dir, file)):
            if start.get(trn.symbol) is None:
                start[trn.symbol] = 0

            if Action.addsQuantity(trn.action):
                start[trn.symbol] += trn.quantity
            else:
                start[trn.symbol] -= trn.quantity

            if Action.addsCashAmount(trn.action):
                start['Cash'] += trn.cashAmount
            else:
                start['Cash'] -= trn.cashAmount

    # Default missing keys so we don't skip anything
    for key in start:
        if end.get(key) is None:
            end[key] = 0

    for key in end:
        if start.get(key) is None:
            start[key] = 0

        value = end[key] - start[key]

        # 0 quantity positions are not included
        if value != 0:
            myReconOut[key] = value

    displayResults(expectedReconOut, myReconOut)


def displayResults(expected, actual):
    endc    = '\033[0m'
    redc    = '\033[31m'
    greenc  = '\033[32m'
    yellowc = '\033[33m'
    banner  = '------------------------------'

    if expected == actual:
        print(f'{greenc}{banner} test case passed {banner}{endc}')
    else:
        print(f'{redc}{banner} test case failed {banner}{endc}')

    print(f'{yellowc}Expected:{endc}', expected)
    print(f'{yellowc}Actual:{endc}  ', actual, '\n')


def run():
    myDir = path.dirname(__file__)
    
    for subDir in listdir(path.join(myDir, 'tests')):
        # Skip hidden directories like .DS_Store
        if subDir.startswith('.'):
            continue
        performTest(path.join(myDir, 'tests', subDir))


# ______________________________ main ______________________________

if __name__ == '__main__':
    run()

