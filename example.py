#!/usr/bin/env python
'''
Simple usage example of rubbersnake
'''

import rubbersnake as rs
import datetime


class User(rs.Model):

    #User properties
    username = rs.types.String(mapping={"index": "not_analyzed"})
    active = rs.types.Bool(default=True)
    userlevel = rs.types.Enum("MEMBER", "ADMIN", default="MEMBER")

    #Callables are fine as default values too
    registrationdate = rs.types.DateTime(default=lambda : datetime.datetime.utcnow())

    #Optionally extra mappings can be added (properties will be overriden with your model data)
    #_mapping = {}


#Get a mapping dict for the model
print(User().__mapping__)

#Instantiate a new user and save it
user = User({
    "username": "foobar",
}, _parent="AOEU")
print(user.__dict__)

#You can also trigger validations manually
user.__validate__()
