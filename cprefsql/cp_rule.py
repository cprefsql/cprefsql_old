# -*- coding: utf-8 -*-
"""
Module to manipulate each contextual preference rule
"""

from cp_interval import create_interval, split_interval, interval_str, \
                        tuple_has_interval


class CPRule(object):
    """
    Class to represent a contextual preference rule

    Attributes:
        antecedents_dict (dict): Dictionary to intervals antecedent attributes
        attribute (str): Rule attribute
        preferred (tuple): Preferred interval to rule attribute
        not_preferred (tuple): Not preferred interval to rule attribute
        indifferent_att_set (set): Set of indifferent attributes
    """

    # Antecedent terms of rule
    antecedents_dict = {}
    # Main attribute of rule
    attribute = ''
    # Values preferred to main attribute
    preferred = ()
    # Values not preferred to main attribute
    not_preferred = ()
    # Indifferent attributes of rule
    indifferent_att_set = set()

    def __init__(self, parse_result=None):
        """
        Create a CPRule from a ParseResult object
        """
        # Attribute initialization
        self.antecedents_dict = {}
        self.attribute = ''
        self.preferred = ()
        self.not_preferred = ()
        self.indifferent_att_set = set()
        if parse_result:
            # Get antecedent
            ant = parse_result.antecedent
            # Get each condition in antecedent
            for cond in ant:
                self.antecedents_dict[cond.attribute] = create_interval(
                                                       cond.left_limit,
                                                       cond.left_operator,
                                                       cond.right_operator,
                                                       cond.right_limit)
            # Get consequent
            cons = parse_result.consequent
            self.attribute = cons.preferred.attribute
            self.preferred = create_interval(
                                        cons.preferred.left_limit,
                                        cons.preferred.left_operator,
                                        cons.preferred.right_operator,
                                        cons.preferred.right_limit)
            self.not_preferred = create_interval(
                                            cons.not_preferred.left_limit,
                                            cons.not_preferred.left_operator,
                                            cons.not_preferred.right_operator,
                                            cons.not_preferred.right_limit)
            # Get indifferent attributes
            self.indifferent_att_set = set(
                                        parse_result.indifferent_attributes)

    def __del__(self):
        self.antecedents_dict.clear()
        del self.antecedents_dict
        del self.attribute
        del self.preferred
        del self.not_preferred
        self.indifferent_att_set.clear()
        del self.indifferent_att_set

    def __str__(self):
        tmp = ''
        if len(self.antecedents_dict):
            antecedent_list = []
            for ant in self.antecedents_dict:
                antecedent_list.append(
                        interval_str(ant, self.antecedents_dict[ant]))
            tmp += 'IF ' + ' AND '.join(antecedent_list) + ' THEN '
        tmp += interval_str(self.attribute, self.preferred)
        tmp += ' > ' + interval_str(self.attribute, self.not_preferred)
        if len(self.indifferent_att_set):
            tmp += ' [' + ','.join(list(self.indifferent_att_set)) + ']'
        return tmp

    def __cmp__(self, other):
        if len(self.antecedents_dict) + len(self.indifferent_att_set) \
        < len(other.antecedents_dict) + len(other.indifferent_att_set):
            return -1
        elif self.antecedents_dict == other.antecedents_dict \
        and self.attribute == other.attribute \
        and self.preferred == other.preferred \
        and self.not_preferred == other.not_preferred \
        and self.indifferent_att_set == \
        other.indifferent_att_set:
            return 0
        else:
            return 1

    def get_atomic_formulas(self):
        """
        Get atomic formulas in rule
        """
        formulas_list = []
        # Get intervals in antecedent
        for att in self.antecedents_dict:
            formula = {att: self.antecedents_dict[att]}
            formulas_list.append(formula)
        formula = {self.attribute: self.preferred}
        formulas_list.append(formula)
        formula = {self.attribute: self.not_preferred}
        formulas_list.append(formula)
        return formulas_list

    def copy(self):
        """
        Create a copy of object
        """
        cpr = CPRule()
        cpr.antecedents_dict = self.antecedents_dict.copy()
        cpr.attribute = self.attribute
        cpr.preferred = self.preferred
        cpr.not_preferred = self.not_preferred
        cpr.indifferent_att_set = self.indifferent_att_set.copy()
        return cpr

    def get_antecedent_att_set(self):
        """
        Get a set of attributes present in the antecedent
        """
        return set(self.antecedents_dict.keys())

    def split_rule(self, rule):
        """
        Split 'self' if there is overlap in intervals in
        same attribute of 'self' and 'rule'
        """
        # Try split antecedent intervals of 'rule'
        for att in self.antecedents_dict:
            fixed_interval = self.antecedents_dict[att]
            new_rules_list = split_rule_auxiliary(rule, att, fixed_interval)
            if new_rules_list != []:
                return new_rules_list
        # Try split preferred interval of 'rule'
        fixed_interval = self.preferred
        new_rules_list = split_rule_auxiliary(rule, self.attribute,
                                           fixed_interval)
        if new_rules_list == []:
            # Try split not preferred interval of 'rule'
            fixed_interval = self.not_preferred
            new_rules_list = split_rule_auxiliary(rule, self.attribute,
                                                   fixed_interval)
        return new_rules_list

    def formula_dominates(self, formula1, formula2):
        """
        Returns True if 'formula1' dominates (is preferred to) formula2
        according to rule
        """
        # Check if 'formula1' has preferred value
        # and 'formula2' has not preferred value
        if self.attribute not in formula1 or self.attribute not in formula2 \
        or formula1[self.attribute] != self.preferred \
        or formula2[self.attribute] != self.not_preferred:
            return False
        # Check if tuples satisfies rule antecedent
        for att in self.antecedents_dict:
            if att not in formula1 \
            or formula1[att] != self.antecedents_dict[att]:
                return False
            if att not in formula2 \
            or formula2[att] != self.antecedents_dict[att]:
                return False
        # Get attributes present in 'formula1' and 'formula2'
        tup_att_set = set(formula1.keys())
        tup_att_set = tup_att_set.union(set(formula2.keys()))
        # Ignore antecedent attributes (already checked)
        tup_att_set = tup_att_set.difference(set(self.antecedents_dict.keys()))
        # Ignore rule attribute
        tup_att_set.remove(self.attribute)
        # Ignore indifferent attributes
        tup_att_set = tup_att_set.difference(self.indifferent_att_set)
        # Check if all another attributes are equal,
        for att in tup_att_set:
            if att not in formula1 \
            or att not in formula2 \
            or formula1[att] != formula2[att]:
                return False
        return True

    def datalog_tuple(self, tup):
        """
        Generate a new tuple if input tuple satisfies rule
        """
        # Check if 'tup' has the preferred value
        if not tuple_has_interval(tup, self.attribute, self.preferred):
            return None
        # Copy 'tup' to 'new_tuple' and do not consider indifferent attributes
        new_tup = {}
        for att in tup:
            # Check if tuple validates antecedent
            if att in self.antecedents_dict \
            and not tuple_has_interval(tup, att, self.antecedents_dict[att]):
                return None
            # Do not consider indifferent attributes
            elif att not in self.indifferent_att_set:
                new_tup[att] = tup[att]
        # Switch preference attribute
        new_tup[self.attribute] = self.not_preferred
        return new_tup

    def datalog_formula(self, formula):
        """
        Generate a new formula if input formula satisfies rule
        """
        # Check if 'formula' has the preferred value
        if self.attribute not in formula \
        or formula[self.attribute] != self.preferred:
            return None
        new_formula = {}
        # Check if formula validates antecedent
        for att in formula:
            if att in self.antecedents_dict \
            and formula[att] != self.antecedents_dict[att]:
                return None
            # Do not consider indifferent attributes
            elif att not in self.indifferent_att_set:
                new_formula[att] = formula[att]
        # Switch preference attribute
        new_formula[self.attribute] = self.not_preferred
        return new_formula


def split_antecedents(rule, attribute, fixed_interval):
    """
    Split rule if fixed_interval interval overlaps some interval from
    antecedent part
    """
    new_rules_list = []
    # Check if 'rule' has 'attribute' in its antecedents_dict
    if attribute in rule.antecedents_dict:
        # Get interval from 'attribute' in 'rule' antecedent
        interval = rule.antecedents_dict[attribute]
        # Split 'interval' interval based on 'fixed_interval'
        new_intervals_list = split_interval(fixed_interval, interval)
        # Add rules with new intervals
        for new_interval in new_intervals_list:
            new_rule = rule.copy()
            new_rule.antecedents_dict[attribute] = new_interval
            new_rules_list.append(new_rule)
    return new_rules_list


def split_preferred(rule, attribute, fixed_interval):
    """
    Split rule if fixed_interval interval overlaps preferred interval
    """
    new_rules_list = []
    # Check if rule attribute is equal 'attribute'
    if rule.attribute == attribute:
        # Get preferred interval from 'attribute'
        interval = rule.preferred
        # Split 'interval' interval based on 'fixed_interval'
        new_intervals_list = split_interval(fixed_interval, interval)
        # Add rules with new intervals
        for new_interval in new_intervals_list:
            new_rule = rule.copy()
            new_rule.preferred = new_interval
            new_rules_list.append(new_rule)
    return new_rules_list


def split_not_preferred(rule, attribute, fixed_interval):
    """
    Split rule if fixed_interval interval overlaps not preferred interval
    """
    new_rules_list = []
    # Check if 'rule attribute' is equal 'attribute'
    if rule.attribute == attribute:
        # Get not preferred interval from 'attribute'
        interval = rule.not_preferred
        # Split 'interval' interval based on 'fixed_interval' interval
        new_intervals_list = split_interval(fixed_interval, interval)
        # Add rules with new intervals
        for new_interval in new_intervals_list:
            new_rule = rule.copy()
            new_rule.not_preferred = new_interval
            new_rules_list.append(new_rule)
    return new_rules_list


def split_rule_auxiliary(rule, att, fixed_interval):
    """
    Split 'rule' if there is overlap on intervals of attributions
    with 'att' and 'fixed_interval' in each part of 'rule'
    """
    # Try split antecedent intervals of 'rule'
    new_rules_list = split_antecedents(rule, att, fixed_interval)
    if new_rules_list != []:
        return new_rules_list
    # Try split preferred interval of 'rule'
    new_rules_list = split_preferred(rule, att, fixed_interval)
    if new_rules_list == []:
        # Try split not preferred interval of 'rule'
        new_rules_list = split_not_preferred(rule, att, fixed_interval)
    return new_rules_list
