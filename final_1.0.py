from __future__ import division, print_function
import csv
from datetime import datetime
import numpy as np
from operator import itemgetter


class LFP_TreeNode():
    def __init__(self, item=None, support=1):
        self.item = item  # 'Value' of the item
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
        self.tree_root = None  # The root of the initial LFP-Tree
        self.prefixes = {}
        self.frequent_itemsets = []

    # Count the number of trajectories that contains item.
    def number_trajectory(self, item, trajectories):
        counter = 0
        for trajectory in trajectories:
            if item in trajectory:
                counter += 1
        support = counter
        return support

    # Returns a set of frequent items.
    def frequent_items(self, trajectories):
        # Get all unique items in the transactions
        unique_items = set(
            item for trajectory in trajectories for item in trajectory)
        items = []
        for item in unique_items:
            sup = self.number_trajectory(item, trajectories)
            if sup >= self.k_value:
                items.append([item, sup])
        # Sort by support - Highest to lowest
        items.sort(key=lambda item: item[1], reverse=True)
        frequent_items = [[el[0]] for el in items]
        return frequent_items   # Only return the items

    # Insert all frequent items to the tree by recursive function.
    def insert_tree(self, node, children):
        if not children:
            return
        # Create new node as the first item in children list
        child_item = children[0]
        child = LFP_TreeNode(item=child_item)
        # If parent has child => append child
        if child_item in node.children:
            node.children[child.item].support += 1
        #otherwise add item as new child
        else:
            node.children[child.item] = child
        # recursive
        self.insert_tree(node.children[child.item], children[1:])

    def make_tree(self, trajectories, frequent_items=None):
        if not frequent_items:
            # Get frequent items sorted by support
            frequent_items = self.frequent_items(trajectories)
        unique_frequent_items = list(
            set(item for itemset in frequent_items for item in itemset))
        # Construct the root of the LFP-Tree
        root = LFP_TreeNode()
        # Remove items that are not frequent according to unique_frequent_items
        for trajectory in trajectories:
            trajectory = [item for item in trajectory if item in unique_frequent_items]
            trajectory.sort(key=lambda item: frequent_items.index([item]))
            self.insert_tree(root, trajectory)
        return root

    # Recursive print method
    def print_tree(self, node=None, indent_times=0):
        if not node:
            node = self.tree_root
        indent = "    " * indent_times
        print("%s%s:%s" % (indent, node.item, node.support))
        for child_key in node.children:
            child = node.children[child_key]
            self.print_tree(child, indent_times + 1)

    # Makes sure that the first item in itemset
    # is a child of node and that every following item
    # in itemset is reachable via that path
    def is_prefix(self, itemset, node):
        for item in itemset:
            if not item in node.children:
                return False
            node = node.children[item]
        return True

    # Recursive method that adds prefixes to the itemset by
    # traversing the FP Growth Tree
    def determine_prefixes(self, itemset, node, prefixes=None):
        if not prefixes:
            prefixes = []

        # If the current node is a prefix to the itemset
        # add the current prefixes value as prefix to the itemset
        if self.is_prefix(itemset, node):
            itemset_key = self.get_itemset_key(itemset)
            if not itemset_key in self.prefixes:
                self.prefixes[itemset_key] = []
            self.prefixes[itemset_key] += [{"prefix": prefixes, "support": node.children[itemset[0]].support}]

        for child_key in node.children:
            child = node.children[child_key]
            # Recursive call with child as new node. Add the child item as potential prefix.
            self.determine_prefixes(itemset, child, prefixes + [child.item])

    # Determines the look of the hashmap key for self.prefixes
    # List of more strings than one gets joined by '-'
    def get_itemset_key(self, itemset):
        if len(itemset) > 1:
            itemset_key = "-".join(itemset)
        else:
            itemset_key = str(itemset[0])
        return itemset_key

    def determine_frequent_itemsets(self, conditional_database, suffix):
        # Calculate new frequent items from the conditional database of suffix
        frequent_items = self.frequent_items(conditional_database)
        cond_tree = None

        if suffix:
            cond_tree = self.make_tree(conditional_database, frequent_items)
            # Output new frequent itemset as the suffix added to the frequent items
            self.frequent_itemsets += [el + suffix for el in frequent_items]

        # Find larger frequent itemset by finding prefixes of the frequent
        # items in the FP Growth Tree for the conditional database.
        self.prefixes = {}
        for itemset in frequent_items:
            # If no suffix (first run)
            if not cond_tree:
                cond_tree = self.tree_root
            # Determine prefixes to itemset
            self.determine_prefixes(itemset, cond_tree)
            conditional_database = []
            itemset_key = self.get_itemset_key(itemset)
            # Build new conditional database
            if itemset_key in self.prefixes:
                for el in self.prefixes[itemset_key]:
                    # If support = 4 => add 4 of the corresponding prefix set
                    for _ in range(el["support"]):
                        conditional_database.append(el["prefix"])
                # Create new suffix
                new_suffix = itemset + suffix if suffix else itemset
                self.determine_frequent_itemsets(conditional_database, suffix=new_suffix)
        #print(conditional_database)
        #print(suffix)
        #print(frequent_items)
        #print(self.frequent_itemsets)


    def find_frequent_itemsets(self, trajectories, suffix=None, show_tree=False):
        self.trajectories = trajectories
        # Build the LFP-Tree
        self.tree_root = self.make_tree(trajectories)
        if show_tree:
            print("\nLFP Tree:")
            self.print_tree(self.tree_root)

        self.determine_frequent_itemsets(trajectories, suffix=None)

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
    # print("\nAfter putting and sorting all doublets into C list:\n%s\n" % C)

    lfp_tree = LFP_Tree(k_value=k_value)

    # Get and print the frequent itemsets
    frequent_itemsets = lfp_tree.find_frequent_itemsets(trajectories, show_tree=True)
    print("Frequent itemsets:")
    for itemset in frequent_itemsets:
        print("\t%s" % itemset)

    end_time = datetime.now()
    print('\nDuration: {}'.format(end_time - start_time))
