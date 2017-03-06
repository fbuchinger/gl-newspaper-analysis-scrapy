import os
import csv
import sys
import logging
import ast

import math

# logger = logging.getLogger('similarity-checker')
# logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO)

def read_csv(filename):
    csv_data = csv.DictReader(open(filename, "r"), delimiter=",")
    return sorted(csv_data, key=lambda row: row['requested_url'], reverse=False)

def jaccard (list1, list2):
    union = list(set(list1) | set(list2))
    intersection = list(set(list1) & set(list1))
    jaccard = float(len(intersection)) / float(len(union))
    return jaccard

def normalize_dict (val_dict):
    norm = [float(val_dict[key]) / sum(val_dict.values()) for key in val_dict.keys()]
    return dict(zip(val_dict.keys(),norm))

# http://stackoverflow.com/questions/38369742/calculate-euclidean-distance-from-dicts-sklearn
def euclidian(dict1, dict2):
    dict1 = normalize_dict(dict1)
    dict2 = normalize_dict(dict2)
    euclidian = math.sqrt(sum((dict1.get(d, 0) - dict2.get(d, 0)) ** 2 for d in set(dict1).union(set(dict2))))
    return 1 - euclidian #the closer the values, the more similar

def parse_cell_value(csv_row, column_name):
    if column_name.endswith("List"):
        return csv_row[column_name].split(',')
    else:
        col_data = csv_row[column_name]
        return ast.literal_eval(col_data.replace('u"','u').replace('":',':'))

def calculate_similarity(csv_data, column, similarity_metric):
    similarity_csv = []
    for index, snapshot in enumerate(csv_data):
        if index > 0:
            try:
                previous = csv_data[index - 1]
                previousValue = parse_cell_value(previous, column)
                currentValue = parse_cell_value(snapshot, column)
                snapshot[column + 'Similarity'] = similarity_metric (previousValue, currentValue)
            except:
                snapshot[column + 'Similarity'] = -1
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
    similarity_csv = calculate_similarity(csv_data, 'nodeUsedCSSClassAttributesList', jaccard)
    similarity_csv = calculate_similarity(similarity_csv, 'textUniqueFonts', euclidian)
    similarity_csv = calculate_similarity(similarity_csv, 'imageUniqueDimensionss', euclidian)
    similarity_csv = calculate_similarity(similarity_csv, 'textUniqueFontSizes', euclidian)
    out_file = os.path.splitext(in_file)[0] + '_similarity.csv'
    write_csv(out_file, similarity_csv)