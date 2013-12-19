# -*- coding: UTF-8 -*-
'''
Created on 01/dic/2013

@author: ross
'''
import re

ESCAPE_CHAR = '\\'
START_FIELD_CHAR = '{'
END_FIELD_CHAR = '}'
START_INTERNAL_TEMPLATE_CHAR = '('
END_INTERNAL_TEMPLATE_CHAR = ')'
SUPER_KEY_WORD = 'super.'
INPUT_PARAM_CHR = '\$'
PREFIX_FIELD_NAME = '{0}.{field_name}'
SUB_EXPR_START = '['
SUB_EXPR_END = ']'
SEARCH_EXPR_SPLIT_RE = r'(\b\w+\b)\s*(==|!=)\s*(\$?.*)'
EXPR_EQUAL_OP = '=='
EXPR_DISEQUAL_OP = '!=' #TODO it is useless?
SEARCH_EXPR_ERR_MSG = "Search expression is syntactically incorrect"
EXPR_ERR_MSG = 'Expression is syntactically incorrect'
NOT_COLLECTION_MSG = 'Search can''t be done on a non-collection attribute: {0}'
FILTER_ELEMENT_NONE_MSG = 'Field to search and the operator can''t be None'


def is_start_field_name(string, actual_index, prev_index):
        return (actual_index==0 or string[prev_index]!=ESCAPE_CHAR) and string[actual_index]==START_FIELD_CHAR
    
def is_end_field_name(string, actual_index, prev_index):
    return string[prev_index]!=ESCAPE_CHAR and string[actual_index]==END_FIELD_CHAR

#Invoked after is_start_field_name
def is_start_internal_template(string, actual_index, next_index):
    return string[actual_index]==START_FIELD_CHAR and ( len(string)>next_index and string[next_index]==START_INTERNAL_TEMPLATE_CHAR)

def is_end_internal_template( string, actual_index, next_index):
    return string[actual_index] == END_INTERNAL_TEMPLATE_CHAR and ( len(string)>next_index and string[next_index]==END_FIELD_CHAR)

def is_internal_template(string):
    return string.startswith(START_INTERNAL_TEMPLATE_CHAR) and string.endswith(END_INTERNAL_TEMPLATE_CHAR)  

#A string is valid if doesn't start neither with '$' nor with the string: 'super.'
#Return (false,false) if is valid
#(true false) if string starts with super
#(false, true) if string starts with $
def is_field_name_a_valid_string(string):
    """
    Return (false,false) if is valid
    (true false) if string starts with super
    (false, true) if string starts with $
    """
    return re.match(SUPER_KEY_WORD, string), re.match(INPUT_PARAM_CHR, string)                

def add_tuple(litteral_text, field_name, result):
    """
    Add the tuple to result converting each field in string and the container
    lists cleared
    """
    litteral_text_str = ''.join(litteral_text).replace(ESCAPE_CHAR,'') if litteral_text else None        
    field_name_str = ''.join(field_name) if field_name else None        
    string_tuple = (litteral_text_str, field_name_str, None, None)
    result.append(string_tuple)
    litteral_text = list()
    field_name = list()
    return field_name, litteral_text

def internal_template_split(field_internal_template):
    sep_index = field_internal_template.rindex(':')        
    internal_template= field_internal_template[1: sep_index ]
    object_name = field_internal_template[sep_index+1: -1]
    return internal_template, object_name
    
    
#Change the field_name starting with n-super.
#in a string startin with 'n.' where n is the number of repetitons of super.
def process_super_prefix(field_name):
    i = 0
    count = 0
    while i < len(field_name[i:]) and re.match(SUPER_KEY_WORD, field_name[i:]):
        count += 1
        i = i + len(SUPER_KEY_WORD)        
    field_name = PREFIX_FIELD_NAME.format(count, field_name = field_name[i:])
    return field_name

def prepare_field_name(field_name):
    is_super, is_dollar = is_field_name_a_valid_string(field_name)
    if is_super:
        #string starts with super.
        return process_super_prefix(field_name)
    elif is_dollar:
        #string starts with $ so we simply remove it
        return field_name[1:]
    else: #string is valid
        return PREFIX_FIELD_NAME.format(0,field_name=field_name)

def is_key_constants(key):
    return isinstance(key, str) and key[0] == '\"' and key[-1] == '\"'    

def find_sub_expr(expression):
    """
    Retrieve the sub-expression contained into square bracket, if any
    Return an Exception if there is only an open-bracket
    """
    start_sub_expr = expression.find(SUB_EXPR_START)
    
    if start_sub_expr < 0:
        return None, None
    
    end_sub_expr  =  expression.rfind(SUB_EXPR_END)
    
    if end_sub_expr < 0:
        raise Exception(EXPR_ERR_MSG)
    
    return start_sub_expr,end_sub_expr

#An expression is a search expression if is as follows:
# <string> == <evaluable_string>
# <string> != <evaluable_string>
#Here we check only if it contains the (dis)equality operator, the consistency check
#will be done successively
def expr_is_search_expression(expression):
    """
    Retrieve if the expression represents a search expression or not
    """
    #Need to do the comparison because .find() returns -1 if it didn't find the string
    #but -1 is a True boolean expression. (The False value corresponds to 0)
    return (expression.find(EXPR_EQUAL_OP) > -1 or 
            expression.find(EXPR_DISEQUAL_OP) > -1)

#Split with a regular expression checking if 
#there are exactly 3 elements
#the first element it's a simple string
#the second element it's a valid operator.
#
#On the third element no check is done because it's an evaluable element.
#the checks will be done during evaluation
def search_expr_split(expression):
    """
    Split the search expression into a list of 3 element:
    [left_operand, operator, right_operand]
    """
    match = re.match(SEARCH_EXPR_SPLIT_RE, expression)
    if not match or len(match.groups())<3:
        raise Exception(SEARCH_EXPR_ERR_MSG)
    return match.groups()


def find_top_level_rmdoc(args):
    """
    Retrieve the top level rmdoc
    """    
    return args[-1]


#it if no other params are specified returns __getattribute__ 
#Otherwise search recursively into the public attributes the one named attr_name.
#If it is a collection find and returns the element that match the criteria:
# field_to_filter operator valure 
def get_attribute(obj, attr_name, field_to_filter = None, operator = None, value = None):
    """
    Get an attribute by attr_name, if the attr_name is a collection AND 
    field_to_filter, operator, value are correctly setted returns the element
    accordingly to the search criteria
    """
    if not (field_to_filter and operator and value):
        return search_attribute(obj,attr_name)
    
    if not (field_to_filter and operator):
        raise Exception(FILTER_ELEMENT_NONE_MSG)
        
    attribute=search_attribute(obj,attr_name)
    if not isinstance(attribute, (list, tuple)):
        raise Exception(NOT_COLLECTION_MSG )
    
    field = None
    for item in attribute:
        field = item.__getattribute__(field_to_filter)
        if operator == EXPR_EQUAL_OP:
            if field == value:
                return item
    #If there isn't any attribute that match the filter
    return None     

#Recursively search an user defined attribute and retrieve it.
def search_attribute(obj, name):
    #The attribute_path is the path to the attribute using dot notation.
    #REM the first name is the root of the path. It can be in any level of the obj
    #but it must be found without ambiguity
    attribute_path = name.split('.')
    #Base
    attr =  getattr(obj, attribute_path[0], None)
    if not attr:
        #Get all attributes
        public_attrs = obj.__dict__.itervalues()
        for item in public_attrs:
            if hasattr(item, "__dict__"):
                attr=search_attribute(item, name)
                if attr:
                    break;
    for attr_step in attribute_path[1:]:
        attr = getattr(attr, attr_step)
    
    return attr
    
    