import os, sys, timeit, pickle

# Ajout du répertoire de la bibliothèque
curdir = os.path.dirname(__file__)
libdir = os.path.realpath(curdir+"/../src")
sys.path.append(libdir)

from panoptiscan_lib import Mouse

m = Mouse()
m.x = 2000
m.y = 2000
#m.button_left = True
#m.button_middle = True
#m.button_right = True
m.buttons = 4
ser = m.serialize()
print(len(ser))
print(ser)
ser2 = pickle.dumps(m)
print(len(ser2))