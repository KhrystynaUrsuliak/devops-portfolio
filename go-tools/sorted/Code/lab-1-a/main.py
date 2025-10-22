import random

def generate_ebnf(mask):
    ebnf = "<word> ::= "
    meta_dict = {}
    meta_counter = 1
    i = 0

    while i < len(mask):
        if mask[i] == "[":
            i += 1
            num_str = ""
            while i < len(mask) and mask[i].isdigit():
                num_str += mask[i]
                i += 1
            if i < len(mask) and mask[i] == "]" and num_str:
                if num_str not in meta_dict:
                    meta_dict[num_str] = f"meta{meta_counter}"
                    meta_counter += 1
                ebnf += f"<{meta_dict[num_str]}>"
            i += 1
        else:
            ebnf += "'"
            while i < len(mask) and mask[i] != "[":
                ebnf += mask[i]
                i += 1
            ebnf += "'"

    ebnf += "\n"

    for num_str, meta_name in meta_dict.items():
        ebnf += f"<{meta_name}> ::= " + "(" + ")(".join("<sign>" for _ in range(int(num_str))) + ")\n"

    ebnf += "<sign> ::= '+' | '-' | '*' | '/'"

    return ebnf


def generate_word_from_mask(mask):
    result = ""
    i = 0
    while i < len(mask):
        if mask[i] == "[":
            j = i + 1
            num_str = ""
            while j < len(mask) and mask[j].isdigit():
                num_str += mask[j]
                j += 1
            if j < len(mask) and mask[j] == "]" and num_str:
                result += "".join(random.choice("+-*/") for _ in range(int(num_str)))
                i = j
            else:
                result += "["
        else:
            result += mask[i]
        i += 1
    return result


def generate_words(mask, count):
    return [generate_word_from_mask(mask) for _ in range(count)]


def main():
    mask = input("Введіть маску: ")
    print(f"\nРозширена БНФ:\n{generate_ebnf(mask)}\n")

    count = int(input("Введіть кількість слів для генерації: "))
    words = generate_words(mask, count)

    print("\nЗгенеровані слова:")
    for word in words:
        print(word)

    with open("generated_words.txt", "w") as file:
        file.write("\n".join(words))

    print("\nСлова записані у файл 'generated_words.txt'.")


if __name__ == "__main__":
    main()
