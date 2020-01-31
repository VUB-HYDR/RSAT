# -*- coding: utf-8 -*-
"""
Documentation: RSAT_0.2.0_usermanual.pdf
Written in python 3.7 by Annabel Vaessens, Gert Ghysels and Ferdinand Guggeis
January 2020
#"""

import time
import itertools
import math
import matplotlib.pyplot as plt
import matplotlib.backends.backend_tkagg as pltb  
import numpy as np
import os
import pandas as pd 
import string
import tkinter as tk 

########################### FUNCTIONS ###############################
class Program:    
    def newDirectory(self): #changes the directory: this will be the map that opens when opening and saving files
        self.newDirectory= tk.filedialog.askdirectory()
        tk.Label(GUI, text=self.newDirectory[-35:],font=("Helvetica", "8"), width='32', foreground='navy').grid(row=i-5, column=j, sticky='W')
        os.chdir(self.newDirectory)
            
    def OpenFile(self): # opens file where the horizontal hydraulic conductivity calculations are performed on
        self.ListNamesCols=[]
        filenameDir=tk.filedialog.askopenfilename(filetypes = [("DAT files","*.dat"),("All Files","*")])
        self.RAWDATA=pd.read_csv(filenameDir,decimal=',',delim_whitespace=True,header=None, names=['Time [s]','Transducer [V]','Head [ft]','Head [mm]','Pressure [mbar]']) 
        try:
            self.dfRAWDATA=pd.DataFrame(self.RAWDATA.astype(float))
        except ValueError:
            tk.messagebox.showerror("Warning", "The input file contains characters, which cannot be converted to float (literals or wrong/mixed decimal seperators) \nOnly '.' OR ',' are allowed as seperator!")
        self.filename=str(filenameDir.split('/')[-1]) # gives the file name you have selected
        self.ListNamesCols=['Time [s]', self.filename]
        tk.Label(GUI, text=self.filename,font=("Helvetica", "9"), foreground='navy').grid(row=i-3, column=j, sticky='W')
        
    def SaveFig(self): # to save figures that are created
        NameFig=tk.filedialog.asksaveasfilename(title= 'Save as', confirmoverwrite=True, initialdir=self.newDirectory)
        self.Figure.savefig(NameFig + '.pdf', bbox_inches='tight')
    
    def Canvas(self, figure, m, r, c): # to make a canvas and display the figure in a pop-up window
        canvas = pltb.FigureCanvasTkAgg(figure, master=m)
        canvas.draw()
        canvas.get_tk_widget().grid(row=r, column=c)
        
    def PlotDataSeperateBox(self): # plots the imported data in a pop-up window
        box = tk.Toplevel(background='snow', cursor='crosshair')
        box.title("Data "+ self.filename )
        FigRawData = plt.figure(figsize=(13,8),facecolor='snow')
        plt.title(self.filename, fontsize=16)
        ax1 = FigRawData.add_subplot(111)
           
        self.dfRAWDATA.plot(x='Time [s]', y='Head [mm]',ax=ax1)
        plt.ylabel('Head [mm]', fontsize=14)
        plt.xlabel('Time [s]', fontsize=14)
        plt.axis([self.dfRAWDATA.iloc[0,0]-len(self.dfRAWDATA)/60,self.dfRAWDATA.iloc[-1,0]+len(self.dfRAWDATA)/60,min(self.dfRAWDATA.iloc[:,3])-20,max(self.dfRAWDATA.iloc[:,3])+20])
        
        self.Canvas(FigRawData,box, 0,0)
    
        self.Figure=FigRawData # for using in the save-function
        tk.Button(box, text="Save figure", command=self.SaveFig, width=10).grid(row=2,column=2) # option to save the figure
        tk.Button(box, text="Close", command=box.destroy, width=10).grid(row=3,column=2) # option to close the pop up window
    
    # making a clickable graph in a pop-up window, where the boundaries of individual measurements can be clicked
    def ClickableGraph(self):
        self.PlotDataSeperateBox()    
        self.NumPoints=int(NM.get())*2 # two times the amount of measurements need to be clicked   
        BoundPoints1=list(plt.ginput(self.NumPoints, show_clicks=True)) # list makes a list of the tuple that ginput gives
        self.BoundPoints=list(itertools.chain.from_iterable(BoundPoints1)) 
    
    # splitting the imported data in individual measurements with the clicks defined in ClickableGraph()
    def SplitRawData(self):
        x=0
        y=1
        while (x < len(self.BoundPoints)-1): #(len(BoundPoints)-1)/4 is the amount of repetitions needed, this is equal to the amount of measurements
            DistFirstPoint=[]
            DistSecondPoint=[]
            RAWDATASliced=[]
            for P in range(0,self.dfRAWDATA.count(axis='rows')[0]):
                DistFirstPoint.append(math.sqrt((self.BoundPoints[x]-self.dfRAWDATA.iloc[P,0])**2 + (self.BoundPoints[y]-self.dfRAWDATA.iloc[P, 3])**2 )) 
                DistSecondPoint.append(math.sqrt((self.BoundPoints[x+2]-self.dfRAWDATA.iloc[P,0])**2 +(self.BoundPoints[y+2]-self.dfRAWDATA.iloc[P, 3])**2 ))
            FirstPoint_Data=min(DistFirstPoint)
            SecondPoint_Data=min(DistSecondPoint)
            IndexFirstPoint=DistFirstPoint.index(FirstPoint_Data)
            IndexSecondPoint=DistSecondPoint.index(SecondPoint_Data)
            RAWDATASliced=self.dfRAWDATA[IndexFirstPoint:IndexSecondPoint+1]
            self.RepeatMeas=list(string.ascii_uppercase)
            RAWDATASliced.to_csv(self.filename[:-4]+'_proc'+self.RepeatMeas[int(x/4)]+'.dat', header=False, index=False, sep=' ') 
            x=x+4
            y=y+4
        tk.messagebox.showinfo('Info', 'Splitting in individual measurements was successful. You can find the individual measurements in the current working directory.')
    
    # function that opens multiple (or one) individual measurements, let the user define location of the baselevel and splits the data (from the minimum head to the recovered head or end of the data)
    def RepeatabilityOpen(self):
        self.BaseLevelList=[]
        self.BaseLevelListLL=[]
        self.listNamesRepMeas_H=[] # list with only the names of the columns containing head data
        self.listNamesRepMeas_TH=[] # list with the column names of the repeated measurements that were selected
        self.Q=0 
        try:
            filenameDir=tk.filedialog.askopenfilenames(filetypes = [("DAT files","*.dat"),("All Files","*")])
            filenameDirList=list(filenameDir)  
            self.DFSlicedNormHead_Rep=pd.DataFrame()
            while self.Q < len(filenameDirList):
                self.DATA=pd.read_csv(filenameDirList[self.Q],decimal=',',delim_whitespace=True,header=None, names=['Time [s]','Transducer [V]','Head [ft]','Head [mm]','Pressure [mbar]'])
                self.dfDATA=pd.DataFrame(self.DATA.astype(float))
                filenameRepeat=str((filenameDir[self.Q].split('/')[-1]).split('.')[0])
                self.listNamesRepMeas_H.append(filenameRepeat)
                self.listNamesRepMeas_TH.append('Time_'+filenameRepeat)
                self.listNamesRepMeas_TH.append(filenameRepeat)
                tk.Label(GUI, text=filenameRepeat,font=("Helvetica", "9"), foreground='navy').grid(row=i+7+self.Q, column=j+1)
                
                #open a new pop-up window
                box2 = tk.Toplevel(background='snow', cursor='crosshair')
                box2.title("Data "+ filenameRepeat+ '  -- Indicate the last baselevel value')
                FigRepBaselvl = plt.figure(figsize=(13,8),facecolor='snow')
                plt.title('Indicate the last baselevel value', fontsize=16)
                ax2 =  FigRepBaselvl.add_subplot(111)
                                    
                self.dfDATA.plot(x='Time [s]', y='Head [mm]',ax=ax2) 
                plt.xlabel('Time [s]', fontsize=14)
                plt.ylabel('Head [mm]', fontsize=14)
            
                self.Canvas(FigRepBaselvl, box2, 0,0)
            
                BaseLevel=list(itertools.chain.from_iterable(plt.ginput(1, show_clicks=True)))
                self.BaseLevelListLL.append(BaseLevel) 
                self.BaseLevelList= [val for sublist in self.BaseLevelListLL for val in sublist]
            
                self.SplitProcData()
                box2.destroy()
                self.Q=self.Q+1
                
            self.DFSlicedNormHead_Rep.columns=self.listNamesRepMeas_TH
        except ValueError:
                tk.messagebox.showerror("Warning", "The input file contains characters, which cannot be converted to float (literals or wrong/mixed decimal seperators) \nOnly '.' OR ',' are allowed as seperator!")
            
    
    # used in RepeatabilityOpen; splits the data file into the part used for the normhead-time curves (from the minimum head to the recovered head or end of the data)
    def SplitProcData(self):
        self.DFSlicedNormHead_Rep_1Meas=pd.DataFrame() 
        DistBaseLevel=[]
        for P in range(0,self.dfDATA.count(axis='rows')[0]):
            DistBaseLevel.append(math.sqrt((self.BaseLevelList[self.Q*2]-self.dfDATA.iloc[P,0])**2 + (self.BaseLevelList[(self.Q*2)+1]-self.dfDATA.iloc[P,3])**2 )) #oke
        MinDistBaseLevel=min(DistBaseLevel)
        IndexMinDistBaseLevel=DistBaseLevel.index(MinDistBaseLevel)
        BaseLevel=np.mean(self.dfDATA.iloc[IndexMinDistBaseLevel-10:IndexMinDistBaseLevel,3]) # baselevel is average of ten points before the clicked point
        MinHead2=min(self.dfDATA.iloc[:,3])
        IndexMin2=self.dfDATA['Head [mm]'].idxmin()
        k=IndexMin2
        while (self.dfDATA.iloc[k,3]<= BaseLevel) and (self.dfDATA.iloc[k,3] < self.dfDATA.iloc[-1,3]):
            k=k+1
        if self.dfDATA.iloc[k,3] < BaseLevel:
            tk.messagebox.showinfo("Warning", "Recovery is not reached for this measurement")
        self.DFSlicedNormHead_Rep_1Meas[self.listNamesRepMeas_TH[2*self.Q]]=self.dfDATA.iloc[IndexMin2:k,0]
        self.DFSlicedNormHead_Rep_1Meas[self.listNamesRepMeas_TH[2*self.Q+1]]=self.dfDATA.iloc[IndexMin2:k,3]
        for w in range (0,k-IndexMin2):
            self.DFSlicedNormHead_Rep_1Meas.iloc[w,1]=(BaseLevel-self.DFSlicedNormHead_Rep_1Meas.iloc[w,1])/(BaseLevel- MinHead2) # normalized head of the sliced part (minhead to baselevel)
            self.DFSlicedNormHead_Rep_1Meas.iloc[w,0]=self.DFSlicedNormHead_Rep_1Meas.iloc[w,0]-self.dfDATA.iloc[IndexMin2,0] # we need the time for each measurement in order to plot measurements with different frequencies on one graph
        self.DFSlicedNormHead_Rep=pd.concat((self.DFSlicedNormHead_Rep, self.DFSlicedNormHead_Rep_1Meas),ignore_index=True, axis=1)
    
    # general settings to plot the normalized head vs time curves in a pop-up window
    # used in PlotNormHead_Time() and PlotNormHead_LogTime()
    def Multi_plot(self, title,label,xscale): 
        box3 = tk.Toplevel(background='snow')
        box3.title( title +" "+", ".join(str(x) for x in self.listNamesRepMeas_H))
            
        RepFig = plt.figure(figsize=(13,8),facecolor='snow') # RepFig stands for 'Repeated measurements figures'
        plt.title(label, fontsize=16)
        ax4 = RepFig.add_subplot(111)
        ax4.set(xscale = xscale )
        plt.xlabel(xscale +' Time [s]', fontsize=14)
        plt.ylabel('Normalized Head [-]', fontsize=14)
        
        i=0
        for i in range(0, len(self.listNamesRepMeas_TH)-1,2):       
            plt.plot(self.DFSlicedNormHead_Rep[self.listNamesRepMeas_TH[i]], self.DFSlicedNormHead_Rep[self.listNamesRepMeas_TH[i+1]]) # plotting in this way makes the frequency of the data incorporated by itself
        plt.legend(self.listNamesRepMeas_H, fontsize='large')
        
        self.Canvas(RepFig,box3,1,0)
            
        self.Figure=RepFig # to use in SaveFig-function
        tk.Button(box3, text="Save figure", command=self.SaveFig, width=10).grid(row=2,column=2)
        tk.Button(box3, text="Close", command=box3.destroy, width=10).grid(row=3,column=2)
    
    def PlotNormHead_Time(self): # specific settings for the normalized head vs time curves
        title = 'Normalized Head versus Time of measurements'
        label = 'Normalized Head versus Time'
        xscale='linear'
        self.Multi_plot(title,label,xscale)
        
    def PlotNormHead_LogTime(self): # specific settings for the normalized head vs log(time) curves
        title = 'Normalized Head versus time (logscale) of measurements'
        label = 'Plot Normalized Head versus Log Time'
        xscale='log'
        self.Multi_plot(title,label,xscale)
    
    # Bouwer-Rice calculations for unconfined aquifer, partially penetrating well
    # used in PerformCalc()
    def KhBouwerRice_PP(self): 
        coeff=math.log((self.AqThick-(self.d+self.Le))/(self.rw*math.sqrt(self.Aniso)))
        if coeff > 6:
            coeff=6
        A = 1.4720 + 0.03537*(self.Le/(self.rw*math.sqrt(self.Aniso)))-0.00008148*(self.Le/(self.rw*math.sqrt(self.Aniso)))**2+0.0000001028*(self.Le/(self.rw*math.sqrt(self.Aniso)))**3-0.00000000006484*(self.Le/(self.rw*math.sqrt(self.Aniso)))**4+0.00000000000001573*(self.Le/(self.rw*math.sqrt(self.Aniso)))**5
        B = 0.2372 + 0.005151*(self.Le/(self.rw*math.sqrt(self.Aniso))) - 0.000002682*(self.Le/(self.rw*math.sqrt(self.Aniso)))**2 - 0.0000000003491*(self.Le/(self.rw*math.sqrt(self.Aniso)))**3 + 0.0000000000004738*(self.Le/(self.rw*math.sqrt(self.Aniso)))**4
        self.Kh_BR_PP_cms=self.rc*self.rc*(1.1/math.log((self.d+self.Le)/(self.rw*math.sqrt(self.Aniso)))+((A+(B*coeff))/self.Le*self.rw*math.sqrt(self.Aniso)))**(-1)/(2*self.Le*self.T01)/10 # /10 to go from mm/s to cm/s
        self.Kh_BR_PP_cms=round(self.Kh_BR_PP_cms,5) # rounding off to five decimals
        self.Kh_BR_PP_md=self.Kh_BR_PP_cms*864
        self.Kh_BR_PP_md=round(self.Kh_BR_PP_md, 5)
    
    # Bouwer-Rice calculations for unconfined aquifer, fully penetrating well, used in PerformCalc()    
    def KhBouwerRice_FP(self): 
        C=0.7920+0.03993*(self.Le/(self.rw*math.sqrt(self.Aniso)))-0.00005743*(self.Le/(self.rw*math.sqrt(self.Aniso)))**2+0.00000003858*(self.Le/(self.rw*math.sqrt(self.Aniso)))**3-0.000000000009659*(self.Le/(self.rw*math.sqrt(self.Aniso)))**4
        self.Kh_BR_FP_cms=self.rc*self.rc*(1.1/math.log((self.d+self.Le)/(self.rw*math.sqrt(self.Aniso)))+(C/self.Le*self.rw*math.sqrt(self.Aniso)))**(-1)/(2*self.Le*self.T01)/10
        self.Kh_BR_FP_cms=round(self.Kh_BR_FP_cms,5 )
        self.Kh_BR_FP_md=self.Kh_BR_FP_cms*864
        self.Kh_BR_FP_md=round(self.Kh_BR_FP_md,5)
        
    # Hvorslev calculations for confined aquifer, partially penetrating well    
    def KhHvorslev_PP(self): 
        F=1/(2*math.sqrt(self.Aniso)/(self.Le/self.rw)) + math.sqrt(1 + (1/(2*math.sqrt(self.Aniso)/(self.Le/self.rw)))**2)
        self.Kh_H_PP_cms = (self.rc*self.rc*math.log(F)) / (2*self.Le*self.T01)/10
        self.Kh_H_PP_cms=round(self.Kh_H_PP_cms,5)
        self.Kh_H_PP_md = self.Kh_H_PP_cms * 864
        self.Kh_H_PP_md=round(self.Kh_H_PP_md,5)
        
    # Hvorslev calculations for confined aquifer, fully penetrating well
    def KhHvorslev_FP(self): 
        self.Kh_H_FP_cms=(self.rc*self.rc*math.log(self.re/self.rw))/(2*self.AqThick*self.T01)/10
        self.Kh_H_FP_cms=round(self.Kh_H_FP_cms,5)
        self.Kh_H_FP_md=self.Kh_H_FP_cms*864
        self.Kh_H_FP_md=round(self.Kh_H_FP_md,5)
        
    # pop-up window for the user to define the baselevel
    # used in PerformCalc()
    def DefBaseLevel(self):
        box4 = tk.Toplevel(background='snow', cursor='crosshair')
        box4.title("Data "+ self.filename + '  -- Indicate the last baselevel value')
     
        FigBaselvl = plt.figure(figsize=(13,8),facecolor='snow')
        plt.title('Indicate the last baselevel value '+ self.filename, fontsize=16)
        ax5 = FigBaselvl.add_subplot(111)
                                
        self.dfRAWDATA.plot(x='Time [s]', y='Head [mm]',ax=ax5)
        plt.xlabel('Time [s]', fontsize=14)
        plt.ylabel('Head [mm]', fontsize=14)
    
        self.Canvas(FigBaselvl, box4,0,0)
        
        self.EstBaseLevel=list(itertools.chain.from_iterable(plt.ginput(1, show_clicks=True)))
        
        box4.destroy()
    
    # for checking whether there are limitations for certain methods. 
    # used in the button 'Check limitations'
    def CheckLimitations(self):
        self.DefBaseLevel()
        DistBaseLevel=[]
        for P in range(0,self.dfRAWDATA.count(axis='rows')[0]):
            DistBaseLevel.append(math.sqrt((self.EstBaseLevel[0]-self.dfRAWDATA.iloc[P,0])**2 + (self.EstBaseLevel[1]-self.dfRAWDATA.iloc[P,3])**2 )) #oke
        MinDistBaseLevel=min(DistBaseLevel)
        IndexMinDistBaseLevel=DistBaseLevel.index(MinDistBaseLevel)
        self.BaseLevel=np.mean(self.dfRAWDATA.iloc[IndexMinDistBaseLevel-10:IndexMinDistBaseLevel,3])
        self.MinHead=min(self.dfRAWDATA.iloc[:,3])
        self.H0=self.BaseLevel-self.MinHead
        IndexMin=self.dfRAWDATA.iloc[:,3].idxmin()
        k=IndexMin
        while (self.dfRAWDATA.iloc[k,3]<= self.BaseLevel) and (self.dfRAWDATA.iloc[k,3] < self.dfRAWDATA.iloc[-1,3]):
            k=k+1
        self.DFSlicedNormHead=pd.DataFrame([self.dfRAWDATA.iloc[IndexMin:k,0], self.dfRAWDATA.iloc[IndexMin:k,3]], index=self.ListNamesCols)
        self.DFSlicedNormHead=self.DFSlicedNormHead.transpose()
        for w in range (0,k-IndexMin):
            self.DFSlicedNormHead.iloc[w,1]=(self.BaseLevel-self.DFSlicedNormHead.iloc[w,1])/(self.H0) # normalized head of the sliced part (minhead to baselevel)
            self.DFSlicedNormHead.iloc[w,0]=self.DFSlicedNormHead.iloc[w,0]-self.dfRAWDATA.iloc[IndexMin,0] #  start time for each measurement should be zero in order to plot measurements with different frequencies on one graph
        if self.DFSlicedNormHead.iloc[-1,1]>0.30:
            tk.messagebox.showinfo("Info", "Recovery is not reached for this measurement. Maximum normalized head is "+ str(round(self.DFSlicedNormHead.iloc[-1,1],2)) + ', "No full recovery" and "All data" methods are limited to the range 1 - '+ str(round(self.DFSlicedNormHead.iloc[-1,1],2)) + '. No "Best range" methods can be calculated.')
        elif self.DFSlicedNormHead.iloc[-1,1]>0.25:
            tk.messagebox.showinfo("Info", "Recovery is not reached for this measurement. Maximum normalized head is "+ str(round(self.DFSlicedNormHead.iloc[-1,1],2)) + '. Hvorslev best range cannot be calculated.' +' "All data" and "Bouwer-Rice best range" methods are limited to the range 1 - '+ str(round(self.DFSlicedNormHead.iloc[-1,1],2)))
        elif self.DFSlicedNormHead.iloc[-1,1]>0.20:
            tk.messagebox.showinfo("Info", "Recovery is not reached for this measurement. Maximum normalized head is "+ str(round(self.DFSlicedNormHead.iloc[-1,1],2)) + '. "All data" methods are limited to the range 1 - '+str(round(self.DFSlicedNormHead.iloc[-1,1],2)) +', best range for Bouwer-Rice is limited to the range 0.30 - '+str(round(self.DFSlicedNormHead.iloc[-1,1],2)) + ', "Hvorslev best range" method is limited to 0.25 - '+str(round(self.DFSlicedNormHead.iloc[-1,1],2))+ '.')
        elif self.DFSlicedNormHead.iloc[-1,1]>0.15:
            tk.messagebox.showinfo("Info", "Recovery is not reached for this measurement. Maximum normalized head is "+ str(round(self.DFSlicedNormHead.iloc[-1,1],2)) + '. "All data" methods are limited to the range 1 - '+str(round(self.DFSlicedNormHead.iloc[-1,1],2))+ ', Hvorlsev best range is limited to the range 0.25 - '+str(round(self.DFSlicedNormHead.iloc[-1,1],2))+ '.')     
        elif self.DFSlicedNormHead.iloc[-1,1]>0:
            tk.messagebox.showinfo("Info", "Recovery is not reached for this measurement, but all calculation methods are possible.")     
        else:
            tk.messagebox.showinfo("Info", "Recovery is reached for this measurement. No limitations for calculation methods")
            
    # splits the data and calculates the log of the normalized heads
    # used in PerformCalc()
    def SplitProcDataForCalc(self): 
        DistBaseLevel=[]
        for P in range(0,self.dfRAWDATA.count(axis='rows')[0]):
            DistBaseLevel.append(math.sqrt((self.EstBaseLevel[0]-self.dfRAWDATA.iloc[P,0])**2 + (self.EstBaseLevel[1]-self.dfRAWDATA.iloc[P,3])**2 )) 
        MinDistBaseLevel=min(DistBaseLevel)
        IndexMinDistBaseLevel=DistBaseLevel.index(MinDistBaseLevel)
        self.BaseLevel=np.mean(self.dfRAWDATA.iloc[IndexMinDistBaseLevel-10:IndexMinDistBaseLevel,3])
        self.MinHead=min(self.dfRAWDATA.iloc[:,3])
        self.H0=self.BaseLevel-self.MinHead
        IndexMin=self.dfRAWDATA.iloc[:,3].idxmin()
        k=IndexMin
        while (self.dfRAWDATA.iloc[k,3]<= self.BaseLevel) and (self.dfRAWDATA.iloc[k,3] < self.dfRAWDATA.iloc[-1,3]):
            k=k+1
        if self.dfRAWDATA.iloc[k,3] < self.BaseLevel:
            tk.messagebox.showinfo("Info", "Recovery is not reached for this measurement")
        self.DFSlicedNormHead=pd.DataFrame([self.dfRAWDATA.iloc[IndexMin:k,0], self.dfRAWDATA.iloc[IndexMin:k,3]], index=self.ListNamesCols)
        self.DFSlicedNormHead=self.DFSlicedNormHead.transpose()
        for w in range (0,k-IndexMin):
            self.DFSlicedNormHead.iloc[w,1]=(self.BaseLevel-self.DFSlicedNormHead.iloc[w,1])/(self.H0) # normalized head of the sliced part (minhead to baselevel)
            self.DFSlicedNormHead.iloc[w,0]=self.DFSlicedNormHead.iloc[w,0]-self.dfRAWDATA.iloc[IndexMin,0] # start time for each measurement should be zero in order to plot measurements with different frequencies on one graph
        # slicing the normalized heads list to the desired ranges for the calculations and taking the logs that are used in the linear regression:
        self.DFSlicedNormHead_All=self.DFSlicedNormHead[(self.DFSlicedNormHead[self.ListNamesCols[1]]>=0.035)&(self.DFSlicedNormHead[self.ListNamesCols[1]]<=1)]
        if (V3.get()==True) or (V6.get()==True) or (V9.get()==True) or (V12.get()==True):
            self.DFSlicedLogNormHead_All=self.DFSlicedNormHead_All.copy() # copy() is needed for not overwriting the original dataframe
            self.DFSlicedLogNormHead_All[self.ListNamesCols[1]]=self.DFSlicedNormHead_All[self.ListNamesCols[1]].map(lambda a: math.log(a))
        if (V1.get()==True) or (V4.get()==True):
            self.DFSlicedNormHead_RangeBR=self.DFSlicedNormHead[(self.DFSlicedNormHead[self.ListNamesCols[1]]>=0.2)&(self.DFSlicedNormHead[self.ListNamesCols[1]]<=0.3)]
            self.DFSlicedLogNormHead_RangeBR=self.DFSlicedNormHead_RangeBR.copy()
            self.DFSlicedLogNormHead_RangeBR[self.ListNamesCols[1]]=self.DFSlicedNormHead_RangeBR[self.ListNamesCols[1]].map(lambda a: math.log(a))
        if (V7.get()==True) or (V10.get()==True):
            self.DFSlicedNormHead_RangeH=self.DFSlicedNormHead[(self.DFSlicedNormHead[self.ListNamesCols[1]]>=0.15)&(self.DFSlicedNormHead[self.ListNamesCols[1]]<=0.25)]
            self.DFSlicedLogNormHead_RangeH=self.DFSlicedNormHead_RangeH.copy()
            self.DFSlicedLogNormHead_RangeH[self.ListNamesCols[1]]=self.DFSlicedNormHead_RangeH[self.ListNamesCols[1]].map(lambda a: math.log(a))
        if (V2.get()==True) or (V5.get()==True) or (V8.get()==True) or (V11.get()==True):   
            self.DFSlicedNormHead_Begin=self.DFSlicedNormHead[(self.DFSlicedNormHead[self.ListNamesCols[1]]>=0.3)&(self.DFSlicedNormHead[self.ListNamesCols[1]]<=1)]
            self.DFSlicedLogNormHead_Begin=self.DFSlicedNormHead_Begin.copy()
            self.DFSlicedLogNormHead_Begin[self.ListNamesCols[1]]=self.DFSlicedNormHead_Begin[self.ListNamesCols[1]].map(lambda a: math.log(a))  
        
    # determines the linear regression coefficients for the corresponding range of selected data (All data/ 0.20-0.30/ 0.15-0.25 /0.3-1)
    # used in Performalc()
    def LinearRegression(self,DFSlicedLogNormHead_X): 
        self.LinRegCoef=np.polyfit(DFSlicedLogNormHead_X[self.ListNamesCols[0]], DFSlicedLogNormHead_X[self.ListNamesCols[1]],1)
        self.H01=math.exp(self.LinRegCoef[1])*self.H0
        self.T01=(-1-self.LinRegCoef[1])/self.LinRegCoef[0]
        #LinRegCorr=np.corrcoef(DFSlicedLogNormHead_X[ListNamesCols[0]], DFSlicedLogNormHead_X[ListNamesCols[1]])[0,1] # not used, but can be implemented when information regarding the regression fit is wanted
        self.dfFit=pd.DataFrame([np.array(range(0,len(self.DFSlicedNormHead.index)+1)), [math.exp(i) for i in self.LinRegCoef[0]*np.array(range(0,len(self.DFSlicedNormHead.index)+1)+self.LinRegCoef[1])]], index=self.ListNamesCols)
        self.dfFit=self.dfFit.transpose()
    
    # pop-up window with the regression results
    # used in PerformCalc()    
    def PlotRegResults(self): 
        box5 = tk.Toplevel(background='snow')
        box5.title("Regression results for "+ self.filename)
        
        self.PlotRegRes = plt.figure(figsize=(7,7),facecolor='snow')
        plt.title("Regression results for "+ self.filename, fontsize=16)
        self.ax3= plt.subplot(111)
        plt.ylabel('Normalized Head [mm]', fontsize=14)
        plt.xlabel('Time [s]', fontsize=14)
        self.DFSlicedNormHead_All.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1], ax=self.ax3, logy=True,color='c')
    
        self.Canvas(self.PlotRegRes, box5,0,0)
    
    # shows a pop up window with a table with the calculated hydraulic conductivity values
    # used in PerformCalc()    
    def TableResults(self):  
        box6 = tk.Toplevel(background='snow')
        box6.title("Horizontal hydraulic conductivity results for "+ self.filename)
        tk.Label(box6,text='Horizontal hydraulic conductivity results for ' + self.filename, background='snow',font=("Helvetica", "14")).grid(row=0, column=1)
        tk.Label(box6, text=' ', width=10, background='snow').grid(row=0, column=0)
        
        TableResults= plt.figure(figsize=(16,5),facecolor='snow')
        plt.subplot(111)
        cell_text = []
        for row in range(len(self.ResultsK)):
            cell_text.append(self.ResultsK.iloc[row])
    
        ResultsTable=plt.table(cellText=cell_text, rowLabels=self.ResultsK.index, colLabels=self.ResultsK.columns, colWidths=[0.20,0.20,0.20,0.20], loc='center')
        ResultsTable.set_fontsize(14)
        ResultsTable.scale(1,2)
        plt.axis('off')
        
        self.Canvas(TableResults, box6, 1,1)
    
    # checks which calculations options are checked and performs the hydraulic conductivity calculations, shows the results in pop-up windows    
    def PerformCalc(self): 
        try:
            self.LinearReg_Coeff=[]
            self.Aniso=float(ANISO.get())
            self.d=float(D.get())*10
            self.Le=float(LE.get())*10
            self.rc=float(RC.get())*10
            self.rw=float(RW.get())*10
            LegendList=['Measurements']
            self.DefBaseLevel()
            self.SplitProcDataForCalc()
            # making results dataframe for hydraulic conductivities
            iterables=[['Best range','No full recovery','All data'],['[cm/s]','[m/d]']]
            index = pd.MultiIndex.from_product(iterables)
            self.ResultsK=pd.DataFrame(np.nan,index=index,columns=['Bouwer-Rice, fully p.','Bouwer-Rice, partially p.','Hvorslev, fully p.','Hvorslev, partially p.'])
            # making results dataframe for H0 and T0
            iterables2=[['Best range','No full recovery','All data'],['H0+','T0+']]
            index2 = pd.MultiIndex.from_product(iterables2)
            self.ResultsH0T0=pd.DataFrame(np.nan,index=index2,columns=['Bouwer-Rice, fully penetrating','Bouwer-Rice, partially penetrating','Hvorslev, fully pnetrating', 'Hvorslev, partially penetrating'])
            self.PlotRegResults()
            if V1.get()== True:    # if this button is clicked, the calculations are done for the specific method (Bouwer-Rice/Hvorslev) and range (best range, all data, begin of the data)
                self.LinearRegression(self.DFSlicedLogNormHead_RangeBR)
                self.LinearReg_Coeff.append(self.LinRegCoef[:])
                self.ResultsH0T0.iloc[0,0]=self.H01
                self.ResultsH0T0.iloc[1,0]=self.T01
                self.KhBouwerRice_FP()
                self.ResultsK.iloc[0,0]=self.Kh_BR_FP_cms
                self.ResultsK.iloc[1,0]=self.Kh_BR_FP_md
                self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='g')
                LegendList.append('Bouwer-Rice - range 0.20-0.30')
            if V4.get()==True:
                self.AqThick=float(AQTHICK.get())*1000
                self.LinearRegression(self.DFSlicedLogNormHead_RangeBR)
                self.ResultsH0T0.iloc[0,1]=self.H01
                self.ResultsH0T0.iloc[1,1]=self.T01
                self.KhBouwerRice_PP()
                self.ResultsK.iloc[0,1]=round(self.Kh_BR_PP_cms, 5)
                self.ResultsK.iloc[1,1]=round(self.Kh_BR_PP_md,5)
                if V1.get()== False:
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='g')
                    LegendList.append('Bouwer-Rice - range 0.20-0.30')
                    
            if V7.get()==True:
                self.AqThick=float(AQTHICK.get())*1000
                self.re=float(RE.get())*10
                self.LinearRegression(self.DFSlicedLogNormHead_RangeH)
                self.LinearReg_Coeff.append(self.LinRegCoef[:])
                self.ResultsH0T0.iloc[0,2]=self.H01
                self.ResultsH0T0.iloc[1,2]=self.T01
                self.KhHvorslev_FP()
                self.ResultsK.iloc[0,2]=self.Kh_H_FP_cms
                self.ResultsK.iloc[1,2]=self.Kh_H_FP_md
                self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='b')
                LegendList.append('Hvorslev - range 0.15-0.25')
            if V10.get()==True:
                self.LinearRegression(self.DFSlicedLogNormHead_RangeH)
                self.LinearReg_Coeff.append(self.LinRegCoef[:])
                self.ResultsH0T0.iloc[0,3]=self.H01
                self.ResultsH0T0.iloc[1,3]=self.T01
                self.KhHvorslev_PP()
                self.ResultsK.iloc[0,3]=self.Kh_H_PP_cms
                self.ResultsK.iloc[1,3]=self.Kh_H_PP_md
                if V7.get()== False:
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='b')
                    LegendList.append('Hvorslev - range 0.15-0.25')
                
                    
            if V2.get()==True:
                self.LinearRegression(self.DFSlicedLogNormHead_Begin)
                self.LinearReg_Coeff.append(self.LinRegCoef[:])
                self.ResultsH0T0.iloc[2,0]=self.H01
                self.ResultsH0T0.iloc[3,0]=self.T01
                self.KhBouwerRice_FP()
                self.ResultsK.iloc[2,0]=self.Kh_BR_FP_cms
                self.ResultsK.iloc[3,0]=self.Kh_BR_FP_md  
                self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='y')
                LegendList.append('Range 0.3-1')
            if V5.get()==True:
                self.AqThick=float(AQTHICK.get())*1000
                self.LinearRegression(self.DFSlicedLogNormHead_Begin)
                self.ResultsH0T0.iloc[2,1]=self.H01
                self.ResultsH0T0.iloc[3,1]=self.T01
                self.KhBouwerRice_PP()
                self.ResultsK.iloc[2,1]=self.Kh_BR_PP_cms
                self.ResultsK.iloc[3,1]=self.Kh_BR_PP_md
                if V2.get()== False:
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='y')
                    LegendList.append('Range 0.30-1')
            if V8.get()==True:
                self.AqThick=float(AQTHICK.get())*1000
                self.re=float(RE.get())*10
                self.LinearRegression(self.DFSlicedLogNormHead_Begin)
                self.ResultsH0T0.iloc[2,2]=self.H01
                self.ResultsH0T0.iloc[3,2]=self.T01
                self.KhHvorslev_FP()
                self.ResultsK.iloc[2,2]=self.Kh_H_FP_cms
                self.ResultsK.iloc[3,2]=self.Kh_H_FP_md
                if (V2.get()== False) & (V5.get()== False):
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='y')
                    LegendList.append('Range 0.3-1')
            if V11.get()==True:
                self.LinearRegression(self.DFSlicedLogNormHead_Begin)
                self.ResultsH0T0.iloc[2,3]=self.H01
                self.ResultsH0T0.iloc[3,3]=self.T01
                self.KhHvorslev_PP()
                self.ResultsK.iloc[2,3]=self.Kh_H_PP_cms
                self.ResultsK.iloc[3,3]=self.Kh_H_PP_md
                if (V2.get()== False) & (V8.get()== False)& (V5.get()== False):
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='y')
                    LegendList.append('Range 0.3-1') 
                    
            if V3.get()==True:
                self.LinearRegression(self.DFSlicedLogNormHead_All)
                self.LinearReg_Coeff.append(self.LinRegCoef[:])
                self.ResultsH0T0.iloc[4,0]=self.H01
                self.ResultsH0T0.iloc[5,0]=self.T01
                self.KhBouwerRice_FP()
                self.ResultsK.iloc[4,0]=self.Kh_BR_FP_cms
                self.ResultsK.iloc[5,0]=self.Kh_BR_FP_md
                self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='m')
                LegendList.append('All data')
            if V6.get()==True:
                self.AqThick=float(AQTHICK.get())*1000
                self.LinearRegression(self.DFSlicedLogNormHead_All)
                self.ResultsH0T0.iloc[4,1]=self.H01
                self.ResultsH0T0.iloc[5,1]=self.T01
                self.KhBouwerRice_PP()
                self.ResultsK.iloc[4,1]=self.Kh_BR_PP_cms
                self.ResultsK.iloc[5,1]=self.Kh_BR_PP_md
                if V3.get()== False:
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='m')
                    LegendList.append('All data')
            if V9.get()==True:
                self.AqThick=float(AQTHICK.get())*1000
                self.re=float(RE.get())*10
                self.LinearRegression(self.DFSlicedLogNormHead_All)
                self.ResultsH0T0.iloc[4,2]=self.H01
                self.ResultsH0T0.iloc[5,2]=self.T01
                self.KhHvorslev_FP()
                self.ResultsK.iloc[4,2]=self.Kh_H_FP_cms
                self.ResultsK.iloc[5,2]=self.Kh_H_FP_md
                if (V3.get()== False) & (V6.get()== False):
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='m')
                    LegendList.append('All data')
            if V12.get()==True:
                self.LinearRegression(self.DFSlicedLogNormHead_All)
                self.ResultsH0T0.iloc[4,3]=self.H01
                self.ResultsH0T0.iloc[5,3]=self.T01
                self.KhHvorslev_PP()
                self.ResultsK.iloc[4,3]=self.Kh_H_PP_cms
                self.ResultsK.iloc[5,3]=self.Kh_H_PP_md
                if (V3.get()== False) & (V6.get()== False)& (V9.get()== False):
                    self.dfFit.plot(x=self.ListNamesCols[0], y=self.ListNamesCols[1],ax=self.ax3, logy=True, linestyle='dashed', color='m')
                    LegendList.append('All data')
            plt.axis([self.DFSlicedNormHead_All.iloc[0,0],self.DFSlicedNormHead_All.iloc[-1,0],self.DFSlicedNormHead_All.iloc[-1,1],self.DFSlicedNormHead_All.iloc[0,1]])
            plt.legend(LegendList, fontsize=11)
            self.ResultsK=self.ResultsK.fillna(" \ ") # instead of nan, '\' will be displayed in the results table for the non-calculated values
            self.TableResults()
        except ValueError:
            tk.messagebox.showerror("Warning", "The calculations cannot be performed! \nCheck if all needed parameters are given and in the correct (float) format")
                        
        
    
    # save the hydraulic conductivity, H0 and T0 results in a text file and the regression figure as pdf
    def SaveResults(self):
        # making a text file with the results
        filenameResult=tk.filedialog.asksaveasfilename(title= 'Save as', confirmoverwrite=True, initialdir=self.newDirectory)
        logText=[]
        logText='\n'.join(['____________________________________________________________\n', '          Logfile Slug Test Analysis Script' , '____________________________________________________________', ' ', ' '.join(['Time:',time.strftime("%a, %d %b %Y %H:%M:%S ")]), 'Working directory: '+ os.getcwd()+'\n', 'Filename: '+self.filename+'\n'])
        logText = logText + '\nMinimal head: '+' H = ' + '%.2f'%self.MinHead + ' mm\n'
        logText = logText + 'Equilibrium Head: '+ '%.2f'%self.BaseLevel + ' mm' + '\n' + 'Initial Displacement H0: '+ '%.2f'%self.H0 + ' mm\n\n' 
        # write the parameters
        logText= logText + '____________________________________________________________\n\n' +'         SLUG TEST CHARACTERISTICS\n'+'____________________________________________________________\n\n'+ 'Rc: '+'%.5f' % (self.rc/10)+' cm \n'+'Rw: '+'%.5f' % (self.rw/10)+' cm \n' + 'd: '+ '%.5f'%(self.d/10) + ' cm \n'+ 'Le: '+ '%.5f' %(self.Le/10)+ ' cm \n\n'
        logText= logText +'____________________________________________________________\n\n' + '          AQUIFER CHARACTERISTICS\n'+'____________________________________________________________\n\n' + 'Aquifer thickness: '+'%.5f' % (self.AqThick/1000) + 'm\n' + 'Anisotropy ratio Kh/Kv: ' + '%.5f'%(self.Aniso) +' [-] \n\n'
        #write the results for Bouwer & Rice
        if (V1.get()== True) or (V2.get()== True) or (V3.get()== True):    
            logText = logText + '____________________________________________________________\n\n' +'      BOUWER & RICE - fully penetrating \n'+'____________________________________________________________\n\n' 
        if V1.get()== True:
            logText = logText + 'a) Calculation based on normalized head data in interval 0.20-0.30:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[0,0]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[1,0]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[0,0] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[1,0] + ' m/d\n\n'
        if V2.get()== True:
            logText = logText + 'b) Calculation based on normalized head data in interval 0.3-1:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[2,0]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[3,0]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[2,0] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[3,0] + ' m/d\n\n\n'
        if V3.get()==True:
            logText = logText + 'c) Calculation based on all head data:\n\n' + 'H0 = '+ '%.2f'%(self.ResultsH0T0.iloc[4,0]/10) + ' cm\n' + 'T0 = ' + '%.1f'%(self.ResultsH0T0.iloc[5,0]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[4,0] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[5,0] + ' m/d\n\n'
            
        if (V4.get()== True) or (V5.get()== True) or (V6.get()== True):    
            logText = logText +'____________________________________________________________\n\n' + '    BOUWER & RICE - partially penetrating \n'+'____________________________________________________________\n\n' 
        if V4.get()== True:
            logText = logText + 'a) Calculation based on normalized head data in interval 0.20-0.30:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[0,1]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[1,1]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[0,1] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[1,1] + ' m/d\n\n'
        if V5.get()== True:
            logText = logText + 'b) Calculation based on normalized head data in interval 0.3-1:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[2,1]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[3,1]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[2,1] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[3,1] + ' m/d\n\n\n'
        if V6.get()==True:
            logText = logText + 'c) Calculation based on all head data:\n\n' + 'H0 = '+ '%.2f'%(self.ResultsH0T0.iloc[4,1]/10) + ' cm\n' + 'T0 = ' + '%.1f'%(self.ResultsH0T0.iloc[5,1]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[4,1] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[5,1] + ' m/d\n\n'
        
        if (V10.get()== True) or (V11.get()== True) or (V12.get()== True):# see above
            logText = logText +'____________________________________________________________\n\n' + 'HVORSLEV - Fully penetrating \n'+'____________________________________________________________\n\n' 
        if V10.get()== True:
            logText = logText + 'a) Calculation based on normalized head data in interval 0.15-0.25:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[0,3]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[1,3]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[0,3] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[1,3] + ' m/d\n\n'
        if V11.get()== True:
            logText = logText + 'b) Calculation based on normalized head data in interval 0.3-1:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[2,3]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[3,3]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[2,3] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[3,3] + ' m/d\n\n\n'
        if V12.get()==True:
            logText = logText + 'c) Calculation based on all head data:\n\n' + 'H0 = '+ '%.2f'%(self.ResultsH0T0.iloc[4,3]/10) + ' cm\n' + 'T0 = ' + '%.1f'%(self.ResultsH0T0.iloc[5,3]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[4,3] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[5,3] + ' m/d\n\n'
       
        # write the results for hvorslev-partially penetrating
        if (V7.get()== True) or (V8.get()== True) or (V9.get()== True):# see above
            logText = logText +'____________________________________________________________\n\n' + '  HVORSLEV - Partially penetrating\n'+'____________________________________________________________\n\n' 
        if V7.get()== True:
            logText = logText + 'a) Calculation based on normalized head data in interval 0.15-0.25:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[0,2]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[1,2]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[0,2] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[1,2] + ' m/d\n\n'
        if V8.get()== True:
            logText = logText + 'b) Calculation based on normalized head data in interval 0.3-1:\n\n' + 'H0+ = '+ '%.2f'%(self.ResultsH0T0.iloc[2,2]/10) + ' cm\n' + 'T0+ = ' + '%.1f'%(self.ResultsH0T0.iloc[3,2]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[2,2] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[3,2] + ' m/d\n\n\n'
        if V9.get()==True:
            logText = logText + 'c) Calculation based on all head data:\n\n' + 'H0 = '+ '%.2f'%(self.ResultsH0T0.iloc[4,2]/10) + ' cm\n' + 'T0 = ' + '%.1f'%(self.ResultsH0T0.iloc[5,2]/10) + ' s\n\n' + 'Kh = ' + '%.5f'%self.ResultsK.iloc[4,2] + ' cm/s' + ' or ' + '%.3f'%self.ResultsK.iloc[5,2] + ' m/d\n\n'
        
        with open(filenameResult, 'w') as output:    
            output.write(logText)
        
        # saving a pdf with the regression plots 
        self.PlotRegRes.savefig(filenameResult + '_RegressionPlot' + '.pdf', bbox_inches='tight')
    
############################################################################### 
###################################### MAIN ###################################
###############################################################################
    
################ creating GUI, structure, title and refer to authors ##########
GUI = tk.Tk()
GUI.title('RSAT 0.2.1')
GUI.geometry('1000x650')
i=8
j=15 
tk.Label(GUI, text='RSAT 0.2.1 - Rising head Slug-test Analysis Tool',font=("Helvetica", "18"), height='3').grid(row=i-8, column=j, columnspan=5)
tk.Label(GUI, text='Working directory and data file',font=("Helvetica", "14")).grid(row=i-7, column=j, columnspan=2, sticky='W')
tk.Label(GUI, text='Authors: Annabel Vaessens, Gert Ghysels and Ferdinand Guggeis \n License: MIT',font=("Helvetica", "8")).grid(row=i+16, column=j+3, columnspan=10, sticky='W')
tk.Label(GUI, text=' ', width=10).grid(row=i, column=j+2)
tk.Label(GUI, text=' ', width=10).grid(row=i, column=j-1,)
tk.Label(GUI, text=' ', height=1).grid(row=i+4, column=j, columnspan=7)
tk.Label(GUI, text=' ', height=1).grid(row=i-1, column=j, columnspan=7)
tk.Label(GUI, text=' ', height=1).grid(row=i+12, column=j-1)
tk.Label(GUI, text=' ', height=2).grid(row=i+15, column=j+3, columnspan=7)
tk.Label(GUI, text='', width=13).grid(row=i-1, column=4+j) # set width of column 4+j to 13

p=Program() # to make the class Program work in the main

########################## DIRECTORY AND OPEN FILE ############################
# button to change directory
tk.Label(GUI, text='Working directory',font=("Helvetica", "11")).grid(row=i-6, column=j, sticky='W')
tk.Button(GUI, text="Browse", command=p.newDirectory, font=("Helvetica", "9"), bg='grey80').grid(row=i-6, column=j+1, sticky='W')

# label and button to import a file 
tk.Label(GUI, text='Data file name',font=("Helvetica", "11")).grid(row=i-4, column=j, sticky='W')
tk.Button(GUI, text="Browse", font=("Helvetica", "9"), command=p.OpenFile, bg='grey80').grid(row=i-4, column=j+1, sticky='W')

# button to plot a head (mm) - time (s) curve in a pop-up window
tk.Button(GUI,text="Show data plot", command=p.PlotDataSeperateBox, font=("Helvetica", "9"), width=26, bg='grey80').grid(row=i-2, column=j, sticky='W')

########################### SPLITTING RAW DATA ################################
# an entry to enter how many measurements there are in the imported file
tk.Label(GUI, text='Splitting raw data',font=("Helvetica", "14")).grid(row=i, column=j, columnspan=2, sticky='W')
tk.Label(GUI, text='Number of measurements in file: ',font=("Helvetica", "9")).grid(row=i+1, column=j, sticky='W')
NM=tk.IntVar()
NumberMeas=tk.Entry(GUI,textvariable=NM, width=8).grid(row=i+1, column=j+1, sticky='W')

# button to define the boundaries of individual measurements in the clickable graph
tk.Button(GUI, text='Define boundaries', command=p.ClickableGraph, font=("Helvetica", "9"), width=26, bg='grey80').grid(row=i+2, column=j, sticky='W')
# button to plit the data files into individual measurements
tk.Button(GUI, text='Split data',command=p.SplitRawData, font=("Helvetica", "9"), width=26, bg='grey80').grid(row=i+3, column=j, sticky='W')

########################### CHECK REPEATABILITY ###############################
# label and button to open multiple files in order to check repeatability on normalized head - time curves
tk.Label(GUI,text='Plot normalized head curves', font=("Helvetica", "14")).grid(row=i+6, column=j,columnspan=2, sticky='W')        
tk.Button(GUI, text='Choose files', command=p.RepeatabilityOpen, font=("Helvetica", "9"), width=26, bg='grey80').grid(row=i+7, column=j, sticky='W')

# button to plot normhead-time curves 
tk.Button(GUI, text='Normalized head vs time', command= p.PlotNormHead_Time ,font=("Helvetica", "9"), width=26, bg='grey80').grid(row=i+8, column=j, sticky='W')

# button to plot normhead-log(time) curves     
tk.Button(GUI, text='Normalized head vs log(time)', command= p.PlotNormHead_LogTime ,font=("Helvetica", "9"), width=26, bg='grey80').grid(row=i+9, column=j, sticky='W')

###################### PARAMETERS for calculations #############################
# aquifer characteristics entries
tk.Label(GUI, text='Aquifer characteristics',font=("Helvetica", "14")).grid(row=i, column=3+j,columnspan=3, sticky='W')

tk.Label(GUI, text='Anisotropy Kh/Kv',font=("Helvetica", "10")).grid(row=i+1, column=3+j, sticky='W')
tk.Label(GUI, text='[-]',font=("Helvetica", "10")).grid(row=i+1, column=5+j, sticky='W')
ANISO=tk.StringVar()
tk.Entry(GUI, textvariable=ANISO, width=8).grid(row=i+1, column=4+j)

tk.Label(GUI, text='Thickness of aquifer',font=("Helvetica", "10")).grid(row=i+2, column= 3+j, sticky='W')
tk.Label(GUI, text='[m]',font=("Helvetica", "10")).grid(row=i+2, column=5+j, sticky='W')
AQTHICK=tk.StringVar()
tk.Entry(GUI, textvariable=AQTHICK, width=8).grid(row=i+2, column=4+j)

# slug test characteristics entries
tk.Label(GUI, text='Slug test characteristics',font=("Helvetica", "14")).grid(row=i-7, column=j+3,columnspan=3, sticky='W')

tk.Label(GUI, text='rc - Effective radius well casing',font=("Helvetica", "10")).grid(row=i-6, column=3+j, sticky='W')
tk.Label(GUI, text='[cm]',font=("Helvetica", "10")).grid(row=i-6, column=5+j, sticky='W')
RC=tk.StringVar()
tk.Entry(GUI, textvariable=RC, width=8).grid(row=i-6, column=j+4)

tk.Label(GUI, text='Le - Effective screen length',font=("Helvetica", "10")).grid(row=i-5, column=3+j, sticky='W')
tk.Label(GUI, text='[cm]',font=("Helvetica", "10")).grid(row=i-5, column=5+j, sticky='W')
LE=tk.StringVar()
tk.Entry(GUI, textvariable=LE, width=8).grid(row=i-5, column=j+4)

tk.Label(GUI, text='rw - Effective radius well screen',font=("Helvetica", "10")).grid(row=i-4, column=3+j, sticky='W')
tk.Label(GUI, text='[cm]',font=("Helvetica", "10")).grid(row=i-4, column=5+j, sticky='W')
RW=tk.StringVar()
tk.Entry(GUI, textvariable=RW, width=8).grid(row=i-4, column=4+j)

tk.Label(GUI, text='d - z-position of top of screen',font=("Helvetica", "10")).grid(row=i-3, column=3+j, sticky='W')
tk.Label(GUI, text='[cm]',font=("Helvetica", "10")).grid(row=i-3, column=5+j, sticky='W')
D=tk.StringVar()
tk.Entry(GUI, textvariable=D, width=8).grid(row=i-3, column=4+j)

tk.Label(GUI, text='Re - effective radius parameter',font=("Helvetica", "10")).grid(row=i-2, column=3+j, sticky='W')
tk.Label(GUI, text='[cm]',font=("Helvetica", "10")).grid(row=i-2, column=5+j, sticky='W')
RE=tk.StringVar()
tk.Entry(GUI, textvariable=RE, width=8).grid(row=i-2, column=4+j)

################# CALCULATION OPTIONS + CALCULATIONS ###########################
# 9 check boxes for the different calculation options 
tk.Label(GUI, text='Calculation methods',font=("Helvetica", "14")).grid(row=6+i, column=j+3, columnspan=1, sticky='W')
tk.Button(GUI, text='Check limitations', command=p.CheckLimitations, font=("Helvetica", "10"), width=15, bg='grey80').grid(row=6+i, column=4+j, sticky='W', columnspan=3)

tk.Label(GUI, text='Bouwer & Rice, fully penetrating',font=("Helvetica", "10")).grid(row=7+i, column=3+j, sticky='W')
tk.Label(GUI, text='Best range',font=("Helvetica", "10")).grid(row=7+i, column=4+j, sticky='E')   
V1=tk.IntVar()
tk.Checkbutton(GUI, variable=V1).grid(row=7+i, column=4+j, sticky='W')
tk.Label(GUI, text='No full recovery',font=("Helvetica", "10")).grid(row=7+i, column=6+j, sticky='W')  
V2=tk.IntVar() 
tk.Checkbutton(GUI, variable=V2).grid(row=7+i, column=5+j, sticky='E')
tk.Label(GUI, text='All data',font=("Helvetica", "10")).grid(row=7+i, column=9+j, sticky='W')   
V3=tk.IntVar()
tk.Checkbutton(GUI, variable=V3).grid(row=7+i, column=8+j, sticky='E')

tk.Label(GUI, text='Bouwer & Rice, partially penetrating',font=("Helvetica", "10")).grid(row=8+i, column=3+j, sticky='W')
tk.Label(GUI, text='Best range',font=("Helvetica", "10")).grid(row=8+i, column=4+j, sticky='E')  
V4=tk.IntVar() 
tk.Checkbutton(GUI, variable=V4).grid(row=8+i, column=4+j, sticky='W')
tk.Label(GUI, text='No full recovery',font=("Helvetica", "10")).grid(row=8+i, column=6+j, sticky='W')  
V5=tk.IntVar()  
tk.Checkbutton(GUI, variable=V5).grid(row=8+i, column=5+j, sticky='E')
tk.Label(GUI, text='All data',font=("Helvetica", "10")).grid(row=8+i, column=9+j, sticky='W')   
V6=tk.IntVar() 
tk.Checkbutton(GUI, variable=V6).grid(row=8+i, column=8+j, sticky='E')

tk.Label(GUI, text='Hvorslev, fully penetrating',font=("Helvetica", "10")).grid(row=9+i, column=3+j, sticky='W')
tk.Label(GUI, text='Best range',font=("Helvetica", "10")).grid(row=9+i, column=4+j, sticky='E')  
V7=tk.IntVar()
tk.Checkbutton(GUI, variable=V7).grid(row=9+i, column=4+j, sticky='W')
tk.Label(GUI, text='No full recovery',font=("Helvetica", "10")).grid(row=9+i, column=6+j, sticky='W')   
V8=tk.IntVar()
tk.Checkbutton(GUI, variable=V8).grid(row=9+i, column=5+j, sticky='E')
tk.Label(GUI, text='All data',font=("Helvetica", "10")).grid(row=9+i, column=9+j, sticky='W') 
V9=tk.IntVar()  
tk.Checkbutton(GUI, variable=V9).grid(row=9+i, column=8+j, sticky='E')

tk.Label(GUI, text='Hvorslev, partially penetrating',font=("Helvetica", "10")).grid(row=10+i, column=3+j, sticky='W')
tk.Label(GUI, text='Best range',font=("Helvetica", "10")).grid(row=10+i, column=4+j, sticky='E')  
V10=tk.IntVar()
tk.Checkbutton(GUI, variable=V10).grid(row=10+i, column=4+j, sticky='W')
tk.Label(GUI, text='No full recovery',font=("Helvetica", "10")).grid(row=10+i, column=6+j, sticky='W')   
V11=tk.IntVar()
tk.Checkbutton(GUI, variable=V11).grid(row=10+i, column=5+j, sticky='E')
tk.Label(GUI, text='All data',font=("Helvetica", "10")).grid(row=10+i, column=9+j, sticky='W') 
V12=tk.IntVar()  
tk.Checkbutton(GUI, variable=V12).grid(row=10+i, column=8+j, sticky='E')
# button to perform calculations
tk.Button(GUI, text='Calculate Kh values', command=p.PerformCalc, font=("Helvetica", "10"), width=20, bg='grey80').grid(row=13+i, column=3+j, sticky='W', columnspan=1)
# button to save the results    
tk.Button(GUI, text='Save results', command=p.SaveResults, font=("Helvetica", "10"), width=20, bg='grey80').grid(row=13+i, column=3+j, sticky='E', columnspan=3)
# button to close the GUI
tk.Button(GUI, text="Close tab", command=GUI.destroy, font=("Helvetica", "10"), width=20, bg='grey80').grid(row=i+13, column=j+6, columnspan=4)

tk.mainloop( ) # keeps the GUI open



