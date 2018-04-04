#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Module to manipulate contextual preference theories
"""

from pyparsing import ParseException
from cp_parser import CPParser, get_preferences
from cp_rule import CPRule
from cp_graph import CPGraph
from cp_comparison import CPComparison, str_formula
from cp_interval import tuple_has_interval


class CPTheory(object):
    """
    Class to represent a set of contextual preference rules

    Attributes:
        rules_list (list): List of preference rules
        comparisons_list (list): List of comparisons
        antecedent_att_set (set): Set of attributes in antecedent of all rules
        preference_att_set (set): Set of preference attributes of all rules
        indifferent_att_set (set): Set of indifferent attributes of all rules
        formulas_list (list): List of essential formulas
        consistent (boolean): Flag of theory consistency
    """
    # List of rules
    rules_list = []
    # List of comparisons
    comparisons_list = []
    # Set of attributes in antecedent of rules
    antecedent_att_set = set()
    # Set of attributes with preference
    preference_att_set = set()
    # Set of indifferent attributes
    indifferent_att_set = set()
    # List of formulas
    formulas_list = []
    # Flag of theory consistency
    consistent = False

    def __init__(self, cprules_string):
        """
        Create a CPTheory from a string with preference rules
        """
        self.rules_list = []
        self.comparisons_list = []
        self.antecedent_att_set = set()
        self.preference_att_set = set()
        self.indifferent_att_set = set()
        self.formulas_list = []
        self.consistent = False
        parse_result = CPParser.parse(cprules_string)
        for parse_res in parse_result:
            cpr = CPRule(parse_res)
            self.__add_rule(cpr)
        self.__split_rules()
        self.__check_consistency()
        if self.consistent:
            self.__build_comparisons()

    def __str__(self):
        str_list = [str(r) for r in self.rules_list]
        return ' AND\n'.join(str_list)

    def __len__(self):
        return len(self.rules_list)

    def __del__(self):
        del self.rules_list[:]
        del self.rules_list
        del self.comparisons_list[:]
        del self.comparisons_list
        del self.formulas_list[:]
        del self.formulas_list
        self.antecedent_att_set.clear()
        del self.antecedent_att_set
        self.preference_att_set.clear()
        del self.preference_att_set
        self.indifferent_att_set.clear()
        del self.indifferent_att_set

    def __rules_over_attribute(self, att):
        """
        Return rules where preferences are over 'att' attribute
        """
        rules_att_list = []
        for cpr in self.rules_list:
            if cpr.attribute == att:
                rules_att_list.append(cpr)
        return rules_att_list

    def __add_rule(self, rule):
        """
        Add a rule do rules_list
        """
        self.rules_list.append(rule)
        self.antecedent_att_set = self.antecedent_att_set.union(
                                            rule.get_antecedent_att_set())
        self.preference_att_set.add(rule.attribute)
        self.indifferent_att_set = self.indifferent_att_set.union(
                                            rule.indifferent_att_set)

    def __build_formulas(self):
        """
        Generate a list of formulas combining all intervals of attributes
        """
        # Get atomic formulas in all rules
        self.formulas_list = []
        atomic_formulas_list = []
        for cpr in self.rules_list:
            for formula in cpr.get_atomic_formulas():
                if formula not in self.formulas_list:
                    self.formulas_list.append(formula)
                    atomic_formulas_list.append(formula)
        # Combined formulas
        att_set = self.antecedent_att_set.union(self.preference_att_set)
        for att in att_set:
            new_formulas_list = []
            for formula in self.formulas_list:
                for atomic in atomic_formulas_list:
                    if att not in formula \
                    and att in atomic:
                        new_formula = formula.copy()
                        new_formula[att] = atomic[att]
                        if new_formula not in self.formulas_list \
                        and new_formula not in new_formulas_list:
                            new_formulas_list.append(new_formula)
            self.formulas_list += new_formulas_list

    def __remove_not_essential_comp(self):
        """
        Remove no essential comparisons of 'comparisons_list'
        """
        essential_comp_list = []
        for comp in self.comparisons_list:
            if comp.is_essential(self.comparisons_list):
                essential_comp_list.append(comp)
        self.comparisons_list = essential_comp_list[:]

    def __build_comparisons(self):
        """
        Generate all comparisons that can be realized by cp-rules
        Comparisons are in format:
            (preferred) BETTER (not_preferred) [indifferent]
        """
        # Generate all formulas
        self.__build_formulas()
        # Generate direct comparisons
        for formula1 in self.formulas_list:
            for formula2 in self.formulas_list:
                if formula1 != formula2:
                    for cpr in self.rules_list:
                        if cpr.formula_dominates(formula1, formula2):
                            pref_indiff_set = \
                                cpr.indifferent_att_set.difference(
                                               set(formula1.keys()))
                            not_pref_indiff_set = \
                                cpr.indifferent_att_set.difference(
                                               set(formula2.keys()))
                            new_comp = CPComparison(formula1, formula2,
                                                      pref_indiff_set,
                                                      not_pref_indiff_set)
                            if new_comp not in self.comparisons_list:
                                self.comparisons_list.append(new_comp)
        # Generate indirect comparisons
        build_comp_list = self.comparisons_list[:]
        while build_comp_list != []:
            new_comp_list = []
            for comp in build_comp_list:
                for cpr in self.rules_list:
                    new_formula = cpr.datalog_formula(
                        comp.not_pref_formula_dict)
                    if new_formula is not None:
                        new_comp = CPComparison(comp.pref_formula_dict,
                                                  new_formula,
                                                  comp.pref_indif_set,
                                                  cpr.indifferent_att_set)
                        if new_comp not in self.comparisons_list \
                        and new_comp not in new_comp_list:
                            new_comp_list.append(new_comp)
#             if new_comp_list != []:
            self.comparisons_list += new_comp_list
            build_comp_list = new_comp_list[:]
#             else:
#                 build_comp_list = []
        # Remove not essential formulas
        self.__remove_not_essential_comp()
        self.comparisons_list.sort()

    def __split_rules(self):
        """
        Searches for rules with intersection in intervals.
        When that found, new rules are generated with disjoint intervals.
        Example:
            - Two intersected intervals: (1 < A < 9) and (2 < A < 10)
            - Three three new intervals: (1 < A <= 2) and (2 < A < 9) and
                                        (9 <= A < 10)
        The original number of rules can be increased
        """
        while True:
            # List of new rules
            new_rules_list = []
            # Get pair of rules
            for cpr1 in self.rules_list:
                for cpr2 in self.rules_list:
                    # 'new_rules_list' is rules originated by
                    # 'cpr2' with split in intervals
                    new_rules_list = cpr1.split_rule(cpr2)
                    # Check if there was split in 'cpr2' intervals
                    if new_rules_list:
                        # Remove original rule
                        self.rules_list.remove(cpr2)
                        break
                # Restart iteration
                if new_rules_list:
                    break
            # Check if there was split in intervals
            if new_rules_list:
                # Add new rules
                self.rules_list += new_rules_list
            else:
                # Stop, when there wasn't split
                break

    def __global_consistency(self):
        """
        Check global consistency of theory

        Build a graph with edges ('A', 'P') and ('P', 'C')
        Where, in a rule:
            'A' is a attribute in antecedent of rule
            'P' is the attribute in the preference specification
            'C' is a indifferent attribute
        All rules are considered
        If builded graph is acyclic, then theory is globally consistent
        """
        # Initialize graph
        graph = CPGraph()
        # For each rule
        for cpr in self.rules_list:
            # For each antecedent in 'cpr' rule
            for ant in cpr.antecedents_dict:
                # Add edge ('A', 'P')
                graph.add_edge(ant, cpr.attribute)
            # For each indifferent attribute
            for cet in cpr.indifferent_att_set:
                # Add edge ('P', 'C')
                graph.add_edge(cpr.attribute, cet)
        # Check if graph is acyclic
        if graph.is_acyclic():
            return True
        else:
            return False

    def __local_consistency(self):
        """
        Check local consistency

        Check if there is a cycle like A better B and B better A
        """
        # For each consequent attribute
        for att in self.preference_att_set:
            # Get rules where preferences are over 'att'
            rules_att_list = self.__rules_over_attribute(att)
            # Get all possible lists of antecedents in 'rules_att_list'
            ant_lists = build_ant_lists(rules_att_list)
            for ant_list in ant_lists:
                rules_list = rules_over_ant_list(rules_att_list, ant_list)
                graph = graph_local_consistency(rules_list)
                if not graph.is_acyclic():
                    return False
        return True

    def __check_consistency(self):
        """
        Check if CPTheory is global and local consistent
        """
        if self.__global_consistency() \
        and self.__local_consistency():
            self.consistent = True
            return True
        else:
            self.consistent = False
            return False

    def datalog_dominates(self, tuple1, tuple2):
        """
        Returns True if 'tuple1' dominates (is preferred to) tuple2
        according to theory (datalog method)
        """
        if tuple1 != tuple2:
            # Initialize datalog list
            # List of tuples to be processed
            process_tup_list = [tuple1]
            # List of tuples already tested
            tested_tup_list = []
            while process_tup_list != []:
                # List of new tuples generated by datalog
                new_tup_list = []
                # Generate new tuples to datalog
                for tup in process_tup_list:
                    for rule in self.rules_list:
                        new_tup = rule.datalog_tuple(tup)
                        if new_tup is not None \
                        and new_tup not in tested_tup_list:
                            new_tup_list.append(new_tup)
                            # Check if goal was reached
                            if datalog_goal(new_tup, tuple2):
                                return True
                process_tup_list = new_tup_list[:]
                tested_tup_list += new_tup_list
        return False

    def optimized_dominates(self, tuple1, tuple2):
        """
        Returns True if 'tuple1' dominates (is preferred to) tuple2
        according to theory
        """
        # Check if 'tuple1' is not equal 'tuple2'
        if tuple1 != tuple2:
            # Check for direct dominance test
            for comp in self.comparisons_list:
                if comp.dominates(tuple1, tuple2):
                    return True
        return False

    def print_comparisons(self):
        """
        Print the list of comparison
        """
        self.comparisons_list.sort()
        print self.comparisons_str()

    def print_formulas(self):
        """
        Print the list of formulas
        """
        for formula in self.formulas_list:
            print str_formula(formula)

    def comparisons_str(self):
        """
        Get a string list of comparisons
        """
        comparison_list_str = [str(comp) for comp in self.comparisons_list]
        return '\n'.join(comparison_list_str)


def antecedent_intervals_dict(rules_list):
    """
    Return a dictionary where keys are attributes in antecedent of rules
    in 'rules_list' and values are list of intervals of attributes
    in 'rules_list'
    """
    interval_dict = {}
    for cpr in rules_list:
        for ant in cpr.antecedents_dict:
            if ant in interval_dict:
                interval = cpr.antecedents_dict[ant]
                if interval not in interval_dict[ant]:
                    interval_dict[ant].append(cpr.antecedents_dict[ant])
            else:
                interval_dict[ant] = [cpr.antecedents_dict[ant]]
    return interval_dict


def valid_rules_by_att_interval(rules_list, att, interval):
    """
    Return rules validated by attributions 'att' and 'interval'
    A rule is valid if 'att' is not in antecedent or
    'att' antecedent interval is equal of 'interval'
    """
    rules_interval_list = []
    for cpr in rules_list:
        if att not in cpr.antecedents_dict \
        or cpr.antecedents_dict[att] == interval:
            rules_interval_list.append(cpr)
    return rules_interval_list


def graph_local_consistency(rules_list):
    """
    Build a graph to test local consistency

    Edges are from 'preferred' interval to 'not_preferred' interval
    """
    graph = CPGraph()
    for cpr in rules_list:
        graph.add_edge(cpr.preferred, cpr.not_preferred)
    return graph


def datalog_goal(datalog_tup, goal_tup):
    """
    Check if some tuple in 'datalog_tup' is the 'goal_tup'
    """
    for att in datalog_tup:
        # Check if 'goal_tup' has an attribution inside 'att'
        # and 'datalog_tup[att]'
        if not tuple_has_interval(goal_tup, att, datalog_tup[att]):
            return False
    return True


def build_ant_lists(rules_list):
    """
    Build a list of combined antecedents
    A combined antecedent is a list of antecedent
    """
    ant_lists = []
    # Individual antecedents
    for rule in rules_list:
        ant_list = [rule.antecedents_dict]
        if ant_list not in ant_lists:
            ant_lists.append(ant_list)
    # Combined antecedents
    change = True
    while change == True:
        change = False
        new_ant_list = []
        for ant_list1 in ant_lists:
            for ant_list2 in ant_lists:
                if ant_list1 != ant_list2:
                    new_ant_list = combine_ant_lists(ant_list1, ant_list2)
                    new_ant_list.sort()
                    if new_ant_list != [] \
                    and new_ant_list not in ant_lists \
                    and new_ant_list not in new_ant_list:
                        new_ant_list.append(new_ant_list)
                        change = True
        ant_lists += new_ant_list
    return ant_lists


def combine_ant_lists(ant_list1, ant_list2):
    """
    Combine two combined antecedents
    If combination could not be done return []
    """
    for ant1 in ant_list1:
        for ant2 in ant_list2:
            for att in ant1:
                if att in ant2 \
                and ant1[att] != ant2[att]:
                    return []
    new_comb = ant_list1[:]
    for ant in ant_list2:
        if ant not in new_comb:
            new_comb.append(ant)
    return new_comb


def rules_over_ant_list(rules_list, ant_list):
    """
    Return rules of 'rules_att_list' that have some antecedent in 'ant_list'
    """
    valid_rules_list = []
    for rule in rules_list:
        for ant in ant_list:
            if rule.antecedents_dict == ant:
                valid_rules_list.append(rule)
    return valid_rules_list


############################################################################
# If the file is executed as a program
if __name__ == '__main__':
    PREFS = get_preferences().strip()
    if PREFS != '':
        try:
            print 'Original string theory:'
            print PREFS
            CPRULES = CPTheory(PREFS)
            print '\n CPTheory Rewritten:'
            print len(CPRULES)
            print str(CPRULES)
            if CPRULES.consistent:
                print '\n CPTheory with transitive rules:'
                print len(CPRULES)
                print str(CPRULES)
        except ParseException as parse_exception:
            print 'CPParser error:'
            print parse_exception.line
            print parse_exception
