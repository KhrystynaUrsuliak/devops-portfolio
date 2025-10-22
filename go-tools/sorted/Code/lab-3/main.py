def belongs_to_regex(word):
    state = 'S'
    i = 0

    while i < len(word):
        char = word[i]

        if state == 'S':
            if char == 'x':
                state = 'A'
                i += 1
            elif char == 'y':
                state = 'B'
                i += 1
            else:
                return False

        elif state == 'A':
            if char == 'y':
                state = 'C'
                i += 1
            else:
                return False

        elif state == 'B':
            if char == 'x':
                state = 'S10'
                i += 1

            elif char == 'y':
                state = 'S13'
                i += 1
            else:
                return False

        elif state == 'C':
            if char == 'x':
                state = 'S10'
                i += 1
            elif char == 'y':
                state = 'S'
                i += 1
            else:
                return False

        elif state == 'S10':
            if char == 'y':
                state = 'S11'
                i += 1
            else:
                return False

        elif state == 'S11':
            if char == 'y':
                state = 'B'
                i += 1
            else:
                return False

        elif state == 'S13':
            if char == 'y':
                state = 'S13'
                i += 1
            else:
                return False

        else:
            return False

    return state in ['S', 'A', 'B', 'C', 'S11', 'S13']

string = input("Введіть ланцюжок символів (R = (xyy)*(x|e)(yxy)*y*): \n")
if belongs_to_regex(string):
    print(f"Ланцюжок {string} належить мові автомата.")
else:
    print(f"Ланцюжок {string} НЕ належить мові автомата.")