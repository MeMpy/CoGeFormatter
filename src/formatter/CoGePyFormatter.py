# -*- coding: UTF-8 -*-
'''
Created on 18/ott/2013

@author: eroreng
'''
from string import Formatter
from formatter import utils

ERR_MSG = 'String not correctly formatted'


class CoGePyFormatter(Formatter):    
    
    # returns an iterable that contains tuples of the form:
    # (literal_text, field_name, format_spec, conversion)
    # literal_text can be zero length
    # field_name can be None, in which case there's no
    #  object to format and output
    # if field_name is not None, it is looked up, formatted
    #  with format_spec and conversion and then used
    # REM: format_spec and conversion in this version will be always None
    def parse(self, formatting_string):        
        """
        This new parser will return into the field_name also the internal template:
        an internal template is a field delimited by "{(" and ")}". 
        """        
        
        if not formatting_string:
            return []
        
        is_fieled_name = False
        is_internal_template = False
        litteral_text = list()
        field_name = list()
        actual_char = None
        result = list()
        other_internal_template = 0 #keep track of the internal templates contained into the current internal template
        
        i=0
        while i< len(formatting_string):
            actual_char = formatting_string[i]
            if not is_fieled_name:
                is_fieled_name = utils.is_start_field_name(formatting_string, i, i-1)
                if not is_fieled_name:
                    litteral_text.append(actual_char)
                else:     
                    #We are entering in a field name. We are at the first character               
                    is_internal_template = utils.is_start_internal_template(formatting_string, i, i+1)                                        
            elif is_internal_template: #If we are already in an internal template (and thus we are also in a field_name)            
                #check if starts or ends a new internal template
                if utils.is_start_internal_template(formatting_string, i, i+1):
                    other_internal_template = other_internal_template+1
                elif utils.is_end_internal_template(formatting_string, i, i+1):
                    other_internal_template = other_internal_template-1
                    
                if other_internal_template == -1 and utils.is_end_internal_template(formatting_string, i, i+1):
                    is_internal_template = False
                    other_internal_template = 0
                    is_fieled_name = False
                    field_name.append(actual_char) #We append as last char the ) for coherence with the internal template
                    i=i+1                    
                    field_name, litteral_text = utils.add_tuple(litteral_text, field_name, result)
                else:
                    field_name.append(actual_char)
            elif utils.is_end_field_name(formatting_string, i, i-1):
                is_fieled_name = False                
                field_name, litteral_text = utils.add_tuple(litteral_text, field_name, result)
            else:
                field_name.append(actual_char)
            i = i+1            
        
        if is_fieled_name or is_internal_template:
            raise Exception(ERR_MSG)
        #Append the last part
        if litteral_text or field_name:
            utils.add_tuple(litteral_text, field_name, result)
            
        return result                                       
                                                                            

    #If the field is a normal field, prepend a number indicating the 0-index position
    #of the object in which is present the attribute named field.
    #If the field is an internal template recall format on the internal template passing the object
    #obtained evaluating the expression, and the subsequents args are the containers
    #as they appears in the whole template
    #If the field isn't an internal template and starts with super. replace all occurrences of super.
    #with n. where n is the number of occurrences of super, if it doesn' start with super add a 0. and
    #call super.get_field
    #If the field isn't an internal template and starts with $ remove it and call super.get_field
    #If we can't find the internal template obj or it is None we semply don't write the IT    
    def get_field(self, field_name, args, kwargs):
        
        if utils.is_internal_template(field_name):
            #We are processing the right part of the template 
            #the one which find the rmdoc used to fill the template
            internal_template, obj_expression = utils.internal_template_split(field_name)
            
            try:
                obj = self._get_expr_value(obj_expression.strip(), args, kwargs, False)
            #TODO We can also print a log when we caught in these exceptions
            except KeyError:
                obj = None
            except AttributeError:
                obj = None
            
            #If we can't find internal template obj or if it's None or False we simply don't write the IT
            if obj is None or obj is False:
                return '', obj
                
            
            if isinstance(obj, (list,tuple)):
                values_list = []
                for item in obj:
                    values_list.append( self.format(internal_template, item, *args, **kwargs) )
                value = ''.join(values_list)
            elif isinstance(obj, bool):     
                #If obj is a boolean (it must be True) means that we are evaluating a flag so the IT 
                #must be processed with the previous args    
                value = self.format(internal_template, *args, **kwargs)
            else:
                value = self.format(internal_template, obj, *args, **kwargs)
            return value, obj_expression
        else:
            #We are processing the template itself            
            field_name = utils.prepare_field_name(field_name)
            
            return super(CoGePyFormatter,self).get_field(field_name, args, kwargs)    
                
    
    
    #In expression can be inserted all the standard elements or:
    #-a dictionary: $dict_name[dict_key] where dict_key can be all valid expression that
    #                return a value
    #-an attribute searched into a collection of the rmdoc: collection_name[search expression]
    # where search_expression is builded as follows: attr_name == (!=) value
    #        where value can be all valid expression that return a value
    #        and attr_name is a valid attribute path (ex: super.super....<attr_name>
    def _get_expr_value(self, expression, args, kwargs, evaluate):
        """
        Evaluate recursively the expression to retrieve the right object
        If evaluate is true will be returned the value of the object retrived evaluating the expression
        If it is false will be returned the object itself
        """        
        start_sub_expr, end_sub_expr = utils.find_sub_expr(expression)
        if not start_sub_expr:
            #Base Case
            #expression is one of the follows:
            #attr_name = get the attribute named attr_name from the current rmdoc (args[0])
            #$name = Input parameters -> kwargs[name]
            #super...super.attr_name = process the super in order to find the arg index 
            #                pointing to the rmdoc in which find the attribute named attr_name
            #"hello world" = a constant which need to be returned identically except for the ""
            if evaluate:
                #We are in the right hand of the expression 
                if utils.is_key_constants(expression):
                    return expression[1:-1]
                else:
                    return self.get_field(expression, args, kwargs)[0]
            else:
                #--------------------------------------- We are in the left hand
                #------------ return self.get_field(expression, args, kwargs)[0]
                if utils.is_field_name_a_valid_string(expression)[1]:
                    #the obj is an input variable
                    return self.get_field(expression, args, kwargs)[0]
                else:
                    #first of all we search inside the object of the current template.
                    obj = self.get_field(expression, args, kwargs)[0]
                    if obj:
                        return obj
                    else:
                        #Otherwise Search inside the top-level rmdoc with a deep search
                        #TODO Understand if it is really useful..
                        rmdoc = utils.find_top_level_rmdoc(args)
                        return utils.get_attribute(rmdoc, expression)
        else:
            sub_expr = expression[start_sub_expr+1:end_sub_expr].strip()
            if utils.expr_is_search_expression(sub_expr):
                #Rmdoc collection in which perform the search
                attr_name = expression[0:start_sub_expr]
                #We are searching for an attribute with a criteria.
                expr_elems = utils.search_expr_split(sub_expr)
                #Right elements need to be evaluated
                #The evaluation can raise a KeyError exception. It is catched outside
                right_elem = self._get_expr_value(expr_elems[2], args, kwargs, True)
                #Typically if we are here we have terminated the recursion                
                rmdoc = utils.find_top_level_rmdoc(args)
                return utils.get_attribute(rmdoc, attr_name, expr_elems[0], expr_elems[1], right_elem)
            else:
                #We are evaluating a dictionary
                #Here we need to retrieve the effective value of the expression                
                key =self._get_expr_value(sub_expr, args, kwargs, True)
                dict_name = expression[1:start_sub_expr]
                dict_obj = kwargs[dict_name]
                return dict_obj[key]
