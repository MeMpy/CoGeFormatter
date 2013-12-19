CoGeFormatter : An extended version of string.format
======
This is a Python Formatter Class that extends the standard string formatter allowing the user to create powerful template in order to generate text filled by a data object

## REQUIREMENTS
Python 2.7 - use your packet manager to install it or compile from source

## Usage

To run the formatter you need

1. A string 
2. An object to fill the string
3. An instance of the formatter 


		class User(object):
			def __init__(self):
				name = 'Monkey D.'
	
		template = 'My name is {name}'
		usr = User()
		formatter = CoGePyFormatter()	
		
		formatter.format(template, usr)
		

 

#Template
The template itself is the core of formatter. It is a string with placeholders

	My name is {name}

`{name}` will be filled with the value of the attribute named `name` of the object passed to the formatter.

Using `User` the result will be:

    My name is Monkey D.

## Internal Template ##
An internal template is a template contained into an other template:

    My name is {name} {(my addresses are: \n {street}: address)}

The syntax is:

	{( <template> : <attribute or object> )}


where `<template>` is a text with placeholders views above and `<attribute or object>` is the object used to fill the internal template.

### Attribute or object ###

According to `<attribute or object>` we have different behavior.

- *simple class instance* ---> `address`
	- it acts in the standard way.
- *collection* ---> `addresses`
	- it iterates through the collection and writes the internal template many times as the elements of collection are. For each element it acts in the standard way
- *variable* ---> `$address`
	- it acts in the standard way but the object will be searched in the kwargs rather than in the top level object
- *searched object with constants* ---> `addresses[street == "penny lane n. 8 "]`
	- It searches into the collection `addresses` retrieved from the top level object the object whose attribute `street` match the constant: `"penny lane n. 8 "` 
- *searched object with variable* ---> `addresses[street == $my_street]`
	- Like above but the search string is taken from a variable from kwargs
- *searched object with dictionary* ---> `addresses[street == $streets[name]]`
	- `$streets[name]` is a dictionary passed into kwargs. As *keys* you can use any attribute value of the top level object or a variable passed in input (`$name`). In case of an attribute value, the attribute will be searched into the object of the container template.
- *dictionary of boolean* ---> `$streets_bool[ name ]`
	- In this case the internal template will be written only if  the entry value corresponding to `name` is True. The object used will be the one of the container template.

If any of this `<attribute or object>` returns None the internal template will be not written.

### Placeholders ###
Each (internal) template can contain placeholders. They can be of different types:

- *attribute_name* ---> `{name}`
	- It will be replaced with the value of the attribute named `name` of the current object (the one passed to the template)
- *super.....super.attribute_name* --->`{super....super.name}`
	- It will be replaced with the value of the attribute named `name` of the object of the container template. According to the number of super you can get different containing level.
- *variable* ---> `{$name}`
	- It will be replaced with the value contained into the kwargs searching `name` as key 

### Formatter Examples ###

In these examples we will use a modified User class showed above:

	class User(object):
        class Address(object):
            class Phone():
                
                def __init__(self):
                    self.prefix = '081'
                    self.number = '123456'
                    
            def __init__(self, i):
                self.street = "penny lane n. " + str(i)+" "
                self.cod = "040404"
                self.phone = self.Phone()
                
        def init(self):
            self.__setattr__("name", "Monkey D.")
            self.__setattr__("surname", "Rufy" )
            self.__setattr__("address", self.Address(-1))
            addresses = []
            for i in range(0,10):
                addresses.append(self.Address(i))
            self.__setattr__("addresses", addresses)

----------

    usr = User()

And we'll show the result applying the CoGePyFormatter:

	formatter = CoGePyFormatter()	

----------



- Standard behavior:

		template = "Hello world! {name}, {surname}."

		formatter.format(template, usr)
		
		result:
	
		Hello world! Monkey D., Rufy.

- Internal template standard behavior (with an object attribute):
	
		template = "Hello world! {name}, {surname}.{(I live in {street} {cod}, Don't forget that my name is {super.name}: address)}"
		
		formatter.format(template, usr)

		result:

		Hello world! Monkey D., Rufy.I live in penny lane n. -1  040404, Don't forget that my name is Monkey D.

- Internal template with a variable as object:

		template = "Hello world! {name}, {surname}.{(I live in {street} {cod}, Don't forget that my name is {super.name}: $address)}"
		
		a = User.Address(-1)

		formatter.format(template, usr, address = a)

		result:

		Hello world! Monkey D., Rufy.I live in penny lane n. -1  040404, Don't forget that my name is Monkey D.

- Internal template with a collection (in this case it is a object attribute):

		template = "Hello world! {name}, {surname}.{(I live in {street} {cod}, Don't forget that my name is {super.name}: addresses)}"

		formatter.format(template, usr)

		result:

		Hello world! Monkey D., Rufy.I live in penny lane n. 0  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 1  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 2  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 3  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 4  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 5  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 6  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 7  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 8  040404, Don't forget that my name is Monkey D.
		I live in penny lane n. 9  040404, Don't forget that my name is Monkey D.

- Internal template with a collection element searched by:

	- *constant*:

			template = "Hello world! {name}, {surname}.{(I live in {street} {cod}, Don't forget that my name is {super.name}: addresses[street == "penny lane n. 8 "] )}"
		

	- *variable*:

			template = "Hello world! {name}, {surname}.{(I live in {street} {cod}, Don't forget that my name is {super.name}: addresses[street == $my_street] )}"

			my_street = "penny lane n. 8 "
			formatter.format(template, usr, my_street = my_street)

	- *dictionary*:
			
			template = "Hello world! {name}, {surname}.{(I live in {street} {cod}, Don't forget that my name is {super.name}: addresses[street == $streets[name]] )}"

			streets = dict()
	        streets["Zoro"] = "street of holes"
	        streets["Monkey D."] = "penny lane n. 8 "

			formatter.format(template, usr, streets = streets)
			
	 all these give the same result:
		
		Hello world! Monkey D., Rufy.I live in penny lane n. 8  040404, Don't forget that my name is Monkey D.


- Conditional internal template:

		template = "Hello world! {name}, {surname}.{(my name is {name}: $streets[ name ] )}

		streets = dict()
        streets["Monkey D."] = True

		formatter.format(template, usr, streets = streets)

		streets["Monkey D."] = False

		formatter.format(template, usr, streets = streets)

		results:

		1. Hello world! Monkey D., Rufy.my name is Monkey D.

		2. Hello world! Monkey D., Rufy.


- **Complex example**: 
	- Use of super...super inside placeholder

			template = "Hello world! {name}, {surname}.
						{(I live in {street} {cod}, 
							{(my name is {super.super.name}, i live in {street}: addresses[street == "penny lane n. 8 "] )} 
						Don't forget that my name is {super.name}: addresses)}

			formatter.format(template, usr)

			result:

			Hello world! Monkey D., Rufy.I live in penny lane n. 0  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 1  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 2  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 3  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 4  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 5  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 6  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 7  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 8  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.I live in penny lane n. 9  040404, 
	         my name is Monkey D., i live in penny lane n. 8 
	
	         Don't forget that my name is Monkey D.

	- Show only some collection elements:

			template = "Hello world! {name}, {surname}.
						{(I live in {street} {cod}, 
                 			{(my name is {super.name}, i live in {street}: $streets[street] )} 
                 		Don't forget that my name is {super.name}: addresses)}
			
			streets = dict()
	        streets["penny lane n. 1 "] = True
	        streets["penny lane n. 2 "] = True
	        streets["penny lane n. 8 "] = True
	        streets["penny lane n. 3 "] = True

			formatter.format(template, usr, streets = streets)

			result:


			Hello world! Monkey D., Rufy.I live in penny lane n. 0  040404, 
                  
             Don't forget that my name is Monkey D.I live in penny lane n. 1  040404, 
             my name is Monkey D., i live in penny lane n. 1  
             Don't forget that my name is Monkey D.I live in penny lane n. 2  040404, 
             my name is Monkey D., i live in penny lane n. 2  
             Don't forget that my name is Monkey D.I live in penny lane n. 3  040404, 
             my name is Monkey D., i live in penny lane n. 3  
             Don't forget that my name is Monkey D.I live in penny lane n. 4  040404, 
              
             Don't forget that my name is Monkey D.I live in penny lane n. 5  040404, 
              
             Don't forget that my name is Monkey D.I live in penny lane n. 6  040404, 
              
             Don't forget that my name is Monkey D.I live in penny lane n. 7  040404, 
              
             Don't forget that my name is Monkey D.I live in penny lane n. 8  040404, 
             my name is Monkey D., i live in penny lane n. 8  
             Don't forget that my name is Monkey D.I live in penny lane n. 9  040404, 
              
             Don't forget that my name is Monkey D.

	- Use an attribute not directly associeted to the top level object

			template = "Hello world! {name}, {surname}.
						{(My Phone is {prefix}
                 			{(my name is {super.super.name}, i live in {street}: address)}
                 		{number}: phone)}"
			
			formatter.format(template, usr)

			result: 

			Hello world! Monkey D., Rufy.My Phone is 081
                 my name is Monkey D., i live in penny lane n. -1 
                  123456