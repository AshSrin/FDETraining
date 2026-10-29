amount=20000


match amount:
    case amount if amount<10000:
         print("approval by supervisor.")
    case amount if amount>10000 and amount<250000:
            print("approval by manager in match")       
    case amount if amount>250000 and amount<500000:
            print("approval by director.")  