# -*- coding: utf-8 -*-
"""
Module to manipulate each contextual preference rule
"""

from cp_interval import interval_str, value_in_interval


class CPComparison(object):
    """
    Class to represent tuple comparisons directly
    """

    # Preferred formula
    pref_formula_dict = {}
    # Not preferred formula
    not_pref_formula_dict = {}
    # Preferred indifferent set
    pref_indif_set = set()
    # Preferred indifferent set
    not_pref_indif_set = set()

    def __init__(self, pref_formula_dict, not_pref_formula_dict,
                 pref_indif_set, not_pref_indif_set):
        """
        Create a CPComparison object
        """
        # Initialization
        self.pref_formula_dict = pref_formula_dict.copy()
        self.not_pref_formula_dict = not_pref_formula_dict.copy()
        self.pref_indif_set = pref_indif_set.copy()
        self.not_pref_indif_set = not_pref_indif_set.copy()

    def __del__(self):
        self.pref_formula_dict.clear()
        self.not_pref_formula_dict.clear()
        del self.pref_formula_dict
        del self.not_pref_formula_dict
        del self.pref_indif_set
        del self.not_pref_indif_set

    def __str__(self):
        tmp_str = str_formula(self.pref_formula_dict)
        if len(self.pref_indif_set) > 0:
            tmp_str += '[' + ','.join(self.pref_indif_set) + ']'
        tmp_str += ' > '
        tmp_str += str_formula(self.not_pref_formula_dict)
        if len(self.not_pref_indif_set) > 0:
            tmp_str += '[' + ','.join(self.not_pref_indif_set) + ']'
        return tmp_str

    def __cmp__(self, other):
        if self.pref_formula_dict < other.pref_formula_dict:
            return -1
        if self.pref_formula_dict == other.pref_formula_dict \
        and self.not_pref_formula_dict < other.not_pref_formula_dict:
            return -1
        if self.pref_formula_dict == other.pref_formula_dict \
        and self.not_pref_formula_dict == other.not_pref_formula_dict \
        and self.pref_indif_set == other.pref_indif_set \
        and self.not_pref_indif_set == other.not_pref_indif_set:
            return 0
        else:
            return 1

    def preference_att_set(self):
        """
        Return a set with all attribute of comparison
        """
        ## TODO: Precisa checar isto
        # Attributes in preferred part must be the same in not preferred part
        att_set = set(self.pref_formula_dict.keys())
        att_set = att_set.union(self.pref_indif_set)
        return att_set

    def preferred(self, tup):
        """
        Check if 'tup' satisfies preferred values
        """
        for att in self.pref_formula_dict:
            if att not in tup \
            or not value_in_interval(tup[att], self.pref_formula_dict[att]):
                return False
        return True

    def not_preferred(self, tup):
        """
        Check if 'tup' satisfies not preferred values
        """
        for att in self.not_pref_formula_dict:
            if att not in tup \
            or not value_in_interval(tup[att],
                                     self.not_pref_formula_dict[att]):
                return False
        return True

    def dominates(self, tuple1, tuple2):
        """
        Returns True if 'tuple1' dominates (is preferred to)
        'tuple2' according to comparison
        """
        # Check if 'tuple1' and 'tuple2' have the same attributes
        if tuple1.keys() != tuple2.keys():
            return False
        # Check if tuple1 satisfies preferred values
        if not self.preferred(tuple1):
            return False
        # Check if tuple2 satisfies not preferred values
        if not self.not_preferred(tuple2):
            return False
        # Check if attributes another attributes of tuples
        # (except attributes in formulas and indifferent set)
        # have the same value
        for att in tuple1:
            if att not in self.pref_formula_dict \
            and att not in self.pref_indif_set \
            and att not in self.not_pref_indif_set \
            and tuple1[att] != tuple2[att]:
                return False
        return True

    def is_essential(self, comp_list):
        """
        A comparison b: f ^ a[Wf] > f' ^ a'[Wf'] is essential if there no
        exists another comparison b': g[Wg] > g[Wg'] such that:
          (1) g = f, g'= f', a = a', Wf is subset of Wg
              and Wf' is subset of Wg'
          (1) g = f, g' = f', (Attr(a) union Wf) is subset of Wg
              and (Attr(a') union Wf') is subset of Wg'
        """
        for comp in comp_list:
            # Check if 'self' formulas are sub-formulas of 'comp' formulas
            if self != comp \
            and is_subformula(self.pref_formula_dict, comp.pref_formula_dict) \
            and is_subformula(self.not_pref_formula_dict,
                              comp.not_pref_formula_dict):
                pref_diff = difference_formula(self.pref_formula_dict,
                                               comp.pref_formula_dict)
                not_pref_diff = difference_formula(self.not_pref_formula_dict,
                                                   comp.not_pref_formula_dict)
                if pref_diff == not_pref_diff \
                and self.pref_indif_set.issubset(comp.pref_indif_set) \
                and self.not_pref_indif_set.issubset(comp.not_pref_indif_set):
                    return False
                pref_diff_set = set(pref_diff.keys())
                not_pref_diff_set = set(not_pref_diff.keys())
                pref_diff_set = pref_diff_set.union(self.pref_indif_set)
                not_pref_diff_set = not_pref_diff_set.union(
                                                    self.not_pref_indif_set)
                if pref_diff_set.issubset(comp.pref_indif_set) \
                and not_pref_diff_set.issubset(comp.not_pref_indif_set):
                    return False
        return True


def str_formula(formula):
    """
    Convert a formula stored in dictionary in a string
    """
    attribution_list = []
    for att in formula:
        attribution_list.append(interval_str(att, formula[att]))
    return '(' + ')^('.join(attribution_list) + ')'


def is_subformula(formula, subformula):
    """
    Check if 'subformula' is sub-formula of 'formula'
    """
    for att in subformula:
        if att not in formula \
        or subformula[att] != formula[att]:
            return False
    return True


def difference_formula(big_formula, small_formula):
    """
    Return attributions in 'big_formula' and not in 'small_formula'
    """
    formula = {}
    for att in big_formula:
        if att not in small_formula:
            formula[att] = big_formula[att]
    return formula
