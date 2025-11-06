#for file by file
# do radon hal . > halstead_metrics.txt
# for all file aggregate
# run this code,
# which basically compiles all the results, which were output by radon to a json file

import json
import math

with open("hal.json", "r") as f:
    data = json.load(f)

total_h1 = 0
total_h2 = 0
total_N1 = 0
total_N2 = 0

for file_metrics in data.values():
    # aggregate per file 'total'
    file_total = file_metrics.get("total", {})
    total_h1 += file_total.get("h1", 0)
    total_h2 += file_total.get("h2", 0)
    total_N1 += file_total.get("N1", 0)
    total_N2 += file_total.get("N2", 0)

vocabulary = total_h1 + total_h2
length = total_N1 + total_N2
length_derived = total_h1 * (0 if total_h2==0 else total_N2)  # optional
volume = length * (0 if vocabulary==0 else math.log2(vocabulary))

print("=== Aggregate Halstead Metrics ===")
print("n1:", total_h1)
print("n2:", total_h2)
print("N1:", total_N1)
print("N2:", total_N2)
print("vocabulary:", vocabulary)
print("length:", length)
print("volume:", volume)
