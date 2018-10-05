import csv
import numpy as np
from operator import itemgetter

obj = []
#read file with delimiter line by line
with open("database.txt") as f:
    c = csv.reader(f, delimiter=' ', skipinitialspace=True)
    for line in c:
        obj.append(line)
print("All objects we have, overall %d:\n%s \n" % (len(obj), obj))


# List C which includes all dublets
C = []
for i in range(len(obj)):
    for j in range(len(obj[i])):
        C.append(obj[i][j])
print("After putting all doublets into C list:\n%s\n" % C)

# List C is sorted by a to z
C.sort()
print("After sorting all doublets in C list:\n%s\n" % C)


unique_elements, counts_elements = np.unique(C, return_counts=True)
unique_elements = np.asarray(unique_elements)
counts_elements = np.asarray(counts_elements)
# All unique doublets with its frequence
UniqueCount = []
for i in range (len(unique_elements)):
    UniqueCount.append((unique_elements[i],counts_elements[i]))
#print(unique_elements, counts_elements)
#print("Frequency of unique doublets of the said list:\n%s\n" % UniqueCount)
UniqueCount = sorted(UniqueCount, key=itemgetter(1), reverse=True)
print("Frequency of unique doublets of the said list sorted by its frequency:\n%s\n" % UniqueCount)

# S is a MVS list
S = []
for i in range(len(UniqueCount)):
    if UniqueCount[i][1] == 1:
        S.append(UniqueCount[i][0])

print(S)