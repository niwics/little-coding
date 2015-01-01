#!/usr/bin/env python

import mod
from mod import a, b, inc, printa, get, set

print 'A po importu: %s, %s' % (a, mod.a)
print 'Get A: %s' % get(True)
print 'B po importu: %s, %s' % (b, mod.b)

mod.a = 7
printa()
#inc()

# kdyz to tady neni tak 
#from mod import a


print 'A: %s, %s' % (a, mod.a)
print 'Get A: %s' % get(True)
set(333)
print 'Get A po setu: %s' % get(True)
print 'test: %s' % a
print 'test get: %s' % get(True)
printa()
