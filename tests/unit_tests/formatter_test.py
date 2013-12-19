# -*- coding: UTF-8 -*-
'''
Created on 12/nov/2013

@author: ross
'''
import unittest
from formatter.CoGePyFormatter import CoGePyFormatter

class Test(unittest.TestCase):

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
 
    @classmethod
    def setUpClass(cls):
        super(Test, cls).setUpClass()
        #Flush the file
        f= open("formatter_cases.txt", "w")
        f.close()
        
    def setUp(self):
        self.formatter = CoGePyFormatter()
        unittest.TestCase.setUp(self)
        self.usr = self.User()
        self.usr.init()
        self.a = "Hello world! {name}, {surname}."
        self.it_text = "I live in {street} {cod}, Don't forget that my name is {super.name}"        
        self.f = open("formatter_cases.txt", "a")
        self.f.write("\n-------------------------\n")
    
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.f.close()
        
    def testNoIT(self):
        
        print "NoIT"
        
        self.f.write("NoIT\n "+self.a)
        
        print self.formatter.format(self.a, self.usr)  

    def testITwithRmDoc(self):
        
        print "Rmdoc"
        
        b = self.a + "{("+self.it_text+": address)}"
        
        self.f.write("Rmdoc\n "+b)
        
        
        print self.formatter.format(b, self.usr)
        
    def testITwithVariable(self):
        
        print "Variable"
        
        address = self.User.Address(-1)
        b = self.a + "{("+self.it_text+": $address)}"
        
        self.f.write("Variable\n "+b)
        
        print self.formatter.format(b, self.usr, address = address)
        
    def testITwithCollection(self):
        
        print "Collection"
        
        b = self.a + "{("+self.it_text+"\n: addresses)}"
        
        self.f.write("Collection\n "+b)
        
        print self.formatter.format(b, self.usr)
        
    def testITwithSearchVar(self):
        
        print "Search Var"
        
        b = self.a + "{("+self.it_text+"\n: addresses[street == $my_street] )}"
        my_street = "penny lane n. 8 "

        self.f.write("Search Var\n "+b)
        
        print self.formatter.format(b, self.usr, my_street = my_street)
        
    def testITwithSearchConst(self):
        
        print "Search Const"
        
        b = self.a + "{("+self.it_text+"\n: addresses[street == \"penny lane n. 8 \"] )}"        
        
        self.f.write("Search Const\n "+b)
        
        print self.formatter.format(b, self.usr)
        
    def testITwithSearchDictionary(self):
        
        print "Search Dict"
        
        b = self.a + "{("+self.it_text+"\n: addresses[street == $streets[name]] )}"
        streets = dict()
        streets["Zoro"] = "street of holes"
        streets["Monkey D."] = "penny lane n. 8 "
        
        self.f.write("Search Dict\n "+b)
        
        print self.formatter.format(b, self.usr, streets = streets)        
        
    def testITNoneWithVar(self):
        
        print "NoneWithVar"
        
        b = self.a + "{("+self.it_text+": $address)}"        
    
        self.f.write("NoneWithVar\n"+b)
        
        print "1"+self.formatter.format(b, self.usr)
        print "2"+self.formatter.format(b, self.usr, address = None)
    def testITNoneWithRmdoc(self):
        
        print "NoneRmdoc"
        
        b = self.a + "{("+self.it_text+": NoAddress)}"
        
        self.f.write("NoneRmdoc\n"+b)
        print self.formatter.format(b, self.usr)
        
    def testITNoneWithSearch(self):
        
        print "NoneSearch"
        
        b = self.a + "{("+self.it_text+"\n: addresses[street == $my_street] )}"
        my_street = "of mine n. 8"
    
        self.f.write("NoneSearch\n"+b)
        
        print "1"+self.formatter.format(b, self.usr, my_street=my_street)
        print "2"+self.formatter.format(b, self.usr)
        
    def testITIF(self):
        
        print "IF"    
                
        streets = dict()
        streets["Monkey D."] = True
        
        b = self.a + "{(my name is {name}: $streets[ name ] )}"
        print "1"+self.formatter.format(b, self.usr, streets = streets)
        
        streets["Monkey D."] = False
            
        self.f.write("IF\n"+b)
        
        print "2"+self.formatter.format(b, self.usr, streets = streets)
        
    def testITOnlyforSomeElemOfCollection(self):
        
        print "Only some collection elems"
        
        b = (self.a + 
             """{(I live in {street} {cod}, 
                 {(my name is {super.name}, i live in {street}: $streets[street] )} 
                 Don't forget that my name is {super.name}: addresses)}"""
                 )
        
        streets = dict()
        streets["penny lane n. 1 "] = True
        streets["penny lane n. 2 "] = True
        streets["penny lane n. 8 "] = True
        streets["penny lane n. 3 "] = True
        
        self.f.write("Only some collection elems\n"+b)
        
        
        print self.formatter.format(b, self.usr, streets = streets)
    
    def testDeepSearchRmDoc(self):
        
        print "Deep Search rmdoc"
        
        b = (self.a + 
             """{(I live in {street} {cod}, 
                 {(my name is {super.super.name}, i live in {street}: addresses[street == \"penny lane n. 8 \"] )} 
                 Don't forget that my name is {super.name}: addresses)}"""
                 )
        
        self.f.write("Deep Search rmdoc\n"+b)
        
        
        print self.formatter.format(b, self.usr)
        
    
    def testDeepRmDoc(self):
         
        print "Deep rmdoc"
         
        b = (self.a + 
             """{(My Phone is {prefix}
                 {(my name is {super.super.name}, i live in {street}: address)}
                  {number}: phone)}"""
                 )
        
        self.f.write("Deep rmdoc\n"+b)
         
        print self.formatter.format(b, self.usr)
        
        
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()