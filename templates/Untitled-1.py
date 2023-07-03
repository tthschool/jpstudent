def recusive(list , target):
    if len(list) == 0:
        return False
    else:
        mid = len(list) // 2
        if list[mid] == target:
            return True
        else:
            if list[mid] > target:
                return recusive(list[:mid], target)
            if list[mid] < target:
                return recusive(list[mid+1:], target)

def main():
    list = [1,2,3,4,5,6,7,8,9,10]
    target = 5
    print(recusive(list, target))