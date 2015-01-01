#!/usr/bin/env python

a = 'aa'
b = 'be'

class Foo():
  def __init__(self):
    global a, b
    a = 'fooaa'
    b = 'foobe'

f = Foo()

def inc():
  global a
  a = 555

def get(isA):
  return a if isA else b

def set(value):
  global a, b
  a = value
  b = value

def printa():
  print 'Printuju a: %s' % a

print 'MODULE INIT: %s' % a
