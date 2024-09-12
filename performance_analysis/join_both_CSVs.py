# join both CSVs if they have the same number of rows
import csv

def join_csvs(csv1, csv2):
    with open(csv1, 'r') as csvfile1, open(csv2, 'r') as csvfile2:
        reader1 = csv.reader(csvfile1)
        reader2 = csv.reader(csvfile2)
        with open('performance_analysis/joined.csv', 'w', newline='') as joined_csv:
            writer = csv.writer(joined_csv)
            for row1, row2 in zip(reader1, reader2):
                writer.writerow(row1 + row2)

join_csvs('performance_analysis/request_results.csv', 'performance_analysis/resource_usage.csv')