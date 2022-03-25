# -*- coding: utf-8 -*-

from root import Root
from tx_model import TxModel
from rx_model import RxModel

"""
    This is the Main function for the programme.
"""
def main():
    root = Root()
    root.mainloop()

"""
    This is a Command Line Interface Test function.
"""
def test_pr():
    t1 = TxModel(x=-0.5, y=0.25, z=2.195, pr=2.424162777141011e-06)
    t2 = TxModel(x=-0.5, y=0.6, z=2.195, pr=1.805735942220138e-06)
    t3 = TxModel(x=0.5, y=0.25, z=2.195, pr=8.324370247537219e-07)
    #t4 = TxModel(x=-1.5, y=-1.5, z=3, pr=0.4577E-3)
    txs = [t1, t2, t3]
    r = RxModel(-0.2, 0, 0.175, 7.0686e-2, txs, 0)
    print("Location : x =", r.x, ", y =", r.y)
    
def test2_pr():
    #Pt = 20886
    #Pr = 3354
    t1 = TxModel(x=-0.5, y=0.25, z=2.195, pr=3354)
    t2 = TxModel(x=-0.5, y=0.6, z=2.195, pr=3354)
    t3 = TxModel(x=0.5, y=0.25, z=2.195, pr=3354)
    #t4 = TxModel(x=-1.5, y=-1.5, z=3, pr=0.4577E-3)
    txs = [t1, t2, t3]
    r = RxModel(0, 0, 0.85, 7.0686e-2, txs, 0)
    print("Location : x =", r.x, ", y =", r.y)


# Choose the function want to run
if __name__ == "__main__":
    #test2_pr()
    main()
