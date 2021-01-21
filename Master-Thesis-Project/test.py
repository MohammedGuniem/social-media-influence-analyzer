l = [
    {
        "a": 0,
        "b": 0
    },
    {
        "a": 0,
        "b": 0
    }
]

print(l)


def removeDuplicatesFromDictArray(input_array):
    output_array = []
    for d in input_array:
        if d not in output_array:
            output_array.append(d)
    return output_array

print(removeDuplicatesFromDictArray([0, 1, 0]))
print(removeDuplicatesFromDictArray(l))
