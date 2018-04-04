# -*- coding: utf-8 -*-
"""
Module to compute the top k tuples according to preferences
Algorithms optimized using preference partition method
"""

from cp_theory import CPTheory
from cp_most_preferred_partition import get_tuple_id


def buildk_partitions(result_list, attributes_set):
    """Build a partition set over tuples based on 'attribute_set'

    For each value combination of attributes 'attributes_set',
    a partition is created"""
    partitions = {}
    # Check if 'attribute_set' is empty
    if len(attributes_set) == 0:
        partitions[()] = result_list
    else:
        for tup_dict in result_list:
            tup = tup_dict['tuple']
            # Get an 'id' to 'tup'
            tup_id = get_tuple_id(tup, attributes_set)
            # Check if partition already exists
            if tup_id in partitions:
                partitions[tup_id].append(tup_dict)
            else:
                partitions[tup_id] = [tup_dict]
    return partitions


def bestk_direct(result_list, comparison):
    """Change levels of tuples in 'result_list' partition
     according to 'comparison'"""
    not_preferred_list = []
    dominated = False
    for tup_dict in result_list:
        tup = tup_dict['tuple']
        # Check if tuple is preferred
        if comparison.preferred(tup):
            dominated = True
        # Check if tuple is incomparable
        elif comparison.not_preferred(tup):
            not_preferred_list.append(tup_dict)
    # Check if some tuple was dominated
    if dominated:
        # Update levels of dominated tuples
        for tup_dict in not_preferred_list:
            tup_dict['level'] += 1


def bestk_partition(result_list, comparisom):
    """Change levels of tuples in 'result_list' according to 'comparison'"""
    tup_dict = result_list[0]
    # Tuple attributes
    tuples_att_set = set(tup_dict['tuple'].keys())
    # Attributes of tuples not present in 'comparison'
    att_set = tuples_att_set.difference(comparisom.preference_att_set())
    partitions = buildk_partitions(result_list, att_set)
    # Update levels in each partition
    for tup_id in partitions:
        bestk_direct(partitions[tup_id], comparisom)


def mostk_preferred_partition(preference_rules, k, tuples_list):
    """Return dominant tuples from 'tuples_list'
    according to 'preference_rules'"""
    # Create a cp-theory to compare tuples
    cpt = CPTheory(preference_rules)
    # Temporary list
    temp_list = []
    # Build a structure of tuples and their levels
    for tup in tuples_list:
        tup_dict = {}
        tup_dict['level'] = 0
        tup_dict['tuple'] = tup
        temp_list.append(tup_dict)
    # Current level of tuples to be get
    level = 0
    # Number of tuples ready
    num_tuples_ready = 0
    # List of tuple by level
    tuples_by_level_dict = {}
    # Process 'temp_list' until all level will be explored
    # Or 'k' tuples are ready
    while len(temp_list) > 0 and num_tuples_ready < k:
        # Initialize list of tuples in level 'level'
        tuples_by_level_dict[level] = []
        # Process comparisons over 'temp_list'
        for comp in cpt.comparisons_list:
            bestk_partition(temp_list, comp)
        # Copy list of 'temp_list'
        copy_list = [tup_dict for tup_dict in temp_list]
        temp_list = []
        # Tuples if level > 'level' (not ready) remain in 'temp_list'
        for tup_dict in copy_list:
            # If tuple level = 'level' then tuple is ready
            if tup_dict['level'] == level:
                tuples_by_level_dict[level].append(tup_dict['tuple'])
                num_tuples_ready += 1
            else:
                tup_dict['level'] = level + 1
                temp_list.append(tup_dict)
        level += 1

    result = []
    current_level = 0
    # Return only k tuples required
    while len(result) < k and len(result) < len(tuples_list):
        result += tuples_by_level_dict[current_level]
        current_level += 1
    if len(result) > k:
        result = result[:k]
    del cpt
    return result
