from __future__ import division, print_function
import pandas as pd
import numpy as np
import itertools


class LFP_TreeNode():
    def __init__(self, item=None, support=1):
        self.item = item
        self.support = support
        self.children = {}

class LFP_Tree():

    def __init__(self, min_sup=0.3):
        self.min_sup = min_sup
        self.tree_root = None
        self.prefixes = {}
        self.frequent_itemsets = []

    def _calculate_support(self, item, transactions):
        count = 0
        for transaction in transactions:
            if item in transaction:
                count += 1
        support = count
        return support

    def _get_frequent_items(self, transactions):
        # Get all unique items in the transactions
        unique_items = set(
            item for transaction in transactions for item in transaction)
        items = []
        for item in unique_items:
            sup = self._calculate_support(item, transactions)
            if sup >= self.min_sup:
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

    def _construct_tree(self, transactions, frequent_items=None):
        if not frequent_items:
            frequent_items = self._get_frequent_items(transactions)
        unique_frequent_items = list(
            set(item for itemset in frequent_items for item in itemset))
        root = LFP_TreeNode()
        for transaction in transactions:
            transaction = [item for item in transaction if item in unique_frequent_items]
            transaction.sort(key=lambda item: frequent_items.index([item]))
            self._insert_tree(root, transaction)
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

    def find_frequent_itemsets(self, transactions, suffix=None, show_tree=False):
        self.transactions = transactions

        self.tree_root = self._construct_tree(transactions)
        if show_tree:
            print("LFP Tree:")
            self.print_tree(self.tree_root)

        self._determine_frequent_itemsets(transactions, suffix=None)

        return self.frequent_itemsets

def main():
    transactions = [['s3', 's2', 'n6', 's4', 's5'],
               ['s3', 'n6', 'e4', 'e5'],
               ['s3','s2','e4','e5'],
               ['s3', 's2', 'n6'],
               ['s3', 's2', 'n6', 's4', 's5']]

    print("- LFP-Tree -")
    min_sup = 2
    print("Minimum Support: %s" % min_sup)
    print("Transactions:")
    for transaction in transactions:
        print("\t%s" % transaction)

    lfp_tree = LFP_Tree(min_sup=min_sup)

    # Get and print the frequent itemsets
    frequent_itemsets = lfp_tree.find_frequent_itemsets(
        transactions, show_tree=True)
    print("Frequent itemsets:")
    for itemset in frequent_itemsets:
        print("\t%s" % itemset)


if __name__ == "__main__":
    main()