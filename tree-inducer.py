"""
Tree-inducer file. This is a program that takes a data file as input, and creates a decision tree.

@author Ben Scarbrough
"""

import sys
import math


file_name = None
file_contents = None
tuning_set = None
which_issue = None


def main():
    """
    This is the main function. To run use type "python3 tree-inducer.py 'name of data file'" in command line.
    """
    # If the program is given more than one argument (2 because python takes the program as the first argument) exit.
    if len(sys.argv) > 3 or len(sys.argv) < 3:
        print("This program takes two arguments, the name of the name of the data file and the issue to predict.")
        sys.exit(0)
    elif int(sys.argv[2]) == 0:
        print("Please enter an issue greater than zero.")
        sys.exit(0)
    else:
        # Grab the name of the file and pass it to _read_file.
        file_name = sys.argv[1]
        which_issue = int(sys.argv[2]) - 1
        file_contents = _read_file(file_name)

    tuning_set = _make_tuning_set(file_contents)
    # print(tuning_set)
#   temp = _decision_tree(tuning_set, parent)
    temp = _determine_rep(tuning_set, int(which_issue))
#   temp = _seperate_on_issue(tuning_set, 0)
    print(temp)


def _read_file(file_name):
    """
    This function reads the file and returns it as a 2d tuple.
    """
    try:
        file = open(file_name, "r") # Try to open the file, if it doesn;t exist throw an error.
    except:
        # Print the error and exit.
        print(str("The file " + file_name + " does not exist."))
        sys.exit(0)

    temp_list = [] # Make a temporary list
    content = file.readlines() # Read all the lines of the file.
    for line in content: # For every line of the file
        temp = line.split() # Split the file at whitespace.
        temp_list.append((temp[0], temp[1], temp[2])) # Assuming the data only has 3 indexes (which the voting-data.tsv file does, add each piece.)

    return tuple(map(tuple, temp_list)) # Return the list in tuple form


def _make_tuning_set(set):
    """
    Create the tuning set.
    """
    temp_list = []
    i = 0

    while i <= len(set):
        if i > len(set): # If the i value is greater than the length, break out.
            return tuple(map(tuple, temp_list))
        temp_list.append(set[i])
        i += 4

    return tuple(map(tuple, temp_list))


def _calculate_entropy(parent, set_a, set_b, set_c):
    """
    Calculate the entropy of the subsets.
    """
    len_parent = len(parent)
    parent_reps = _num_reps(parent)
    a_reps = _num_reps(set_a) # Get the reps in set a
    b_reps = _num_reps(set_b) # Get the reps in set b
    c_reps = _num_reps(set_c) # get the reps in set c

    entropy_a = (len(set_a)/len_parent) * _prob_log(a_reps) # calculate the entropy of a
    entropy_b = (len(set_b)/len_parent) * _prob_log(b_reps) # calculate the entropy of b
    entropy_c = (len(set_c)/len_parent) * _prob_log(c_reps) # calculate the entropy of c

    return _prob_log(parent_reps) - (entropy_a + entropy_b + entropy_c) # return the total entropy.


def _num_reps(set):
    """
    Counts the number of republicans/ democrats in the given set. Stores democrats at [0] and republicans at [1], and the total length at [2].
    """
    temp_list = []
    num_d = 0 # num democrats
    num_r = 0 # num republicans

    for i in range(len(set)):
        if set[i][1] == 'D':
            num_d += 1
        elif set[i][1] == 'R':
            num_r += 1

    temp_list.append(num_d)
    temp_list.append(num_r)
    temp_list.append(len(set))

    return temp_list


def _take_log(num):
    """
    A function to take the log, making sure not to take the log of zero.
    """
    if num == 0:
        return 0
    return math.log(num, 2) # Log base 2


def _get_probability(reps, length):
    if length == 0:
        return 0
    return reps/length


def _prob_log(set):
    """
    -p(D)logp(D) - p(R)logp(R)
    """
    d_prob = _get_probability(set[0], set[2]) # calculate the probability of democrats
    r_prob = _get_probability(set[1], set[2]) # calculate the probability of republicans
    return -d_prob * _take_log(d_prob) - r_prob * _take_log(r_prob)


def _decision_tree(set, parent):
    """
    The decision tree algorithm.
    """
    gain = 0
    issue_index = 0

    for i in range(len(set[2])):
        sides = _seperate_on_issue(set, i)
        entropy = _calculate_entropy(set, sides[0], sides[1], sides[2])
        if entropy > gain:
            gain = entropy
            issue_index = i

    if gain > 0:
        split = _seperate_on_issue(set, issue_index)
        for i in split:
            node = _determine_rep(i, issue_index)
            parent.append(node)
            _decision_tree(i, parent)
            return set
    else:
        return set


def _get_issue_votes(set, issue):
    """
    Returns a set of all the votes on the given issue.
    """
    temp_list = []
    for i in range(len(set)):
        temp = set[i][2]
        try: temp_list.append(temp[issue]) # Split the list based on the issue, a, b, c, etc.
        except:
            print("That issue does not exist.")
            sys.exit(0)
            
    return temp_list


def _seperate_on_issue(set, issue):
    """
    Seperate the issue into +, -, and .

    Return three different lists, [0] is +, [1] is =, [2] is .
    """
    votes = _get_issue_votes(set, issue)
    aye = []
    nay = []
    abstain = []

    for i in range(len(set)):
        if votes[i] == '+':
            aye.append(set[i])
        if votes[i] == '-':
            nay.append(set[i])
        if votes[i] == '.':
            abstain.append(set[i])
    return aye, nay, abstain


def _determine_rep(set, issue):
    """
    Determines how a rep will vote based on the set. Ex. If majority of dems voted yea, it is likely some unclassified dem will vote yea.
    """
    reps = _num_reps(set)
    votes = _get_issue_votes(set, issue)

    yea = None
    nay = None
    abstain = None

    #Yea's
    dem_yea = 0
    rep_yea = 0
    # Nay's
    dem_nay = 0
    rep_nay = 0
    # Abstains
    dem_abs = 0
    rep_abs = 0

    # All the checks
    for i in range(len(set)):
        # Check yea's
        if set[i][1] == 'D' and votes[i] == '+':
            dem_yea += 1
            continue
        elif set[i][1] == 'R' and votes[i] == '+':
            rep_yea += 1
            continue

        # Check Nay's
        if set[i][1] == 'D' and votes[i] == '-':
            dem_nay += 1
            continue
        elif set[i][1] == 'R' and votes[i] == '-':
            rep_nay += 1
            continue

        # Check Abstains
        if set[i][1] == 'D' and votes[i] == '.':
            dem_abs += 1
            continue
        elif set[i][1] == 'R' and votes[i] == '.':
            rep_abs += 1
            continue

    # Check totals and return the correct set.
    if dem_yea  > rep_yea:
        yea = "+ D"
    else:
        yea = "+ R"

    if dem_nay  > rep_nay:
        nay = "- D"
    else:
        nay = "- R"

    if dem_abs  > rep_abs:
        abstain = ". D"
    else:
        abstain = ". R"

    return yea, nay, abstain


# Put at the bottom, runs the program from main.
if __name__ == "__main__":
    main()



class Node:
    """
    The node class.
    """

    def __init__(self, node, parent):
        """
        Initialize the node class.
        """
        self.node = node
        self.parent = parent
        self.isLeaf = False
        self.children = None
        self.party = None
        self.vote = None


    def _check_if_leaf(self, node):
        """
        Check if the node is a leaf.
        """
        return self.isLeaf


    def _set_leaf(self, status):
        """
        Set the leaf value of a node.
        """
        self.isLeaf = status


    def _get_parent(self, node):
        """
        Get the parent of a node.
        """
        return self.parent
