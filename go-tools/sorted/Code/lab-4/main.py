string = ''
index = 0
length = 0

def error():
    print('Не належить мові!')
    exit()

def match(terminal):
    global index
    if string.startswith(terminal, index):
        index += len(terminal)
    else:
        error()

def B():
    global index
    if index < length and string[index] in '123':
        index += 1
    else:
        error()

def D():
    global index
    if string.startswith('<table>', index):
        S()
    else:
        B()
        while index < length and string[index] in '123':
            B()

def C():
    while string.startswith('<td>', index):
        match('<td>')
        D()
        match('</td>')
        C()

def R():
    while string.startswith('<tr>', index):
        match('<tr>')
        C()
        match('</tr>')
        R()

def S():
    match('<table>')
    R()
    match('</table>')

def main():
    global string, index, length
    string = input('Введіть ланцюжок:\n').strip()
    length = len(string)
    index = 0
    S()
    if index == length:
        print('Ланцюжок належить мові.')
    else:
        error()

if __name__ == '__main__':
    main()
