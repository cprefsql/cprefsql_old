# -*- coding: utf-8 -*-
"""
Module to manipulate intervals in tuple format

Examples:
    a1 < A < a2 is represented as (a1, '<', '<', a2)
    A = a1 id represented as (a1, '=', '=', a1)
    A < a1 is represented as ('', '', '<', a1)
    A > a1 is represented as (a1, '<', '', '')
"""


def __left_equal(interval1, interval2):
    """
    Check if 'interval1' left limit is equal 'interval2' left limit
    """
    if interval1[1] == interval2[1] and interval1[0] == interval2[0]:
        return True
    elif interval1[1] in ('=', '<=') and interval2[1] in ('=', '<=') \
    and interval1[0] == interval2[0]:
        return True
    else:
        return False


def __right_equal(interval1, interval2):
    """
    Check if 'interval1' right limit is equal 'interval2' right limit
    """
    if interval1[2] == interval2[2] and interval1[3] == interval2[3]:
        return True
    elif interval1[2] in ('=', '<=') and interval2[2] in ('=', '<=') \
    and interval1[3] == interval2[3]:
        return True
    else:
        return False


def __left_after(interval1, interval2):
    """
    Check if 'interval1' left limit is after or equal 'interval2' left limit
    """
    # interval1: |---
    # interval2: <---
    if interval2[1] == '' and interval1[1] != '':
        return True
    # interval1:  |---
    # interval2: |---
    elif interval2[1] in ('<', '<=') and interval1[1] in ('<', '<=', '=') \
    and interval2[0] < interval1[0]:
        return True
    # interval1: []---
    # interval2:  |---
    elif interval2[1] == '<=' and interval1[1] == '<' \
    and interval2[0] == interval1[0]:
        return True
    else:
        return False


def __right_before(interval1, interval2):
    """
    Check if 'interval1' right limit is before or equal 'interval2' right limit
    """
    # interval1: ---|
    # interval2: --->
    if interval2[2] == '' and interval1[2] != '':
        return True
    # interval1: ---|
    # interval2:  ---|
    elif interval2[2] in ('<', '<=') and interval1[2] in ('<', '<=', '=') \
    and interval2[3] > interval1[3]:
        return True
    # interval1: ---[]
    # interval2: ---|
    elif interval2[2] == '<=' and interval1[2] == '<' \
    and interval2[3] == interval1[3]:
        return True
    else:
        return False


def __right_after_equal_left(interval1, interval2):
    """
    Check if 'interval1' right limit is after or equal 'interval2' left limit
    """
    # interval1: ---|
    # interval2:  |---
    if interval1[2] != '' and interval2[1] != '' \
    and interval1[3] > interval2[0]:
        return True
    # interval1: ---|
    # interval2: <---
    elif interval1[2] != '' and interval2[1] == '':
        return True
    # interval1: --->
    # interval2:  |---
    elif interval1[2] == '' and interval2[1] != '':
        return True
    # interval1: ---|
    # interval2:    |---
    elif interval1[2] in ('<=', '=') and interval2[1] in ('=', '<=') \
    and interval1[3] == interval2[0]:
        return True
    else:
        return False


def __value_str(value):
    """
    Return a value in string format
    """
    if type(value) is str:
        return "'{v}'".format(v=value)
    else:
        return str(value)


def __value_after_left(value, interval):
    """
    Check if a value is after left limit of a interval
    """
    if interval[1] == '':
        return True
    elif interval[1] in ('=', '<=') and value >= interval[0]:
        return True
    elif interval[1] == '<' and value > interval[0]:
        return True
    else:
        return False


def __value_before_right(value, interval):
    """
    Check if a value is before right limit of a interval
    """
    if interval[2] == '':
        return True
    elif interval[2] in ('=', '<=') and value <= interval[3]:
        return True
    elif interval[2] == '<' and value < interval[3]:
        return True
    else:
        return False


def create_interval(left_limit, left_operator, right_operator, right_limit):
    """
    Create a tuple representing a interval

    The limits and operators are received from parsed term
    Examples:
        a1 < A < a2 is represented as (a1, '<', '<', a2)
        A = a1 id represented as (a1, '=', '=', a1)
        A < a1 is represented as ('', '', '<', a1)
        A > a1 is represented as (a1, '<', '', '')
    """

    # Term has left and right limits
    if left_limit != '':
        tup = (left_limit, left_operator, right_operator, right_limit)
    # Term like A = a1 represented as (a1, =, =, a1)
    elif right_operator == '=':
        tup = (right_limit, '=', '=', right_limit)
    # Term like A < a1 represented as ( , , <, a1)
    elif right_operator in ('<', '<='):
        tup = ('', '', right_operator, right_limit)
    # Term like A > a1 represented as ( a1, <, , )
    elif right_operator == '>':
        tup = (right_limit, '<', '', '')
    # Term like A >= a1 represented as ( a1, <=, , )
    else:
        tup = (right_limit, '<=', '', '')
    return tup


def split_interval(fixed_interval, split_interval):
    """
    Split 'split_interval' if 'fixed_interval' overlaps 'split_interval'
    """
    new_interval_list = []

    # Get part of 'fixed_interval' that overlaps 'split_interval'
    # First possibility, 'fixed_interval' inside
    # (at least one side) 'split_interval'
    #          fixed_interval:   |--|
    #          split_interval: |------|
    # split_interval' = fixed_interval:   |--|
    if __left_after(fixed_interval, split_interval) \
    and __right_before(fixed_interval, split_interval):
        new_interval_list.append(fixed_interval)
    #          fixed_interval: |--|
    #          split_interval: |------|
    # split_interval' = fixed_interval: |--|
    elif __left_equal(fixed_interval, split_interval) \
    and __right_before(fixed_interval, split_interval):
        new_interval_list.append(fixed_interval)
    #          fixed_interval:    |--|
    #          split_interval: |-----|
    # split_interval' = fixed_interval:    |--|
    elif __left_after(fixed_interval, split_interval) \
    and __right_equal(fixed_interval, split_interval):
        new_interval_list.append(fixed_interval)
    # Second possibility, 'fixed_interval' right limit
    # overlaps 'split_interval' left limit
    #  fixed_interval: ----|
    #  split_interval:  |-----
    # split_interval':  |--|
    elif __right_after_equal_left(fixed_interval, split_interval) \
    and __right_before(fixed_interval, split_interval):
        new_interval_list.append((split_interval[0], split_interval[1],
                                  fixed_interval[2], fixed_interval[3]))
    # Third possibility, 'fixed_interval' left limit
    # overlaps 'split_interval' right limit
    #  fixed_interval:  |-----
    #  split_interval: ----|
    # split_interval':  |--|
    elif __right_after_equal_left(split_interval, fixed_interval) \
    and __left_after(fixed_interval, split_interval):
        new_interval_list.append((fixed_interval[0], fixed_interval[1],
                                  split_interval[2], split_interval[3]))

    # Get part of 'split_interval' after 'fixed_interval'
    #  fixed_interval: ----|
    #  split_interval:  |-----
    # split_interval':     |--
    if __right_after_equal_left(fixed_interval, split_interval) \
    and __right_before(fixed_interval, split_interval):
        if fixed_interval[2] in ('=', '<='):
            new_interval_list.append((fixed_interval[3], '<',
                                      split_interval[2], split_interval[3]))
        else:
            new_interval_list.append((fixed_interval[3], '<=',
                                      split_interval[2], split_interval[3]))

    # Get part of 'split_interval' before 'fixed_interval'
    #  fixed_interval:   |----
    #  split_interval: -----|
    # split_interval': --|
    if __right_after_equal_left(split_interval, fixed_interval) \
    and __left_after(fixed_interval, split_interval):
        if fixed_interval[1] in ('=', '<='):
            new_interval_list.append((split_interval[0], split_interval[1],
                                      '<', fixed_interval[0]))
        else:
            new_interval_list.append((split_interval[0], split_interval[1],
                                      '<=', fixed_interval[0]))

    interval_list = []
    for interval in new_interval_list:
        if interval[0] == interval[3]:
            interval = (interval[0], '=', '=', interval[3])
        interval_list.append(interval)
    return interval_list


def value_in_interval(value, interval):
    """
    Check if a value is in a interval
    """
    if __value_after_left(value, interval) \
    and __value_before_right(value, interval):
        return True
    else:
        return False


def interval_str(att, interval):
    """
    Convert an attribute and its interval in string format
    """
    if interval[1] == '=':
        return str(att) + ' = ' + __value_str(interval[3])
    # Check if interval is like ('', '', '<', 'x')
    elif interval[1] == '' and interval[2] != '':
        return str(att) + ' ' + interval[2] + ' ' + \
               __value_str(interval[3])
    # Check if interval is like ('x', '<', '', '') or ('x', '<=', '', '')
    elif interval[2] == '' and interval[1] != '':
        if interval[1] == '<':
            return str(att) + ' > ' + __value_str(interval[0])
        else:
            return str(att) + ' >= ' + __value_str(interval[0])
    else:
        return __value_str(interval[0]) + ' ' + interval[1] + ' ' + \
            str(att) + ' ' + interval[2] + ' ' \
            + __value_str(interval[3])


def tuple_has_interval(tup, att, interval):
    """
    Check if 'tup' has the an attribution inside with 'att' and 'interval'
    """
    # Check if 'tup' has 'att' = 'interval'
    if att in tup \
    and tup[att] == interval:
        return True
    # Check if 'tup' has interval inside 'interval' on 'att'
    elif att in tup \
    and type(tup[att]) is not tuple \
    and type(interval) is tuple \
    and value_in_interval(tup[att], interval):
        return True
    else:
        return False
