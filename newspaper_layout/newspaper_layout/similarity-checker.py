import os
import csv
import sys
import logging
import ast

import math
import numpy as np
from collections import defaultdict

# logger = logging.getLogger('similarity-checker')
# logger.setLevel(logging.INFO)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("similarity-checker")

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
    similarity_values = []
    for index, snapshot in enumerate(csv_data):
        if index > 0:
            try:
                previous = csv_data[index - 1]
                previousValue = parse_cell_value(previous, column)
                currentValue = parse_cell_value(snapshot, column)
                similarity = similarity_metric (previousValue, currentValue)
                snapshot[column + 'Similarity'] = similarity
                similarity_values.append(similarity)
            except:
                snapshot[column + 'Similarity'] = -1
        else:
            snapshot[column + 'Similarity'] = -1

    similarity_csv.append(snapshot)
    return (csv_data, similarity_values)

def write_csv (filename, csv_data):
    file_obj = open(filename,"w")
    writer = csv.DictWriter(file_obj, fieldnames=csv_data[0].keys())
    writer.writeheader()
    writer.writerows(csv_data)

def get_significant_dissimilarities (sim_values):
    sim_mean = np.mean(sim_values, dtype=np.float64)
    sim_sigma = np.std(sim_values,dtype=np.float64)
    dissimilarities = []
    for sim_index, sim_val in enumerate(sim_values):
        if sim_val < (sim_mean - sim_sigma):
            dissimilarities.append((sim_index, sim_val))
    return dissimilarities

if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit('Usage: %s csvfile' % sys.argv[0])

    if not os.path.exists(sys.argv[1]):
        sys.exit('ERROR: csv file %s was not found!' % sys.argv[1])

    in_file = sys.argv[1]
    csv_data = read_csv(in_file)
    (similarity_csv, cssSimilarity) = calculate_similarity(csv_data, 'nodeUsedCSSClassAttributesList', jaccard)
    (similarity_csv, fontSimilarity) = calculate_similarity(similarity_csv, 'textUniqueFonts', euclidian)
    (similarity_csv, imageDimSimilarity) = calculate_similarity(similarity_csv, 'imageUniqueDimensionss', euclidian)
    (similarity_csv, fontSizeSimilarity) = calculate_similarity(similarity_csv, 'textUniqueFontSizes', euclidian)

    # find out all snapshot urls with more than 1 significant dissimilarity
    all_sims = [cssSimilarity,fontSimilarity, imageDimSimilarity,fontSizeSimilarity]
    dis_sim_count = defaultdict(int)
    for sim in all_sims:
        dis_sims = get_significant_dissimilarities(sim)
        for dis_sim in dis_sims:
            dis_sim_count[dis_sim[0]] += 1


    min_2_dissimilar = [pos for pos, count in dis_sim_count.items() if count > 1]
    dissimilar_urls = []
    for index in min_2_dissimilar:
        difference_url = similarity_csv[index].get('snapshotURL')
        previous_url = similarity_csv[index -1].get('snapshotURL')
        dissimilar_urls.append(difference_url)

    screenshot_file = os.path.split(in_file)[0] + os.path.sep + 'difference_screenshots.txt'
    screenshot_f = open(screenshot_file,"w")
    for url in dissimilar_urls:
        screenshot_f.write("%s \n" % url)

    out_file = os.path.splitext(in_file)[0] + '_similarity.csv'
    write_csv(out_file, similarity_csv)