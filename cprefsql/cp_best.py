# -*- coding: utf-8 -*-
"""
Module to compute the best tuples according to preferences
"""

from cp_theory import CPTheory


def most_preferred(preference_rules, tuples_list):
    """Return dominant tuples from 'tuples_list'
    according to 'preference_rules'"""

    # Create a cp-theory to compare tuples
    cpt = CPTheory(preference_rules)
    # Suppose all tuples will be returned
    # When a position is 'False' the respective tuple is dominated
    # and not will be returned
    return_list = [True] * len(tuples_list)

    # Test if each tuple is dominated by another
    # If no, the tuple is returned
    # Outer loop for 'tup_processed'
    for idx_processed, tup_processed in enumerate(tuples_list):
        if return_list[idx_processed]:
            # Inner loop for 'tup_compared'
            for idx_compared in range(idx_processed + 1, len(tuples_list)):
                # Check if tup_compared is already dominated by another
                if return_list[idx_compared]:
                    tup_compared = tuples_list[idx_compared]
                    # Check if 'tup_compared' dominates 'tup_processed'
                    if cpt.datalog_dominates(tup_compared, tup_processed):
                        return_list[idx_processed] = False
                        break
                    # Check if 'tup_processed' dominates 'tup_compared'
                    elif cpt.datalog_dominates(tup_processed, tup_compared):
                        return_list[idx_compared] = False
    # Build result list
    result_list = []
    for idx, returned in enumerate(return_list):
        # Check it tuple has to be returned
        if returned:
            result_list.append(tuples_list[idx])
    del cpt
    return result_list
