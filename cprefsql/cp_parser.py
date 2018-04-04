#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Module to parse preference rules in string format
"""

from pyparsing import Suppress, CaselessLiteral, Word, alphas, alphanums, \
    oneOf, nums, Optional, sglQuotedString, delimitedList, Group, \
    ParseException


class CPParser(object):
    """Class to parse a string containing contextual preference rules.

    This class represents a grammar that main function is parse
    preference rules of a string.
    Grammar:
        <cp-theory> ::= <cp-rule> {"AND" <cp-rule>}*;
        <cp-rule> ::= [<antecedent>] <consequent> [<indifferent-attributes>]
        <antecedent> ::= "IF" <condition> {"AND" <condition>}* "THEN"
        <consequent> ::= <condition> ">" <condition>
        <indifferent-attributes> ::= "[" <attribute> {"," <attribute>}* "]"
        <condition> ::= <simple-condition> | <interval-condition>
        <simple-condition> ::= <attribute> <operator> <value>
        <interval-condition> ::= <value> <interval-operator> <attribute>
                               <interval-operator> <value>
        <operator> ::= "<" | ">" | "<=" | ">=" | "="
        <interval-operator> ::= "<" | "<="
        <value> ::= <string-value> | <numerical-value>

    Attributes:
        None
    """

    @classmethod
    def __gramar(cls):
        """Definition of contextual preferences grammar"""
        # 'IF' can be ignored
        if_token = Suppress(CaselessLiteral('IF'))
        # 'AND' can be ignored
        and_token = Suppress(CaselessLiteral('AND'))
        # 'THEN' can be ignored
        then_token = Suppress(CaselessLiteral('THEN'))
        # Attribute begin with letter and have letters, numbers or underline
        attribute_token = Word(alphas + '_', alphanums + '_')
        # Convert attribute to lower case
        attribute_token.setParseAction(lambda t: t[0].lower())
        # Operators
        interval_operators_tokens = oneOf('< <=')
        operator_tokens = oneOf('< > <= >= =')
        # Numbers
        integer_token = Word(nums)
        integer_token.setParseAction(lambda t: int(t[0]))
        float_token = Word(nums) + Optional('.' + Word(nums))
        float_token.setParseAction(lambda t: float(t[0]))
        string_token = sglQuotedString
        string_token.setParseAction(lambda t: t[0][1:-1])
        # Value is a number or a string
        value_token = (string_token | integer_token | float_token)
        # Conditions representing intervals
        # TODO: Maybe do interval validation
        interval_condition = value_token('left_limit') + \
                            interval_operators_tokens('left_operator') + \
                            attribute_token('attribute') + \
                            interval_operators_tokens('right_operator') + \
                            value_token('right_limit')
        # Simple condition is a comparison
        simple_condition = attribute_token('attribute') + \
                            operator_tokens('right_operator') + \
                            value_token('right_limit')
        # Condition is interval or simple condition
        condition = (interval_condition |
                        simple_condition)
        # 'BETTER' can be ignored
        better_token = Suppress(CaselessLiteral('>'))
        # Left parentheses
        left_par_token = Suppress('[')
        # Right parentheses
        right_par_token = Suppress(']')
        # Comma
        comma_token = Suppress(',')
        # Antecedent is in format 'IF CONDITION_1 AND ... CONDITION_N THEN'
        antecedent = if_token + \
                         delimitedList(Group(condition), and_token) + \
                         then_token
        # Consequent is in format 'CONDITION BETTER CONDITION'
        # TODO: Maybe check if preferred attribute is equal to not preferred
        # attribute
        consequent = Group(condition).setResultsName('preferred') + \
                         better_token + \
                         Group(condition).setResultsName('not_preferred')
        # Indifferent attributes term is in format (ATT, ATT, ATT, ...)
        indifferent_attributes = left_par_token + \
                  delimitedList(attribute_token, comma_token) + \
                  right_par_token

        # Rule is antecedent, consequent and indifferent attributes
        preference_rule = Group(
                Group(Optional(antecedent)).setResultsName('antecedent') +
                Group(consequent).setResultsName('consequent') +
                Group(Optional(indifferent_attributes)).setResultsName(
                                                'indifferent_attributes')
                   )
        # Theory is set of RULES
        preference_theory = delimitedList(preference_rule, and_token)
        return preference_theory

    @classmethod
    def parse(cls, string_preferences):
        """Parse a string to ParseResult"""
        return cls.__gramar().parseString(string_preferences)


def print_parse_result(parsed_rules):
    """Print a ParseResult of contextual preferences in clear format"""
    rule_number = 0
    for rule in parsed_rules:
        print 'Rule {rn}'.format(rn=rule_number)
        antecedent = rule.antecedent
        consequent = rule.consequent
        indifferent_attributes = rule.indifferent_attributes
        if antecedent is not None:
            print 'Antecedent:'
            for cond in antecedent:
                print '{vall} {opl} {att} {opr} {valr}'.format(
                    vall=cond.left_limit,
                    opl=cond.left_operator,
                    att=cond.attribute,
                    opr=cond.right_operator,
                    valr=cond.right_limit)
        print 'Consequent:'
        print '{vall} {opl} {att} {opr} {valr}'.format(
            vall=consequent.preferred.left_limit,
            opl=consequent.preferred.left_operator,
            att=consequent.preferred.attribute,
            opr=consequent.preferred.right_operator,
            valr=consequent.preferred.right_limit)
        print 'BETTER'
        print '{vall} {opl} {att} {opr} {valr}'.format(
            vall=consequent.not_preferred.left_limit,
            opl=consequent.not_preferred.left_operator,
            att=consequent.not_preferred.attribute,
            opr=consequent.not_preferred.right_operator,
            valr=consequent.not_preferred.right_limit)
        if len(indifferent_attributes) > 0:
            print 'Indifferent attributes:'
            for attribute in indifferent_attributes:
                print '{a}'.format(a=attribute)
        print ''
        rule_number += 1


def print_usage():
    """Print usage of program"""
    import sys
    program_name = sys.argv[0]
    print """
    Contextual Preference Parser
    Usage:
        {program_name} --help: print this help
        {program_name} preferences: parse the preferences
        {program_name} -f file: parse the preferences in file
    """.format(prog=program_name)


def get_preferences():
    """Get preferences from command line or pref_file"""
    import sys
    if len(sys.argv) == 2:
        if sys.argv[1] == '--help':
            print_usage()
            return ''
        else:
            return sys.argv[1]
    elif len(sys.argv) == 3 and sys.argv[1] == '-f':
        pref_file = open(sys.argv[2])
        return pref_file.read()
    else:
        return ''


# Check if file is executed as a program
if __name__ == '__main__':
    PREFS = get_preferences().strip()
    if PREFS == '':
        exit(0)
    try:
        RULES = CPParser.parse(PREFS)
        print 'Original string theory:'
        print PREFS
        print ''
        print 'ParseResult object:'
        print RULES
        print ''
        print 'ParseResult detailed:'
        print_parse_result(RULES)
    except ParseException as parse_exception:
        print 'CPParser error:'
        print parse_exception.line
        print parse_exception
