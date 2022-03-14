def compareHeight(h1, h2):
    h1Feet = int(h1.split("-")[0])
    h1In = int(h1.split("-")[1])
    h2Feet = int(h2.split("-")[0])
    h2In = int(h2.split("-")[1])
    
    if h1Feet > h2Feet:
        return 1
    elif h1Feet == h2Feet:
        if h1In > h2In: return 1
        elif h1In == h2In: return 0
        else: return -1
    else:
        return -1

amari = " 5-11"
zeke = " 4-9"

print(compareHeight(amari, zeke))