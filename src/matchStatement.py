file="csv"

match file:
    case "csv":
        print("The file is a CSV")
    case "json":
        print("The file is a JSON")
    case "txt":
        print("The file is a text file")
    case _:
        print("Unknown file type")
count=20
if file == "csv" or file == "json" :
    print("The file is either a CSV or JSON")
elif (file == "txt") and count>"50":
    print("The file is a text file but not a CSV")
