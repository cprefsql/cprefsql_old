# -*- coding: utf-8 -*-
"""
Module to compute the best tuples according to preferences
Algorithms optimized using preference partition method
"""

from cp_theory import CPTheory


def get_tuple_id(tup, attributes_set):
    """Get a list of values for attributes 'attributes_set' over tuple 'tup'"""
    att_list = []
    for att in attributes_set:
        att_list.append(tup[att])
    return tuple(att_list)


def build_partitions(tuples_list, attributes_set):
    """Build a partition set over 'tuples_list' based on 'attribute_set'

    For each value combination of attributes 'attributes_set' over
    'tuples_list', a partition is created"""
    partitions = {}
    # Check if 'attribute_set' is empty
    if len(attributes_set) == 0:
        partitions[()] = tuples_list
    else:
        for tup in tuples_list:
            # Get an 'id' to 'tup'
            tup_id = get_tuple_id(tup, attributes_set)
            # Check if partition already exists
            if tup_id in partitions:
                partitions[tup_id].append(tup)
            else:
                partitions[tup_id] = [tup]
    return partitions


def best_direct(tuples_list, comparison):
    """Get dominant tuples of partition 'tuples_list'
    according to 'comparison'"""
    preferred_list = []
    incomparable_list = []
    for tup in tuples_list:
        # Check if tuple is preferred
        if comparison.preferred(tup):
            preferred_list.append(tup)
        # Check if tuple is incomparable
        elif not comparison.not_preferred(tup):
            incomparable_list.append(tup)
    # Check if there no exists preferred tuples
    if preferred_list == []:
        return tuples_list
    else:
        # Return dominant tuples (preferred and incomparable)
        return preferred_list + incomparable_list


def best_partition(tuples_list, comparisom):
    """Get dominant tuples from 'tuples_list'
    according to 'comparison'"""
    result_list = []
    # Tuple attributes
    tuples_att_set = set(tuples_list[0].keys())
    # Attributes of tuples not present in 'comparison'
    att_set = tuples_att_set.difference(comparisom.preference_att_set())
    partitions = build_partitions(tuples_list, att_set)
    # Get dominant tuples in each partition according to 'comparison'
    for tup_id in partitions:
        result_list += best_direct(partitions[tup_id], comparisom)
    return result_list


def most_preferred_partition(preference_rules, tuples_list):
    """Return dominant tuples from 'tuples_list'
    according to 'preference_rules'"""
    # Create a cp-theory to compare tuples
    cpt = CPTheory(preference_rules)
    best_list = tuples_list
    if len(best_list):
        # Get dominant tuples from 'best_list' according to each comparison
        for comp in cpt.comparisons_list:
            best_list = best_partition(best_list, comp)
    del cpt
    return best_list
