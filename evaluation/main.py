import csv
import numpy as np
import matplotlib.pyplot as plt


filename = "pair-chris.csv"

filters = []
intensities = []
f_i = []

with open(filename, 'r') as csvfile:
    # creating a csv reader object
    csvreader = csv.reader(csvfile)

    # extracting field names through first row
    fields = next(csvreader)

    # extracting each data row one by one
    for row in csvreader:
        f_i.append([row[7], int(row[8])])
        intensities.append(int(row[8]))

filter_results = []
ints = [0, 25, 50, 75, 100]

filter_results = dict({"OG": [], "Clarendon": [], "Juno": [], "Lark": []})

for filter_type in filter_results.keys():
    for intensity in ints:
        count = 0

        for row in f_i:
            if row[0] == filter_type and row[1] == intensity:
                count += 1

        filter_results[filter_type].append(count)


total_results = []
np_ints = np.asarray(intensities)
for i in ints:
    total_results.append(np.count_nonzero(np_ints == i))



labels = ["0", "25", "50", "75", "100"]
print(filter_results["OG"])
x = np.arange(len(labels))  # the label locations
width = 0.15  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - 2*width, filter_results["OG"], width, label='Original')
rects5 = ax.bar(x - width, total_results, width, color="blue", label='Total')
rects2 = ax.bar(x, filter_results["Clarendon"], width, label='Clarendon')
rects3 = ax.bar(x + width, filter_results["Lark"], width, label='Lark')
rects4 = ax.bar(x + 2*width, filter_results["Juno"], width, label='Juno')



# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend()

# ax.bar_label(rects1, padding=3)
# ax.bar_label(rects2, padding=3)

fig.tight_layout()

plt.show()
