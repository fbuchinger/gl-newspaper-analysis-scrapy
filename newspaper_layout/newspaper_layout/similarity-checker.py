import os
import csv
import sys
import logging

# logger = logging.getLogger('similarity-checker')
# logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO)

def read_csv(filename):
    csv_data = csv.DictReader(open(filename, "r"), delimiter=",")
    return sorted(csv_data, key=lambda row: row['requested_url'], reverse=False)

def calculate_similarity(csv_data, column):
    similarity_csv = []
    for index, snapshot in enumerate(csv_data):
        if index > 0:
            previous = csv_data[index - 1]
            previousClassList = previous[column].split(',')
            currentClassList = snapshot[column].split(',')
            union = list(set(previousClassList) | set(currentClassList))
            intersection = list(set(previousClassList) & set(currentClassList))
            jaccard_index = float(len(intersection))/float(len(union))
            snapshot[column + 'Similarity'] = jaccard_index
            logging.info(previousClassList)
            logging.info(currentClassList)
            print("Similarity between %s and %s: %s" % (previous['snapshotURL'],snapshot['snapshotURL'], jaccard_index))
        else:
            snapshot[column + 'Similarity'] = -1

    similarity_csv.append(snapshot)
    return csv_data

def write_csv (filename, csv_data):
    file_obj = open(filename,"w")
    writer = csv.DictWriter(file_obj, fieldnames=csv_data[0].keys())
    writer.writeheader()
    writer.writerows(csv_data)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: %s csvfile' % sys.argv[0])

    if not os.path.exists(sys.argv[1]):
        sys.exit('ERROR: csv file %s was not found!' % sys.argv[1])

    in_file = sys.argv[1]
    csv_data = read_csv(in_file)
    similarity_csv = calculate_similarity(csv_data, 'nodeUsedCSSClassAttributesList')
    out_file = os.path.splitext(in_file)[0] + '_similarity.csv'
    write_csv(out_file, similarity_csv)