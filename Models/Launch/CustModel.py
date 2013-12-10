from google.appengine.ext import ndb
import logging
import random

# Keep track of customers by vertical

class Codes(ndb.Model):
    name = ndb.StringProperty()     # associated business name
    code = ndb.StringProperty()  
    category = ndb.IntegerProperty(default=3)    # 0 - pets, 1 - auto, 2 - equip
    
    def _pre_put_hook(self):
        self.code = self.name[0:3].upper() + str(random.randint(0,99)) + 'DEC'   
    
    @classmethod
    def by_code(cls,code):
        return cls.query().filter(cls.code==code).get()  
        
    @classmethod
    def by_name(cls,name):
        return cls.query().filter(cls.name==name).get()      