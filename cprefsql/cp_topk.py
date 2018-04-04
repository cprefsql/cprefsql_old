# -*- coding: utf-8 -*-
"""
Module to compute the best tuples according to preferences
"""

from cp_theory import CPTheory


def mostk_preferred(preference_rules, k, tuples_list):
    """Return dominant tuples from 'tuples_list'
    according to 'preference_rules'"""

    # Create a cp-theory to compare tuples
    cpt = CPTheory(preference_rules)

    # Suppose level 0 to all tuples
    level = {key: 0 for key in range(len(tuples_list))}

    # TODO: Can be improved: computing level 0, follows level 1, so on

    # While happens change in levels
    change = True
    max_level = 0
    while change:
        change = False
        # Compare pairs of tuples
        # Outer loop for 'tup_processed'
        for idx_processed, tup_processed in enumerate(tuples_list):
            # Inner loop for 'tup_compared'
            for idx_compared in range(idx_processed + 1, len(tuples_list)):
                tup_compared = tuples_list[idx_compared]
                # Update levels, if it was necessary
                if cpt.datalog_dominates(tup_processed, tup_compared):
                    if level[idx_compared] < level[idx_processed] + 1:
                        level[idx_compared] = level[idx_processed] + 1
                        max_level = max(max_level, level[idx_compared])
                        change = True
                if cpt.datalog_dominates(tup_compared, tup_processed):
                    if level[idx_processed] < level[idx_compared] + 1:
                        level[idx_processed] = level[idx_compared] + 1
                        max_level = max(max_level, level[idx_processed])
                        change = True
    # Create a list of lists, one list for each level
    level_list = [[] for num_level in range(max_level + 1)]

    # Place tuples in correct level list
    for index, tup in enumerate(tuples_list):
        num_level = level[index]
        level_list[num_level].append(tup)

    result = []
    current_level = 0
    # Return only k tuples required
    while len(result) < k and len(result) < len(tuples_list):
        result += level_list[current_level]
        current_level += 1

    if len(result) > k:
        result = result[:k]

    del cpt
    return result
