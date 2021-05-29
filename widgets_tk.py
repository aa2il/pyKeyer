#! /usr/bin/python
############################################################################################
#
# TK Widgets - Rev 1.0
# Copyright (C) 2021 by Joseph B. Attili, aa2il AT arrl DOT net
#
# Modified/augmented gui widgets
#
# To Do - does the standalone version work under python3?
#       - Proably should be part of a library.
#
############################################################################################
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
############################################################################################

import sys
if sys.version_info[0]==3:
    import tkinter as tk
    import tkinter.font
else:
    import Tkinter as tk
    import tkFont

################################################################################

# LCD which responds to mouse wheel & has a call back
class MyLCDNumber():
 
    def __init__(self,parent=None,ndigits=7,nfrac=1,signed=False,leading=False,val=0,wheelCB=None):
        self.wheelCB = wheelCB

        self.val=val
        FONT_SIZE=48    # 120

        # Determine total number of display "digits" including spaced and decimal point
        self.signed  = signed
        self.nfrac   = nfrac                                  # No. fractional position to right of decima
        self.nspaces = int( (ndigits-1)/3 )                   # No. spaces
        if self.nfrac>0:
            self.nspaces += 1
        ntot    = ndigits + self.nspaces + self.nfrac         # Total no. display digits
        if signed:
            ntot+=1
            
        if self.nfrac>0:
            self.fmt = str(ntot-1)+',.'+str(nfrac)+'f'            # Format spec for displaying value
        else:
            self.fmt = str(ntot)+',.'+str(nfrac)+'f'              # Format spec for displaying value
            
        if leading:
            self.fmt = '0'+self.fmt
        if signed:
            # This should cause plus signs but it doesn't
            self.fmt = '+'+self.fmt
        self.max_val = pow(10.,ndigits)-pow(10.,-nfrac)       # Maximum value
        if signed:
            self.min_val = -self.max_val
        else:
            self.min_val = 0
        #self.sc   = 1./120.                                   # Wheel scaling factor
        #print ndigits,self.nfrac,self.nspaces,ntot
        #print('fmt=',self.fmt)

        # Create label & bind mouse wheel events
        self.digitCount = ntot                                # Set no. of digits
        self.label = tk.Label(parent, font=('courier', FONT_SIZE, 'bold'), \
                         width=ntot,anchor='e')
        #self.label.pack(padx=40, pady=40)
        #self.label.pack()
        self.set(val)                                         # Display starting value
        #self.setFocusPolicy(Qt.StrongFocus)
        self.label.bind("<Button-4>", self.wheelEvent)
        self.label.bind("<Button-5>", self.wheelEvent)


    # Callback for mouse wheel event
    def wheelEvent(self,event):
        #print("wheelEvent:",self.val,event.num,event.x,event.y )

        if False:
            if event.num == 5 or event.delta == -120:
                self.val -= 1
            if event.num == 4 or event.delta == 120:
                self.val += 1
            self.set( self.val )
            return

        # Determine which digit the mouse was over when the wheel was spun
        x    = event.x                                    # Width of lcd widget
        ndig = self.digitCount                            # Includes spaces & dec point
        w    = self.label.winfo_width()                   # Width of the display
        edge = 0*.028*w                                     # Offset of border
        idx1 = (w-x-edge)*float(ndig) / (w-2*edge)        # Indicator of digit with mouse but...
        #print('x=',x,'ndig=',ndig,'w=',w,'edge=',edge,'idx1=',idx1)

        # ... Need to adjust for decimal point and spaces
        for n in range(self.nspaces):
            ns = 3*n+self.nfrac
            if idx1>ns and idx1<ns+1:
                idx1 -= 0.5                    # We're over a space or decimal point
            elif idx1>ns+1:
                idx1 -= 1                      # We're to the left of a space or decimal point 
        idx = int(idx1)                        # Finally, we can determine which digit it is
        #print('idx=',idx,ndig)
        if self.signed and idx>=ndig-1:
            idx-=1

        # Adjust step size based on digit 
        self.step = pow(10,idx-self.nfrac)
        if event.num == 5:
            delta = -1
        if event.num == 4:
            delta = 1

        # Display new value
        xx = self.val + self.step*delta
        #print(self.val,self.step,event.num,event.delta)
        #print '---',idx1,idx,xx,self.max_val
        self.set(xx)

        # Do additional work if necessary
        if self.wheelCB:
            self.wheelCB(xx)


    # Function to set LCD display value
    def set(self,f):
        if f!=None:
            self.val=min(max(f,self.min_val),self.max_val)
            #self.display(format(self.val,self.fmt))
            #self.label['text'] = self.val
            self.label['text'] = format(self.val,self.fmt)


    # Function to get LCD display value
    def get(self):
        return self.val

################################################################################

# Test program
if __name__ == '__main__':
    root = tk.Tk()
    root.title('turn mouse wheel')
    root['bg'] = 'darkgreen'
    
    lcd=MyLCDNumber(root)
    lcd.label.pack()
    
    root.mainloop()

