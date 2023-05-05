import csv

with open('office-addins.csv', newline='') as csvfile:
    reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    
    with open('addins-out.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',',quotechar='|', quoting=csv.QUOTE_MINIMAL)
        
        for row in reader:
            for x in row:
                if x == "":
                    pass
                else:
                    #writer.writerow([x.strip('@{Name=').strip('}')])
                    writer.writerow([x.strip(' ')])
                    
print("done")