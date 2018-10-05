class Node:

    def __init__(self, data):
        self.left = None
        self.right = None
        self.data = data
        self.freq = 0

    def insert(self, data):
    # Compare the new value with the parent node
        if self.left is None:
            self.left = Node(data)
            self.left.freq = 1
        else:
            if self.search(data) is True:
                c = 0
                self.left.freq += 1
            else:
                self.left.insert(data)

    # search method to compare the value with nodes
    def search(self, lkpval):
        if self.left is not None:
            if self.left.data is lkpval:
                #return str(lkpval) + " is found"
                return True
            else:
                return self.left.search(lkpval)

    # Print the tree
    def PrintTree(self):
        if self.left:
            self.left.PrintTree()
            #print(self.freq)
        print("%d:%d" % (self.data, self.freq)),
        #if self.right:
            #self.right.PrintTree()

# Use the insert method to add nodes
root = Node(0)
root.insert(1)
root.insert(7)
root.insert(8)
root.insert(9)
root.insert(1)
#print(root.search(5))

root.PrintTree()