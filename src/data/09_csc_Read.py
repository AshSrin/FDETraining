import csv
with open('/Users/srinivasan.ashwini/Documents/fde-week1/src/data/data_file.csv', 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        try:        
            amount = float(row['amount'])
        except ValueError:
            continue
        if(amount > 100000):
           with open('/Users/srinivasan.ashwini/Documents/fde-week1/src/data/filtered_data.csv', 'a', newline='') as filtered_file:
                writer = csv.DictWriter(filtered_file, fieldnames=reader.fieldnames)
                writer.writerow(row)    

