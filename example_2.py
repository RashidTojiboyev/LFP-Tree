from __future__ import division, print_function
import csv
from datetime import datetime
import numpy as np
from operator import itemgetter


class LFP_TreeNode():
    def __init__(self, item=None, support=1):
        self.item = item    # 'Value' of the item
        self.support = support  # Number of times the item occurs in a transaction
        self.children = {}  # Child nodes in the FP Growth Tree

class LFP_Tree():

    """A method for determining frequent itemsets in a trajectory database.
    This is done by building a so called LFP-Tree, which can then be mined
    to collect the frequent itemsets.

    Parameters:
    -----------
    Threshold value, K = : float
    """

    def __init__(self, k_value=2):
        self.k_value = k_value  # Threshold value
        self.tree_root = None   # The root of the initial LFP-Tree
        self.prefixes = {}
        self.frequent_itemsets = []

    # Count the number of trajectories that contains item.
    def number_trajectory (self, item, trajectories):
        counter = 0
        for trajectory in trajectories:
            if item in trajectory:
                counter += 1
        support = counter
        return support

    # Returns a set of frequent items.
    def _get_frequent_items(self, trajectories):
        unique_items = set(
            item for trajectory in trajectories for item in trajectory)
        items = []
        for item in unique_items:
            sup = self.number_trajectory(item, trajectories)
            if sup >= self.k_value:
                items.append([item, sup])
        items.sort(key=lambda item: item[1], reverse=True)
        frequent_items = [[el[0]] for el in items]
        return frequent_items

    def _insert_tree(self, node, children):
        if not children:
            return
        child_item = children[0]
        child = LFP_TreeNode(item=child_item)
        if child_item in node.children:
            node.children[child.item].support += 1
        else:
            node.children[child.item] = child
        self._insert_tree(node.children[child.item], children[1:])

    def _construct_tree(self, trajectories, frequent_items=None):
        if not frequent_items:
            frequent_items = self._get_frequent_items(trajectories)
        unique_frequent_items = list(
            set(item for itemset in frequent_items for item in itemset))
        root = LFP_TreeNode()
        for trajectory in trajectories:
            trajectory = [item for item in trajectory if item in unique_frequent_items]
            trajectory.sort(key=lambda item: frequent_items.index([item]))
            self._insert_tree(root, trajectory)
        return root

    def print_tree(self, node=None, indent_times=0):
        if not node:
            node = self.tree_root
        indent = "    " * indent_times
        print("%s%s:%s" % (indent, node.item, node.support))
        for child_key in node.children:
            child = node.children[child_key]
            self.print_tree(child, indent_times + 1)

    def _is_prefix(self, itemset, node):
        for item in itemset:
            if not item in node.children:
                return False
            node = node.children[item]
        return True

    def _determine_prefixes(self, itemset, node, prefixes=None):

        if not prefixes:
            prefixes = []

        if self._is_prefix(itemset, node):
            itemset_key = self._get_itemset_key(itemset)
            if not itemset_key in self.prefixes:
                self.prefixes[itemset_key] = []
            self.prefixes[itemset_key] += [{"prefix": prefixes, "support": node.children[itemset[0]].support}]

        for child_key in node.children:
            child = node.children[child_key]
            self._determine_prefixes(itemset, child, prefixes + [child.item])

    def _get_itemset_key(self, itemset):
        if len(itemset) > 1:
            itemset_key = "-".join(itemset)
        else:
            itemset_key = str(itemset[0])
        return itemset_key

    def _determine_frequent_itemsets(self, conditional_database, suffix):

        frequent_items = self._get_frequent_items(conditional_database)
        cond_tree = None

        if suffix:
            cond_tree = self._construct_tree(conditional_database, frequent_items)
            self.frequent_itemsets += [el + suffix for el in frequent_items]

        self.prefixes = {}
        for itemset in frequent_items:
            if not cond_tree:
                cond_tree = self.tree_root
            self._determine_prefixes(itemset, cond_tree)
            conditional_database = []
            itemset_key = self._get_itemset_key(itemset)
            if itemset_key in self.prefixes:
                for el in self.prefixes[itemset_key]:
                    for _ in range(el["support"]):
                        conditional_database.append(el["prefix"])
                new_suffix = itemset + suffix if suffix else itemset
                self._determine_frequent_itemsets(conditional_database, suffix=new_suffix)

    def find_frequent_itemsets(self, trajectories, suffix=None, show_tree=False):
        self.trajectories = trajectories

        self.tree_root = self._construct_tree(trajectories)
        if show_tree:
            print("\nLFP Tree:")
            self.print_tree(self.tree_root)

        self._determine_frequent_itemsets(trajectories, suffix=None)

        return self.frequent_itemsets

if __name__ == "__main__":

    start_time = datetime.now()

    trajectories = []
    # read file with delimiter line by line
    with open("database.txt") as f:
        c = csv.reader(f, delimiter=' ', skipinitialspace=True)
        for line in c:
            trajectories.append(line)

    print("LFP-Tree")
    k_value = 2
    print("Threshold value, K = %s\n" % k_value)
    print("trajectories:")
    for trajectory in trajectories:
        print("\t%s" % trajectory)

    # List C which includes all dublets
    C = []
    for i in range(len(trajectories)):
        for j in range(len(trajectories[i])):
            C.append(trajectories[i][j])
    C.sort()
    #print("\nAfter putting and sorting all doublets into C list:\n%s\n" % C)

    unique_elements, counts_elements = np.unique(C, return_counts=True)
    unique_elements = np.asarray(unique_elements)
    counts_elements = np.asarray(counts_elements)
    # All unique doublets with its frequence
    UniqueCount = []
    for i in range(len(unique_elements)):
        UniqueCount.append((unique_elements[i], counts_elements[i]))
    # print(unique_elements, counts_elements)
    # print("Frequency of unique doublets of the said list:\n%s\n" % UniqueCount)
    #UniqueCount = sorted(UniqueCount, key=itemgetter(1), reverse=True)

    UniqueCount = sorted(UniqueCount, key=itemgetter(1), reverse=True)
    print("\nFrequency of unique doublets of the said list sorted by its frequency:\n%s\n" % UniqueCount)

    lfp_tree = LFP_Tree(k_value=k_value)

    # Get and print the frequent itemsets
    frequent_itemsets = lfp_tree.find_frequent_itemsets(trajectories, show_tree=True)
    print("Frequent itemsets:")
    for itemset in frequent_itemsets:
        print("\t%s" % itemset)

    end_time = datetime.now()
    print('\nDuration: {}'.format(end_time - start_time))
