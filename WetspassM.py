
print    """ A libray for the calculation of
     hydrological processes from meteorological data at monthly timestep.
     
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

     Functions:
        - Interception: Calculates Interception from vegetated areas using fixed percentage method
        - Runoff: Calculates runoff for vegetated, bare, impervious and water areas using new Runoff Coefficient Method
        - Evapotranspiration: Calculates evapotranspiration using Penmen Monteith Equation
        - Recharge: Calculates recharge to the soil layer assigning remaining input to the grid
        
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
'__Authors__       Khodayar Abdollahi   <kabdolla@vub.ac.be>,
                   Imtiaz Bashir        <imtiaz.bashir@vub.ac.be> 
                   Okke Batelaan        <batelaan@vub.ac.be>
'__Version__ = 'M'
'__date__ = '19 July 2015'
(c) 2012 Users are encouraged to discuss their research results, experiences, problems with the Authors.
Dept. of Hydrology and Hydraulic Engineering, Vrije Universiteit Brussel
#An indexing bug fixed
+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
"""
#Note: Interception is included in AET
import clr
import sys
from h2pl import *
clr.AddReference('System')
clr.AddReference('System.Windows.Forms')
clr.AddReference('System.Drawing')
from System.Windows.Forms import *
from System.Drawing import *
from System import *
from h2pl.macro import *
from System import DateTime
from System.Diagnostics  import *



#if you remove H2PL (Khodayar's library)  you'll loose most hydrologic functionalitys
#this line can help for error handling:
# <MessageBox.Show(varaiblename)>

#let start

print "Loading WetSpass ..."
print "Monthly version of WetSpass: spatially fully distributed water balance model"
print DateTime.Now



class WetSpassMainPage():
    def __init__(self):
        pass
    class Model(Form):
#       | <=required indentation
        global qt_1
        global qbt_1
        def Dispose(self, disposing):
           if disposing:
            if self.MYcomponents != None:
               self.MYcomponents.Dispose()
               #self.Dispose(disposing)         
        def __init__(self):
          self.MYcomponents = None
          self.loadpage()          
          self.Show()
          
# +++++++++++++++++++++++++++++++++++++++++++++++++ Pre-processing ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        def radioLaiFromInputsCheckedChanged(self, sender, e):
           if self.radioLaiFromInputs.Checked == True and self.checkLAIFroDir.Checked == False:
              self.textLAIdir.Enabled=True
              self.butLAI.Enabled=True
              self.labLAI.Enabled=True
              self.checkLAIFroDir.Enabled=True
              
           elif self.radioLaiFromInputs.Checked == True :
              #self.checkLAIFroDir.Checked = True 
              self.checkLAIFroDir.Enabled=True
        
        def CheckBaseFlowChanged(self, sender, e):
           if self.checkSurfinteract.Checked:
               self.Interactgroup.Enabled = True
               self.qbaseGroup.Enabled = True
           else:
               self.Interactgroup.Enabled = False
               self.qbaseGroup.Enabled = False

        def radioLaiFromLanduseCheckedChanged(self, sender, e):
           if self.radioLaiFromLanduse.Checked == True:
               self.checkLAIFroDir.Enabled=False
               self.textLAIdir.Enabled=False
               self.butLAI.Enabled=False
               self.labLAI.Enabled=False
               
           else:
               self.textLAIdir.Enabled=True
               self.butLAI.Enabled=True
               self.labLAI.Enabled=True               
               self.checkLAIFroDir.Checked = False
  
               
               
        def ClickLAIfromDir(self, sender, e):
             if self.checkLAIFroDir.Checked == True:
                 self.textLAIdir.Enabled=False
                 self.butLAI.Enabled=False
                 self.labLAI.Enabled=False
                 
             else:
                self.textLAIdir.Enabled=True
                self.butLAI.Enabled=True
                self.labLAI.Enabled=True
                

        def LinkSaveLinkClicked(self, sender, e):
            self.sheettable1.SaveAsTBL(self.curenttable)
            print "Changes has been saved \n: "+self.curenttable

        def LinkOpenLinkClicked(self, sender, e):
            self.curenttable=self.sheettable1.OpenTBL();
            if len(self.curenttable)>1:
                print "Table is open:" +self.curenttable
                self.linkSave.Enabled =True

        def buteDoCalibrClick(self, sender, e):
            if len(self.TboxObseved.Text)>=1:
                 ResultStr=""
                 workingdir(self.Tboxotputdir.Text+"\\")
                 ResultStr=Optimize(self.TboxEstimted.Text,self.TboxObseved.Text,6,"Calibration.txt")
                 self.TboxCoefAintercetion.Text=ResultStr[0]
                 self.TboxAlfaCoef.Text=ResultStr[1]
                 self.TboxwSlop.Text=ResultStr[2]
                 self.TboxwLanduse.Text=ResultStr[3]
                 self.TboxwSoil.Text=ResultStr[4]
                 self.Tbox_as_ET.Text=ResultStr[5]
                 self.Tbox_bs_ET.Text=ResultStr[6]
                 self.XtextBox.Text=ResultStr[7]
                 self.buttonRunClick(sender,e);
                 #
            else:
                  print "Select obervations file and try again"   
                  self.butOservClick(self,e)
                  self.buteDoCalibrClick(self,e)
#This function reads a column data and stores the results as a list
        def ColTableToList(self,tbFilename, colname, delimiter):
             nRows = 0
             fristRow = ""
             nCols = 0
             ColNo = -1
             irows = 0
             result = []
             #
             if str.IsNullOrEmpty(tbFilename):
                 MessageBox.Show("Please specify the  estimated file")
             try:
                 TBfileReader = IO.StreamReader(tbFilename)
                 if TBfileReader.Peek() == -1:
                      MessageBox.Show("'" + tbFilename + "' file is Empty!!")
                      return result
                 else:
                      #Reading Data
                      fristRow = TBfileReader.ReadLine().Trim()
                      Columns = fristRow.Split(delimiter)
                      nCols = Columns.Length								
                 if nCols > 0:
                      i = 0
                      while i < nCols:
                          if Columns[i].Trim() == colname.Trim():
                             ColNo = i
                          i += 1

                 if nCols == 0 or ColNo == -1:
                      MessageBox.Show("Could not find '" + colname + "' column in '" + tbFilename + "' file!")
                      return result
                 while TBfileReader.Peek() != -1:
                     irows += 1				
                     currentRow = TBfileReader.ReadLine().TrimStart().TrimEnd()
                     currentRowarray = currentRow.Split(delimiter)
                     nCols = currentRowarray.Length
                     if nCols > ColNo:
                          result.Add( currentRowarray[ColNo])
                 TBfileReader.Dispose()
                 return result
             except Exception, exceptionObject:
                raise Exception("Error while reading column '" + "' :\n" + exceptionObject.ToString() + exceptionObject.StackTrace)
                 
             finally:
                 TBfileReader.Dispose()                 
        def Preprocess(self):
            try:
                findErroe=False
                StrErroRepor="";
                if  len(self.TboxCoefAintercetion.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "The value of a (Interception) is unknown"
                elif len(self.BaseTemp.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Base temperature could not be empty"                        
                elif len(self.MeltFacttextBox.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Melting parameter could not be empty"                       
                elif len(self.AreatextBox.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Area could not be empty"                           
                elif len(self.BetatextBox.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Beta parameter could not be empty"                         
                elif len(self.XtextBox.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "X parameter could not be empty"                             
                elif len(self.ContribtextBox.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Contribution facotor could not be empty"                                
                elif len(self.LPtextBox.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "LP parameter could not be empty"                        
                elif len(self.IntensitytextBox.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Intensity could not be unknown"                       
                elif len(self.TboxwSlop.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "WSlope factor is unknown"                
                elif len(self.TboxwSoil.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "WSoil factor is unknown"   
                elif len(self.TboxAlfaCoef.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" +"Alfa factor is unknown"  
                elif len(self.TboxwLanduse.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "wLanduse factor is unknown" 
  
                elif len(self.TxtFirstStepNo.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Starting time step of  is unknown"  
                elif len(self.TxtPeriodicNos.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "No. of time steps per period  is unknown"                                   
                elif len(self.TboxdemDir.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box for Dem file is empty"                   
                elif len(self.Tboxendtimestep.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box of end time step is empty"                     
                 
                elif len(self.TboxLandusfile.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box for landuse file is empty"                    
                elif len(self.Tboxnodata.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box for nodata values is empty"                     
                elif len(self.Tboxnooftimsteps.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box for number of time steps is empty"                    
                elif len(self.Tboxotputdir.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Output directory is empty"                    
                elif len(self.TboxSlopemapDir.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box for SLOPE file is empty"                   
                elif len(self.TboxsoilmapDir.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box for SOIL map file is empty"                     
                elif len(self.Tboxstarttimestep.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Text box for startig time step is empty"
                elif self.checkSimulations.CheckState == CheckState.Checked and len(self.TxtSimulations.Text)<1:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "File name of the simulations is empty"                
                elif len(self.Tboxworkingdir.Text)<1:
                    findErroe=True
                    self.TxtSimulations.Text
                    StrErroRepor=StrErroRepor+"\n" + "Working directory is empty"
                if self.radioLaiFromInputs.Checked == True and self.checkLAIFroDir.Checked == True:
                    if IO.Directory.Exists(self.Tboxworkingdir.Text+"\\inputs\\maps\\LAI\\")==False:
                         findErroe=True
                         StrErroRepor=StrErroRepor+"\n" + "LAI directory does not exist"
                if self.radioLaiFromInputs.Checked == True and self.checkLAIFroDir.Checked == False:
                    if len(self.textLAIdir.Text)<1:
                         findErroe=True
                         StrErroRepor=StrErroRepor+"\n" + "LAI map has been left empty"
                #Check existance of inputs
                if(IO.File.Exists( self.Tboxworkingdir.Text+ "\\inputs\\tables\\RainyDaysPerMonth.TBL")==False):
                        findErroe=True
                        StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\tables\\RainyDaysPerMonth.TBL"+ "' file does not exist"
 
                if IO.Directory.Exists(self.Tboxworkingdir.Text)==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Working directory does not exist"               
                elif IO.Directory.Exists(self.Tboxotputdir.Text)==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "Outputs directory does not exist"
                elif IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + self.Tboxworkingdir.Text+"\\inputs\\" " does not exist!"              
                elif IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + self.Tboxworkingdir.Text+"\\inputs\\maps\\" " does not exist!"
                elif IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\tables\\")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + self.Tboxworkingdir.Text+"\\inputs\\tables\\" " does not exist!"                   
                if self.checFracFromDir.Checked == True and IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\Fractions\\")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n" + "'Fractions' directory does not exist"                     
                if IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\gwdepth")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\gwdepth"+ "' directory does not exist"                    
                if IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\pet")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\pet"+ "' directory does not exist"
                if IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\wind")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\wind"+ "' directory does not exist"                    
                if IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\temp")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\temp"+ "' directory does not exist"                               
                if IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\rain")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\rain"+ "' directory does not exist"             
                
                if self.checAddIrrig.Checked == True and IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\irrigation")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\irrigation"+ "' directory does not exist"
                    
                if self.checIncludSnow.Checked and IO.Directory.Exists( self.Tboxworkingdir.Text+"\\inputs\\maps\\snow")==False:
                    findErroe=True
                    StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\snow"+ "' directory does not exist"

                    if(IO.File.Exists( self.Tboxworkingdir.Text+ "\\inputs\\tables\\DegreeDaysPerMonth.TBL")==False):
                        findErroe=True
                        StrErroRepor=StrErroRepor+"\n '" +self.Tboxworkingdir.Text+"\\inputs\\maps\\DegreeDaysPerMonth.TBL"+ "' file does not exist"
               
                if  findErroe==True:
                    print "Note: Could not run the model becuase:"+StrErroRepor
                    self.gotError=True
                    MessageBox.Show("Insufficient Inputs: check notifications!")
                    return False
                else:
                    return True
            except Exception, exceptionObject:                
                  MessageBox.Show(exceptionObject.Message.ToString() +'\n' +'Line ' + str(sys.exc_info()[-1].tb_lineno) + '\n'+ "Model failed to finish")
            finally:
                 pass             

        def buttonRunClick(self, sender, e):
            try: 
                             
                self.qt_1=0
                self.qbt_1=0
                coefficients=[]
                if self.Preprocess() == False:
                    return
                #0
                coefficients.append(self.TboxCoefAintercetion.Text)
                #1
                coefficients.append(self.TboxAlfaCoef.Text)
                #2
                coefficients.append(self.TboxwSlop.Text)
                #3
                coefficients.append(self.TboxwLanduse.Text)
                #4
                coefficients.append(self.TboxwSoil.Text)
                #5
                coefficients.append(self.XtextBox.Text)
                #6
                coefficients.append(self.LPtextBox.Text)
                #7
                   #  Monthly rainfall data are mostly available but often availabliy for measurements of rainfall intensity is limited, 
                   # so the 24/I_av was used as aggrigated indicator (i.e. daily rain/I^2) for the effect of intensity on the runoff coefficient.
                intenscoef=24.0/float(self.IntensitytextBox.Text)
                coefficients.append(str(intenscoef))                              
                #8
                coefficients.append(self.BetatextBox.Text)
                #9
                coefficients.append(self.ContribtextBox.Text)
                #10
                coefficients.append(self.BaseTemp.Text)
                #11
                coefficients.append(self.MeltFacttextBox.Text)
                #12
                coefficients.append(self.Snowdensity.Text)
                
                #coefficients=map(float,caliblist)
                #MessageBox.Show(coefficients[1])
                currenstep=int(self.Tboxstarttimestep.Text)
                finaltimstep=int(self.Tboxendtimestep.Text)
                self.gotError=False
                #curPeriodNo=self.TxtFirstStepNo.Text
            
                if IO.Directory.Exists(self.Tboxotputdir.Text+"\\Lookups")==False:
                           IO.Directory.CreateDirectory(self.Tboxotputdir.Text+"\\Lookups")
                self.CreateTopoGama(0)
                self.Landuselookups(0)            
                self.Soiluselookups(0)
                if self.radioLaiFromInputs.Checked == True and self.checkLAIFroDir.Checked == True:
                    self.LAI =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\LAI\\"+self.TboxPrefixLAI.Text+self.Tboxstarttimestep.Text+".asc","lai")
                    #cal("lai=IF(lai<0,0,lai)")
                NRtable= self.Tboxworkingdir.Text+ "\\inputs\\tables\\RainyDaysPerMonth.TBL"
                DegDtable= self.Tboxworkingdir.Text+ "\\inputs\\tables\\DegreeDaysPerMonth.TBL"
                RainyDays=self.ColTableToList(NRtable, "RainyDays", "\t")                
                simsnow=False
                nLoop=0
                if self.checIncludSnow.Checked:
                    simsnow=True
                    DegreeDays=self.ColTableToList(DegDtable, "DegreeDays", "\t")
                while currenstep < finaltimstep+1 and self.gotError==False:
                    nLoop=nLoop+1
                    self.gotError=False
                    reseth2pl()
                    print "Calculation in progress for time step "+str(currenstep)+"."
                    #print "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX" 
                    self.CreateTopoGama(currenstep)
                    self.LoadData(currenstep)
                    self.Landuselookups(currenstep)
                    self.Soiluselookups(currenstep)
                    if self.checIncludSnow.Checked:                      
                        self.Snowmelt(currenstep,nLoop,DegreeDays,coefficients)

                    self.soilwater_storage=cal("soilwater_storage"+str(currenstep-1)+"=0")
                    self.soilwater_storage=cal("soilwater_storage"+str(currenstep)+"=0")
                    self.ET_factor(currenstep,coefficients)
                    self.Interception(currenstep,RainyDays,coefficients)
                    self.Surfacerunoff(currenstep,RainyDays,coefficients)                
                    self.ET(currenstep,coefficients)                
                    self.Recharge(currenstep)                    
                    if self.checkSimulations.Checked:
                        self.Sumup(currenstep,nLoop,coefficients)                
                    self.CleanUnwantedMaps(currenstep)
                    currenstep=currenstep+1
                self.CleanTempMaps(currenstep)
                print "WetSpass has been run successfully!"
                MessageBox.Show("Model has been run successfully!"+'\n' +"To see the results check  output directory "+'\n' + self.Tboxotputdir.Text)
                Process.Start("H2PL.MapViewer.exe")
            except Exception, exceptionObject:                
                  MessageBox.Show(exceptionObject.Message.ToString() +'\n' +'Line ' + str(sys.exc_info()[-1].tb_lineno) + '\n'+ "Model failed to finish")
            finally:
                 pass 
                
    
# +++++++++++++++++++++++++++++++++++++++++++++++++ Loading Input Maps ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        def  LoadData(self,ii):
          try:                 
                i=str(ii)
                if  self.gotError==False:
                  
                    if self.checAddIrrig.Checked == True:
                        workingdir(self.Tboxotputdir.Text+"\\")
                        self.rainfall =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\rain\\"+self.TboxPrefixrainfall.Text+i+".asc","rainfall"+i)
                        self.rainfall =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\irrigation\\"+self.TboxPrefixIrrigatedArea.Text+i+".asc","irrig"+i)
                        cal("rainfall"+i+"=rainfall"+i+"+irrig"+i)
                    else:
                        self.rainfall =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\rain\\"+self.TboxPrefixrainfall.Text+i+".asc","rainfall"+i)
                    self.pet =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\pet\\"+self.TboxPrefixPET.Text+i+".asc","pet"+i)
                    self.temp =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\temp\\"+self.TboxPrefixTemperature.Text+i+".asc","temp"+i)
                    self.wind =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\wind\\"+self.TboxWind.Text+i+".asc","wind"+i)
                    self.gwdepth =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\gwdepth\\"+self.Tboxgwdepth.Text+i+".asc","gwdepth"+i)
                    if self.checIncludSnow.Checked:                        
                        self.gwdepth =rastermap(self.Tboxworkingdir.Text+"\\outputs\\SnowStore"+str(ii-1)+".asc","SnowStore"+str(ii-1))
                        self.gwdepth =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\snow\\"+self.Tboxsnowcover.Text+i+".asc","snowcover"+i)
                    if self.radioLaiFromInputs.Checked == True and self.checkLAIFroDir.Checked == True:
                        self.LAI =rastermap(self.Tboxworkingdir.Text+"\\inputs\\maps\\LAI\\"+self.TboxPrefixLAI.Text+i+".asc","lai")
                        #cal("lai=IF(lai<0,0,lai)")
                        
                else:
                    #print sys.exc_info()[0]
                    pass   
          except  Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while loading defaults at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )      
                  
        
        def  CreateTopoGama(self,ii): #Create a slope map and classify it:
          try:
                if  self.gotError==False:
                    
                    self.dem=rastermap(self.TboxdemDir.Text,"dem")
                    workingdir(self.Tboxotputdir.Text+"\\Lookups\\")
                    self.gamma=cal("gamma=(0.5988-(0.0000133*dem))^5.23")
                    workingdir(self.Tboxotputdir.Text+"\\")
                    if ii==0:
                        # Claculate slope in percent
                                               
                        if self.checkSlopFromDem.Checked == True:
                            print "calculating slope classes"
                            self.slope=cal("slop=SLOPE(dem)")
                        else:
                            self.slop =rastermap(self.TboxSlopemapDir.Text,"slop")
                        cal("slop=IF(slop>0.3,slop,0.3)")    
                        
                        
                    else:
                        workingdir(self.Tboxotputdir.Text+"\\")                         
                        rastermap(self.TboxSlopemapDir.Text,"slop")
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\gamma.asc","gamma")                    
                        
            
                else:
                    pass
          except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while calculting topo/gamm map at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )
                                

# +++++++++++++++++++++++++++++++++++++++++++++++++ Pre-processing ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 
                   
        def  Landuselookups(self,ii):
          try:
                
                if  self.gotError==False: 
                    ########    Read Landuse and create looup maps  according to the tables
                   
 
                   if ii==0:
                        # print "Landuse look-up started for month No. "+currenPeriod+"!"
                        print "Creaion of landuse look-ups  started"
                        #currenPeriod=str(currenPeriodint)

                        workingdir(self.Tboxotputdir.Text+"\\Lookups\\")
                        
                        self.landuse=rastermap(self.TboxLandusfile.Text,"landuse")
                        #landtable= self.Tboxworkingdir.Text+ "\\inputs\\tables\\landuse_table"+currenPeriod+".TBL"
                        landtable= self.Tboxworkingdir.Text+ "\\inputs\\tables\\Landuses.TBL"
                       
                        if self.checFracFromDir.Checked == True:
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\veg_area.asc","vegarea")
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\bare_area.asc","barearea")
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\imp_area.asc","imp_area") 
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\ow_area.asc","owarea")
                            
                            
                        else:
                            
                            outpath= self.Tboxotputdir.Text+"\\Lookups\\vegarea.asc"
                            self.vegarea=lookupmap("landuse",outpath,landtable, 1, 4,"\t",-9999)

                        
                            outpath= self.Tboxotputdir.Text+"\\Lookups\\barearea.asc"
                            self.barearea=lookupmap("landuse",outpath,landtable, 1, 5,"\t",-9999)
                        
                                               
                            outpath= self.Tboxotputdir.Text+"\\Lookups\\imp_area.asc"
                            self.imp_area=lookupmap("landuse",outpath,landtable, 1, 6,"\t",-9999)
                       
                        
                            outpath= self.Tboxotputdir.Text+"\\Lookups\\owarea.asc"
                            self.owarea=lookupmap("landuse",outpath,landtable, 1, 7,"\t",-9999)

                        #0.001 to avoid divid/0 
                        cal("vegratio=vegarea/(0.01+vegarea+barearea)")
                        cal("bareratio=1-vegratio")
                        outpath= self.Tboxotputdir.Text+"\\Lookups\\rootdepth.asc"
                        self.rootdepth=lookupmap("landuse",outpath,landtable, 1, 8,"\t",-9999)
                        
                       
                        if self.radioLaiFromLanduse.Checked == True:
                            outpath= self.Tboxotputdir.Text+"\\Lookups\\lai.asc"
                            self.Lai=lookupmap("landuse",outpath,landtable, 1, 9,"\t",-9999)                        
                        elif self.radioLaiFromInputs.Checked == True and self.checkLAIFroDir.Checked == False:                            
                            self.LAI =rastermap(self.textLAIdir.Text,"lai")                            
                            #cal("lai=IF(lai<0,0,lai)")
                            
                                                
                        outpath= self.Tboxotputdir.Text+"\\Lookups\\minstomata.asc"
                        self.minstomata=lookupmap("landuse",outpath,landtable, 1, 10,"\t",-9999) 
                                            
                        
                        outpath= self.Tboxotputdir.Text+"\\Lookups\\zveg.asc"
                        self.zveg=lookupmap("landuse",outpath,landtable, 1, 11,"\t",-9999)
                         
                        #n_maning is used directly in landfactor
                        
                        #outpath= self.Tboxotputdir.Text+"\\Lookups\\n_maning"+currenPeriod+".asc"
                        #self.zveg=lookupmap("landuse",outpath,landtable, 1, 12,"\t",-9999)
                        
                        outpath= self.Tboxotputdir.Text+"\\Lookups\\landfactor.asc"
                        self.zveg=lookupmap("landuse",outpath,landtable, 1, 13,"\t",-9999)                        

                        outpath= self.Tboxotputdir.Text+"\\Lookups\\Aeroresit_wind1ms.asc"
                        self.zveg=lookupmap("landuse",outpath,landtable, 1, 14,"\t",-9999)

                        

                        print "All Landuse lookup maps are created!"
                        self.gotError=False
                   else:
                       #for after second loop we just define raster names                                             
                                                                       
                        rastermap(self.TboxLandusfile.Text,"landuse")
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\vegratio.asc","vegratio")
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\bareratio.asc","bareratio")                        
                        if self.checFracFromDir.Checked == True:                        
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\veg_area.asc","vegarea")
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\bare_area.asc","barearea")
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\imp_area.asc","imp_area") 
                            rastermap(self.Tboxworkingdir.Text+"\\inputs\\Fractions\\ow_area.asc","owarea")                       
                        else:
                            rastermap(self.Tboxotputdir.Text+"\\Lookups\\vegarea.asc","vegarea")
                            rastermap(self.Tboxotputdir.Text+"\\Lookups\\barearea.asc","barearea")
                            rastermap(self.Tboxotputdir.Text+"\\Lookups\\imp_area.asc","imp_area")                       
                            rastermap(self.Tboxotputdir.Text+"\\Lookups\\owarea.asc","owarea")
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\rootdepth.asc","rootdepth")
                        if self.radioLaiFromLanduse.Checked == True:
                            rastermap(self.Tboxotputdir.Text+"\\Lookups\\lai.asc","lai")                                                   
                        elif self.radioLaiFromInputs.Checked == True and self.checkLAIFroDir.Checked == False:                            
                            rastermap(self.textLAIdir.Text,"lai")                           
                            #cal("lai=IF(lai<0,0,lai)")
                        
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\minstomata.asc","minstomata")                        
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\zveg.asc","zveg")
                        #rastermap(self.Tboxotputdir.Text+"\\Lookups\\n_maning.asc","n_maning")
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\landfactor.asc","landfactor")
                        rastermap(self.Tboxotputdir.Text+"\\Lookups\\Aeroresit_wind1ms.asc","Aeroresit_wind1ms")
                        
                        self.gotError=False
                        
               
          except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while creating landuse lookups at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )

        def  Soiluselookups(self,ii):
          try:
                if  self.gotError==False:
                    if ii==0: 
                         print "Soil look-up started...!"
                         workingdir(self.Tboxotputdir.Text+"\\Lookups\\")
                         self.soil =rastermap(self.TboxsoilmapDir.Text,"soil")                 
                         soiltable= self.Tboxworkingdir.Text+ "\\inputs\\tables\\Soil.TBL"
                         #Field_Capacity
                         outpath= self.Tboxotputdir.Text+"\\Lookups\\fc.asc"
                         self.fc=lookupmap("soil",outpath,soiltable, 1, 3,"\t",-9999)                        

                         #Wilting_Point  
                         outpath= self.Tboxotputdir.Text+"\\Lookups\\wp.asc"
                         self.wp=lookupmap("soil",outpath,soiltable, 1, 4,"\t",-9999)                        

                         #residual_water_content  
                         outpath= self.Tboxotputdir.Text+"\\Lookups\\residual_water_content.asc"
                         self.residual_water_content=lookupmap("soil",outpath,soiltable, 1, 6,"\t",-9999)                        

                        #a1  
                         outpath= self.Tboxotputdir.Text+"\\Lookups\\a1.asc"
                         self.a1=lookupmap("soil",outpath,soiltable, 1, 7,"\t",-9999)                        


                        #evapo_depth 
                         outpath= self.Tboxotputdir.Text+"\\Lookups\\evapo_depth.asc"
                         self.evapo_depth=lookupmap("soil",outpath,soiltable, 1, 8,"\t",-9999)    
                                        
                        #tension_ht  
                         outpath= self.Tboxotputdir.Text+"\\Lookups\\tension_ht.asc"
                         self.tension_ht=lookupmap("soil",outpath,soiltable, 1, 9,"\t",-9999)   
                       

                        #soilfactor=Tetaw/(1-Tetaw)   
                         outpath= self.Tboxotputdir.Text+"\\Lookups\\soilfactor.asc"
                         self.soilfactor=lookupmap("soil",outpath,soiltable, 1, 12,"\t",-9999)   
                       

                                              
                    else:
                         soil=rastermap(self.TboxsoilmapDir.Text,"soil")
                         rastermap(self.Tboxotputdir.Text+"\\Lookups\\fc.asc","fc")
                         rastermap(self.Tboxotputdir.Text+"\\Lookups\\wp.asc","wp")
                         rastermap(self.Tboxotputdir.Text+"\\Lookups\\residual_water_content.asc","residual_water_content")
                         rastermap(self.Tboxotputdir.Text+"\\Lookups\\a1.asc","a1")
                         rastermap(self.Tboxotputdir.Text+"\\Lookups\\evapo_depth.asc","evapo_depth")
                         rastermap(self.Tboxotputdir.Text+"\\Lookups\\tension_ht.asc","tension_ht") 
                         rastermap(self.Tboxotputdir.Text+"\\Lookups\\soilfactor.asc","soilfactor") 
                         
                                                                                                                              
                else:
                    #print sys.exc_info()[0]+ "ERROR IN Soil LOOKUP!"
                    pass   
          except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while creating soil lookups at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )
                


#This function reads a column data and stores the results as a string list
        def ColTableToList(self,tbFilename, colname, delimiter):
             nRows = 0
             fristRow = ""
             nCols = 0
             ColNo = -1
             irows = 0
             result = []
             #
             if str.IsNullOrEmpty(tbFilename):
                 MessageBox.Show("Please specify the  a tabular file name")
             try:
                 TBfileReader = IO.StreamReader(tbFilename)
                 if TBfileReader.Peek() == -1:
                      MessageBox.Show("'" + tbFilename + "' file is Empty!!")
                      return result
                 else:
                      #Reading Data
                      fristRow = TBfileReader.ReadLine().Trim()
                      Columns = fristRow.Split(delimiter)
                      nCols = Columns.Length								
                 if nCols > 0:
                      i = 0
                      while i < nCols:
                          if Columns[i].Trim() == colname.Trim():
                             ColNo = i
                          i += 1

                 if nCols == 0 or ColNo == -1:
                      MessageBox.Show("Could not find '" + colname + "' column in '" + tbFilename + "' file! Make sure this column exist.")
                      return result
                 while TBfileReader.Peek() != -1:
                     irows += 1				
                     currentRow = TBfileReader.ReadLine().TrimStart().TrimEnd()
                     currentRowarray = currentRow.Split(delimiter)
                     nCols = currentRowarray.Length
                     if nCols > ColNo:
                          result.Add( currentRowarray[ColNo])
                 TBfileReader.Dispose()
                 return result
             except Exception, exceptionObject:
                 MessageBox.Show("Error while reading column '" + "' :\n" + exceptionObject.ToString() + exceptionObject.StackTrace)
             finally:
                 TBfileReader.Dispose()
                               
# +++++++++++++++++++++++++++++++++++++++++++++++++ Hydrological Processes ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        def  RunStep3(): # Step3: Computing surface runoff:
          try:
                if  self.gotError==False: 
                    Checkinputs()
                else:
                    pass
          except :
                self.gotError=True

###################    Calculation of Interception


        def  Interception(self,ii,rainydays,coefficients):
          try:
              i=str(ii)
              
              if  self.gotError==False:
                  print "Calculation of Interception for time step "+str(i)+" started...!"                  
                  workingdir(self.Tboxotputdir.Text+"\\")                  
                  #modified in june 2013 by khodayar Abdollahi
                  # 'a' interction=coefficients[0]
                  self.Interceptiona=cal("aLAI=IF(lai<=0,0.001,("+coefficients[0]+"*lai))")
                  #VA is the denominator in the equation of D 
                  cal("Va"+i+"=rainfall"+i+"*(1-(1/EXP(0.463*lai)))")
                  #A file name for  D                    
                  cal("DIT"+i+"=aLAI-(aLAI/(1+(Va"+i+"/aLAI)))") 
                  #Rain days for current time step  
                  cal("nr="+str(rainydays[ii-1]))               
                  self.total_Interception=cal("total_Interception"+i+"=IF(lai>0,(vegarea*rainfall"+i+"*(1-(EXP(-1*DIT"+i+"*nr/rainfall"+i+")))),0)")
                  self.total_Interception=cal("total_Interception"+i+"=IF(total_Interception"+i+">pet"+i+",pet"+i+",total_Interception"+i+")")
                  # alfa=coefficients[1]
                  # LP=coefficients[6]
                  cal("evap_rate"+i+"=IF(rainfall"+i+">pet"+i+",1,rainfall"+i+"/(((rainfall"+i+"^"+coefficients[1]+")+(pet"+i+"^"+coefficients[1]+"))^(1/"+coefficients[1]+")))")
                  #cal("evap_rate"+i+"=rainfall"+i+"/(((rainfall"+i+"^"+coefficients[1]+")+(pet"+i+"^"+coefficients[1]+"))^(1/"+coefficients[1]+"))")
                  #Groen and Savenije (2006) method gives VegeAET+Interception, the formula  seperates interception portion                                    
                  #The interception  accounts for 10–48% of the gross precipitation in vegeted areas (Ho¨rmannet al., 1996).
                  #Interception Ratio adopted from (Xu, Z., Feng, Z., Zhao, C., Zheng, J., Yang, J., Tian, F., ... & Sher, H. (2013). The canopy rainfall interception in actual and potential distribution of Qinghai spruce (Picea crassifolia) forest. Journal of Hydrology and Hydromechanics, 61(1), 64-72.)
                  cal("Interception"+i+"=total_Interception"+i +"*(0.04+0.067*lai)") 
                  cal("Ch"+i+"=IF((evap_rate"+i+"/"+coefficients[6]+ ")>1,1,(evap_rate"+i+"/"+coefficients[6]+ "))")
                  print "Total Interception of time step "+str(i)+" calculated!"                  
                  delmap("Va"+i)
                  delmap("DIT"+i)

                  
              else: 
                  pass
          except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while calculting interception at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )
###################    Calculation of Runoff
        def  WeithedFracts(self,ii):
          try:
                if  self.gotError==False:
                    if ii==1:
                            workingdir(self.Tboxotputdir.Text+"\\Lookups\\")
                            cal("imp_ow_area=owarea+imp_area")
                            cal("FracSum=((vegarea+barearea)*Cper)+(imp_ow_area*(1-Cper))")                            
                    elif ii==int(self.Tboxstarttimestep.Text): 
                            workingdir(self.Tboxotputdir.Text+"\\Lookups\\")
                            cal("imp_ow_area=owarea+imp_area")
                            cal("FracSum=((vegarea+barearea)*Cper)+(imp_ow_area*(1-Cper))")                      
                    else:
                            rastermap(self.Tboxotputdir.Text+"\\Lookups\\imp_ow_area.asc","imp_ow_area")
                            rastermap(self.Tboxotputdir.Text+"\\Lookups\\FracSum.asc","FracSum")
          except Exception, ex:
                   
                   #print sys.exc_info()[0]+ "ERROR in Calculation of Interception!"
                   MessageBox.Show( "Error:"+ ex.Message+"\n")
                   exit(0)
                   self.gotError=True     

        def  Surfacerunoff(self,ii,rainydays,coefficients):

          try:
                i=str(ii)
                if  self.gotError==False:
                    
                    print "Calculation of Surface Runof for time step "+i
                    workingdir(self.Tboxotputdir.Text+"\\")                                
                    cal("Cper=("+coefficients[3]+"*landfactor)+("+coefficients[4]+"*soilfactor)+((("+coefficients[2]+"*slop)/(10+slop)))")
                    self.WeithedFracts(ii)
                    workingdir(self.Tboxotputdir.Text+"\\")
                    #Since P-I=SR/Csr we use it to seprate runoff fractions
                    cal("Cimp=0.09*EXP(2.4*imp_ow_area)")                    
                    cal("Cwp=((1-imp_ow_area)*Cper)+(imp_ow_area*Cimp)")
                    cal("Pdaily" + i + "=rainfall"+i+"/"+str(rainydays[ii-1]))                    
                    cal("Csr"+i+"=(Cwp*Pdaily" + i + ")/((Cwp*Pdaily" + i + ")-("+coefficients[7]+"*Cwp)+"+coefficients[7]+")")
                    self.Cell_runoff=cal("Cell_runoff"+i+"=Ch"+i+"*Csr"+i+"*(rainfall"+i+"-total_Interception" + i + ")" )                    
                    cal("vegrunoff"+i+"=vegarea*Cper*Cell_runoff" + i+"*vegratio*(1-Cimp)" )
                    cal("barerunoff"+i+"=barearea*Cper*Cell_runoff"+i+"*bareratio*(1-Cimp)")
                    cal("imperrunoff"+i+"=imp_area*(1-Cper)*Cell_runoff"+i+"*(1+Cimp)")
                    cal("owrunoff"+i+"=owarea*0.1*Cell_runoff"+i)  #assuming 10 prcent runoff for open water
                   
                else:
                    pass   
          except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while calculting surface runoff at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )

 
###################    Calculation of Evapotranspiration
        def  ET_factor(self,ii,coefficients):
          try:
                i=str(ii)
                if  self.gotError==False: 
                    print "Calculation of ET factor for time step "+str(i)
                    workingdir(self.Tboxotputdir.Text+"\\")                  
                    #Zom=roughness_om 
                    #d=zd
                    #zm=wsml
                    #zh=wsml
                    #(Karman^2)=0.16
                    #We applied these calculations to lookups for better speed 
                    #aerodynamicresist=(ln(((zveg+2.0)-(0.67*zveg))/(0.123*zveg)) *ln((zveg+2.0)-(0.67*zveg))/(0.123*zveg)))/(Karman^2)
                    #penmann_coefficient=psychrometric constant(gamma)/slope of the first drivative of saturated vapor.                                       
                    self.penmann_coefficient=cal("penmann_coefficient"+i+"=gamma/((2503/((temp"+i+"+237.3)^2))*(2.71828^(17.3*temp"+i+"/(temp"+i+"+237.3))))")              
                    #self.winda=cal("winda"+i+"=IF(old_windspeed_ML<=zveg,(w_snominatorcor"+i+"/factor),wind"+i+")")
                    self.winda=cal("winda"+i+"=IF(wind"+i+"==0,0.01,wind"+i+")")
                    self.aerodynamicresist=cal("aerodynamicresist"+i+"=Aeroresit_wind1ms/winda"+i)
                    self.Laia=cal("laia=IF(lai>0,lai,1.0)")
                    self.canopyresist=cal("canopyresist=minstomata/laia")
                    self.ETaccual_factor=cal("ETaccual_factor"+i+"=(1.0+penmann_coefficient"+i+")/(1.0+((1.0+(canopyresist/aerodynamicresist"+i+"))*penmann_coefficient"+i+"))")
          except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while calculting ET factor at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )
        def  ET(self,ii,coefficients):
          try:
                i=str(ii)
                if  self.gotError==False: 
                    print "Calculation of Evapotranspiration of time step "+str(i)
                    workingdir(self.Tboxotputdir.Text+"\\")                  
                    # We applied these calculations on lookups for faster computation speed 
                    #aerodynamicresist=(ln(((zveg+2.0)-(0.67*zveg))/(0.123*zveg)) *ln((zveg+2.0)-(0.67*zveg))/(0.123*zveg)))/(Karman^2)
                    #and Karman=0.41
                    #penmann_coefficient=psychrometric constant(gamma)/slope of the first drivative of saturated vapor.
                    
   
                    self.rootwater=cal("rootwater=((fc-wp)*(rootdepth+tension_ht)*10)")  
                    self.gwdepth=cal("gwdepth"+i+"=IF((gwdepth"+i+"-tension_ht)>=0,(gwdepth"+i+"-tension_ht),0)") 
                    self.awc=cal("awc"+i+"=(rainfall"+i+"+(12.0*rootwater))")            
                    self.pet_veg=cal("pet_veg"+i+"=ETaccual_factor"+i+"*pet"+i)
                    self.a1_power_vega=cal("a1_power_vega"+i+"=awc"+i+"/pet_veg"+i)
                    self.a1_power_veg=cal("a1_power_veg"+i+"=IF(a1_power_vega"+i+">30.0,30.0,a1_power_vega"+i+")")
                    delmap("a1_power_vega"+i)
                    self.potential_to_actual_transpiration_factor=cal("potential_to_actual_transpiration_factor"+i+"=(1.0-(a1^a1_power_veg"+i+"))")                   
                    #self.soilwater_storage=cal("soilwater_storage"+str(ii)+"=IF(soilwater_storage"+str(ii-1)+">rootwater,rootwater,soilwater_storage"+str(ii-1)+")")
                    cal("soilwater_storage"+str(ii)+"=0")
                    self.actualtranspirationa=cal("actualtranspirationa"+i+"=potential_to_actual_transpiration_factor"+i+"*evap_rate"+i+"*pet_veg"+i)
                    self.actualtranspirationb=cal("actualtranspirationb"+i+"=IF(actualtranspirationa"+i+">(rainfall"+i+"-Interception"+i+"-vegrunoff"+i+"+soilwater_storage"+str(ii)+"),(rainfall"+i+"-Interception"+i+"-vegrunoff"+i+"+soilwater_storage"+str(ii)+"),actualtranspirationa"+i+")")    
                    self.actualtranspirationc=cal("actualtranspirationc"+i+"=IF(actualtranspirationb"+i+">(pet"+i+"-Interception"+i+"),(pet"+i+"-Interception"+i+"),actualtranspirationb"+i+")")
                    self.actualtranspiration=cal("actualtranspiration"+i+"=IF(lai==0,0,actualtranspirationc"+i+")")
                    delmap("actualtranspirationa"+i)
                    delmap("actualtranspirationb"+i)
                    self.gw_transpiration=cal("gw_transpiration"+i+"=IF(gwdepth"+i+"<=rootdepth,(pet_veg"+i+"-actualtranspiration"+i+"),0)")
                    self.transpiration=cal("transpiration"+i+"=IF(gwdepth"+i+"<=rootdepth,pet_veg"+i+",actualtranspiration"+i+")")                                    
                    self.a1_power_baresoila=cal("a1_power_baresoila"+i+"=(rainfall"+i+"+(12.0*(fc-residual_water_content)*(evapo_depth+tension_ht)*1000))/pet"+i)
                    self.a1powerbaresoil=cal("a1powerbaresoil"+i+"=IF(a1_power_baresoila"+i+">30.0,30.0,a1_power_baresoila"+i+")")                 
                    delmap("a1_power_baresoila"+i)
                    self.potento_actual_evapofactorbare=cal("potento_actual_evapofactorbare"+i+"=(1.0-(a1^a1powerbaresoil"+i+"))")
                    self.actual_baresoil_evapoa=cal("actual_baresoil_evapoa"+i+"=potento_actual_evapofactorbare"+i+"*evap_rate"+i+"*pet"+i)                  
                    self.actual_baresoil_evapob=cal("actual_baresoil_evapob"+i+"=IF(actual_baresoil_evapoa"+i+">(rainfall"+i+"-barerunoff"+i+"),(rainfall"+i+"-barerunoff"+i+"),actual_baresoil_evapoa"+i+")")                  
                    self.actual_baresoil_evapo=cal("actual_baresoil_evapo"+i+"=IF(actual_baresoil_evapob"+i+">pet"+i+",pet"+i+",actual_baresoil_evapob"+i+")")                   
                    self.gw_evapo=cal("gw_evapo"+i+"=IF(gwdepth"+i+"<evapo_depth,(pet"+i+"-actual_baresoil_evapo"+i+"),0)")                    
                    self.actual_baresoil_evapo=cal("actual_baresoil_evapo"+i+"=IF(gwdepth"+i+"<evapo_depth,pet"+i+",actual_baresoil_evapob"+i+")")
                    delmap("actual_baresoil_evapoa"+i)
                    delmap("actual_baresoil_evapob"+i)
                    #The  impervious_evapo2Precip_Ratio at monthly version changed to the evap_rate. the original was:    impervious_evapo2Precip_Ratio=0.85
                    self.impervious_evapoa=cal("impervious_evapoa"+i+"=evap_rate"+i+"*(rainfall"+i+"-imperrunoff"+i+")")
                    self.impervious_evapo=cal("impervious_evapo"+i+"=IF(impervious_evapoa"+i+">pet"+i+",pet"+i+",impervious_evapoa"+i+")")                    
                    self.Cell_actualtranspiration=cal("Cell_actualtranspiration"+i+"=transpiration"+i+"*vegarea")
                    self.Cell_actual_baresoil_evapo=cal("Cell_actual_baresoil_evapo"+i+"=actual_baresoil_evapo"+i+"*barearea")              
                    self.Cell_ow_evaporation=cal("Cell_ow_evaporation"+i+"=pet"+i+"*owarea")                    
                    self.Cell_imper_evaporation=cal("Cell_imper_evaporation"+i+"=impervious_evapo"+i+"*imp_area")
                    self.Cell_gw_transpiration=cal("Cell_gw_transpiration"+i+"=gw_transpiration"+i+"*vegarea")
                    self.Cell_gw_evaporation=cal("Cell_gw_evaporation"+i+"=gw_evapo"+i+"*barearea")                    
                    self.Cell_evapotranspiration=cal("Cell_evapotranspirations"+i+"=Interception"+i+"+Cell_actualtranspiration"+i+"+Cell_actual_baresoil_evapo"+i+"+Cell_imper_evaporation"+i)
                    #We have introduced a  limitation for acual evapotranspiration here, because it could not exceed than rainfall. Groundwater ET and ET from open water areas are included later on. 
                    self.Cell_evapotranspiration=cal("Cell_evapotranspiration"+i+"=IF(Cell_evapotranspirations"+i+">rainfall"+i+",rainfall"+i+",Cell_evapotranspirations"+i+")")
                    self.Cell_evapotranspiration=cal("Cell_evapotranspiration"+i+"=IF(Cell_evapotranspirations"+i+"<0, 0,Cell_evapotranspirations"+i+")")
                    delmap("Cell_evapotranspirations"+i)
                    self.Cell_evapotranspiration=cal("Cell_evapotranspiration"+i+"=Cell_evapotranspiration"+i+"+Cell_gw_transpiration"+i+"+Cell_gw_evaporation"+i+"+Cell_ow_evaporation"+i)
          except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while calculting ET at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )

###################    Calculation of recharge
        def  Recharge(self,ii):
           try:
                #Note if you change this function into lower case it gives error becuse the same name exists!
                i=str(ii)
                if  self.gotError==False: 
                    print "Calculation of recharge for time step "+str(i)
                    workingdir(self.Tboxotputdir.Text+"\\")                    
                    self.rechargea=cal("rechargea"+i+"=rainfall"+i+"-Cell_evapotranspiration"+i+"-Cell_runoff"+i)                    
                    self.rechargeb=cal("rechargeb"+i+"=IF(owarea>0,IF(rechargea"+i+"<0,0,rechargea"+i+"), rechargea"+i+")") #to set recharge from open water to zero instead of negative. This difference is added to ET 
                    self.recharge=cal("recharge"+i+"=IF(rechargeb"+i+"<(0-soilwater_storage"+str(ii)+"),IF(gwdepth"+i+">rootdepth,(0-soilwater_storage"+str(ii)+"),rechargeb"+i+"),rechargeb"+i+")")
                    self.Cell_evapotranspiration=cal("Cell_evapotranspiration"+i+"=Cell_evapotranspiration"+i+"+(rechargeb"+i+"-rechargea"+i+")") #adding 'negative' recharge difference for openwater to ET
                    self.wb_error=cal("wb_error"+i+"=rainfall"+i+"-Cell_evapotranspiration"+i+"-Cell_runoff"+i+"-recharge"+i)
                    #self.soilwater_storage=cal("soilwater_storage"+i+"=recharge"+i)
                    self.soilwater_storage=cal("soilwater_storage"+i+"=0")                                      
                
                                        
                else:
                    pass   

           except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while calculting recharge at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )
                
###################    Calculation of snow melt
        def  Snowmelt(self,ii,nloop,degreedays,coefficients):
           try:
                i=str(ii)
                workingdir(self.Tboxotputdir.Text+"\\")
                if ii==1 or nloop==1:                            
                       cal("SnowStore"+str(ii-1)+"=dem*0")    

                #Ref: Knight, C.G., Chang, H., Staneva, M.P. and Kostov, D. (2001) A
                #Simplified Basin Model For Simulating Runoff: The Struma
                #River GIS. Professional Geogr., 53 (4), 533–545.
                cal("SWE"+str(ii)+"=SnowStore"+str(ii-1)+"+(rainfall"+i+"/(1.61*(1.35^temp"+i+")+1))")  #share of snow in total (mm)                           
                cal("snowdepth"+str(ii)+"=SWE"+str(ii)+"/"+coefficients[12])
                #Ref for monthly Degree day:
                #Loukas, A., Vasiliades, L., Domenikiotis, C. and Dalezios, N.R.
                #(2005) Basin-Wide Actual Evapotranspiration Estimation
                #Using NOOA/AVHRR Satellite Data. Phys. Chem. Earth, 30,
                #69–79.
                cal("Cm"+i+"=IF(temp"+i+"<"+coefficients[10]+",0,"+coefficients[11]+")")
                cal("SnowMelt_a"+i+"=IF((snowcover"+i+">0&SWE"+i+">0.5),(Cm"+i+"*"+str(degreedays[ii])+"*temp"+i+"),0)")
                cal("SnowMelt"+i+"=IF(SnowMelt_a"+i+">SWE"+i+",SWE"+i+",SnowMelt_a"+i+")")
                # remaining snow in mm:
                cal("SnowStore"+i+"=SWE"+i+"-SnowMelt"+i)  # remaining snow in mm
                delmap("SnowMelt_a"+ i)
                delmap("Cm"+ i)
                #Another monthly method (We did not use this one:
                #Mohseni, O., & Stefan, H. G. (1998). A monthly streamflow model. Water Resources Research, 34(5), 1287-1298.
                #Snowmelt= [1+Cforest*(Msh-1)](Hn/Lf)

                # Hn=RS(1 - Albedo) +4.9*10^-9*cloudness*Emissivity(Temp+273.2)^4 

                #Emissivity can be calculated based on
                #Shuttleworth, W. J., Evapotranspiration, in Handbook of Hydrology,
                #edited by David R. Maidment, McGraw-Hill, New York, 1993

                #Emissivity=0.14(Ed^0.5)-0.34
           except Exception, exceptionObject:  
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened while calculting snowmelt at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )       
                
                
        def  Sumup(self,ii,nloop,coefficients):
           global qt_1
           global qbt_1
           try:
                i=str(ii)
                if ii==1 or nloop==1:
                    report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,"**************************************************************************")
                    report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,"Running at "+DateTime.Now.ToString()+ " with the following parameters:")
                    strfactors="a:"+coefficients[0]+" , alfa:"+coefficients[1]+" , wSlope:"+coefficients[2]+" , wLanduse:"+coefficients[3]+" , wSoil:"+coefficients[4]+" , x:"+coefficients[5]
                    strfactors=strfactors+" , LP:"+coefficients[6]+" , Mean intensity:"+self.IntensitytextBox.Text+" , Beta:"+coefficients[8]+" , Contribution:"+coefficients[9]
                    if self.checIncludSnow.Checked:
                        strfactors=strfactors+" , BaseTemp(snow):"+coefficients[10]+" , Melt factor:"+coefficients[11]+" , Snow density:"+coefficients[12]                     
                    report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,strfactors)
                    report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,"**************************************************************************")
                    if self.checkSurfinteract.Checked:
                         report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,"TimeStep"+"\t"+"AET"+"\t"+"Runoff"+"\t"+"Interception"+"\t"+"Recharge"+"\t"+"Qsurf[m³/mnt]"+"\t"+"Qb[m³/mnt]")
                    else:    
                        report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,"TimeStep"+"\t"+"AET"+"\t"+"Runoff"+"\t"+"Interception"+"\t"+"Recharge")
                    ETe=cal("MEAN(Cell_evapotranspiration"+i+")")
                    SRe=cal("MEAN(Cell_runoff"+i+")")
                    INTCe=cal("MEAN(Interception"+i+")")
                    RECHRG=cal("MEAN(Recharge"+i+")")
                    if self.checIncludSnow.Checked:
                        Snowmelt=cal("MEAN(Snowmelt"+i+")")
                        SReAndMelt=(float(SRe)+float(Snowmelt))
                        SRe=str(SReAndMelt)
                    if self.checkSurfinteract.Checked:
                          QSurfmonth=(float(self.Q0surfTextBox.Text)*float(self.XtextBox.Text))+(1000*(1-float(self.XtextBox.Text)) * float(self.AreatextBox.Text)*float(SRe))
                          QSubmonth=(float(self.QBaseTextBox.Text)*float(coefficients[8]))+(1000*(1-float(coefficients[8]))* float(coefficients[9]) * float(self.AreatextBox.Text)*float(RECHRG))
                          self.linData=i+"\t"+ETe+"\t"+SRe+"\t"+INTCe+"\t"+RECHRG+"\t"+str(QSurfmonth)+"\t"+str(QSubmonth)
                          qt_1=QSurfmonth
                          qbt_1=QSubmonth
                    else:
                         self.linData=i+"\t"+ETe+"\t"+SRe+"\t"+INTCe+"\t"+RECHRG
                    report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,self.linData)
                    
                    
                elif  self.gotError==False:
                    ETe=cal("MEAN(Cell_evapotranspiration"+i+")")
                    SRe=cal("MEAN(Cell_runoff"+i+")")
                    INTCe=cal("MEAN(Interception"+i+")")
                    RECHRG=cal("MEAN(Recharge"+i+")")
                    if self.checIncludSnow.Checked:
                        Snowmelt=cal("MEAN(SnowMelt"+i+")")
                        SReAndMelt=(float(SRe)+float(Snowmelt))
                        SRe=str(SReAndMelt)
                    if self.checkSurfinteract.Checked:
                          QSurfmonth=(float(self.XtextBox.Text)*qt_1)+1000*(1-float(self.XtextBox.Text)) * float(self.AreatextBox.Text)*float(SRe)
                          QSubmonth=(float(coefficients[8])*qbt_1)+(1000*(1-float(coefficients[8]))* float(coefficients[9]) * float(self.AreatextBox.Text)*float(RECHRG))
                          qt_1=QSurfmonth
                          qbt_1=QSubmonth
                          self.linData=i+"\t"+ETe+"\t"+SRe+"\t"+INTCe+"\t"+RECHRG+"\t"+str(QSurfmonth)+"\t"+str(QSubmonth)
                    else:
                         self.linData=i+"\t"+ETe+"\t"+SRe+"\t"+INTCe+"\t"+RECHRG
                    report(self.Tboxotputdir.Text+"\\"+self.TxtSimulations.Text,self.linData)
 
           except Exception, exceptionObject:
                self.gotError=True
                report(i+"\t"+exceptionObject.Message.ToString())

                
        def  CleanUnwantedMaps(self,ii):
            i=str(ii)
            print "remove temporary maps created at time step"+ i
            try:
                if  self.Keep_total_Interception.Checked == False:
                    delmap("total_Interception"+ i)
                if  self.Keep_Interception.Checked == False:
                    delmap("Interception"+ i)
                if  self.Keep_Csr.Checked == False:
                    delmap("Csr"+ i)
                if  self.Keep_Cell_runoff.Checked == False:
                    delmap("Cell_runoff"+ i)
                if  self.Keep_vegrunoff.Checked == False:
                    delmap("vegrunoff"+ i)
                if  self.Keep_barerunoff.Checked == False:
                    delmap("barerunoff"+ i)
                if  self.Keep_imperrunoff.Checked == False:
                    delmap("imperrunoff"+ i)
                if  self.Keep_owrunoff.Checked == False:
                    delmap("owrunoff"+ i)
                if  self.Keep_Cell_actualtranspiration.Checked == False:
                    delmap("Cell_actualtranspiration"+ i)
                if  self.Keep_Cell_actual_baresoil_evapo.Checked == False:
                    delmap("Cell_actual_baresoil_evapo"+ i)
                if  self.Keep_Cell_ow_evaporation.Checked == False:
                    delmap("Cell_ow_evaporation"+ i)
                if  self.Keep_Cell_imper_evaporation.Checked == False:
                    delmap("Cell_imper_evaporation"+ i)
                if  self.Keep_Cell_gw_transpiration.Checked == False:
                    delmap("Cell_gw_transpiration"+ i)
                if  self.Keep_Cell_gw_evaporation.Checked == False:
                    delmap("Cell_gw_evaporation"+ i)
                if  self.Keep_Cell_evapotranspiration.Checked == False:
                    delmap("Cell_evapotranspiration"+ i)
                if  self.Keep_recharge.Checked == False:
                    delmap("recharge"+ i)
                if  self.Keep_soilwater_storage.Checked == False:
                    delmap("soilwater_storage"+ str(ii-1))
                if  self.Keep_penmann_coefficient.Checked == False:
                    delmap("penmann_coefficient"+  i)

               
                delmap("Ch"+i)
                delmap("evap_rate"+i)
                delmap("Pdaily"+i)
                delmap("awc"+i)
                delmap("pet_veg"+i)                
                delmap("potential_to_actual_transpiration_factor"+i)
                delmap("actualtranspirationc"+i)
                delmap("actualtranspiration"+i)
                delmap("gw_transpiration"+i)
                delmap("transpiration"+i)
                delmap("a1powerbaresoil"+i)
                delmap("potento_actual_evapofactorbare"+i)
                delmap("gw_evapo"+i)
                delmap("actual_baresoil_evapo"+i)
                delmap("impervious_evapoa"+i)
                delmap("impervious_evapo"+i)
                delmap("rechargeb"+i)
                delmap("rechargea"+i)
                delmap("winda"+i)
                delmap("a1_power_veg"+i)                
                delmap("aerodynamicresist"+i)
                delmap("Va"+i)
                delmap("DIT"+i)                
                print "temporary filse of time step"+ i+" removed!"

            except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened during removing temp maps at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )                
                
        def  CleanTempMaps(self,ii):
 
            print "remove final temporary maps "
            try:
                delmap("rootwater")
                delmap("Cper")
                delmap("Cimp")
                delmap("Cwp") 
                delmap("imp_ow_area")           
                delmap("aLAI")
                delmap("laia")                
                delmap("canopyresist")
                if  self.Keep_soilwater_storage.Checked == False:
                   # delmap("soilwater_storage"+ str(ii-1))            
                    pass
                print "Model has been successfully completed"
            except Exception, exceptionObject:
                self.gotError=True
                if sys.exc_info()[-1]!=None:
                    raise Exception('An error happened during removing temp maps at line ' + str(sys.exc_info()[-1].tb_lineno)+"\n " +exceptionObject.Message.ToString() )
                else:
                    raise Exception(exceptionObject.Message.ToString()  )                
                                            
# +++++++++++++++++++++++++++++++++++++++++++++++++ End of Hydrological Processes ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        def CloseModel(self, sender, args):
            try:                
                if self.allowclose==0:                        
                        
                        if MessageBox.Show("Are you sure you want to exit the page?" ,"Close " + "Application"  ,MessageBoxButtons.YesNo)== DialogResult.Yes:
                            
                            for xControl in self.Controls:			                    
                                  xControl.Dispose()                                  
                            args.Cancel=0
                            Environment.Exit(0)                           
                            self.allowclose=1
                            exit(0)
                            
                        else:
                            args.Cancel=1
                else:
                        args.Cancel=0
            except Exception, ex: 
                MessageBox.Show("An error happend while closing the model!"+"\n"+ ex.Message)    
#Above function closes current page but we need finalizClose() to exit all  Application                        
        def finalizClose(self, sender, args):
                allowclose=1
                Application.Exit()
                #Process.GetCurrentProcess().Kill()
                  
                
        def buteditmodelClick(self, sender, args):
                self.allowclose=1
                showeditor("")
                
 
 
        def buttonNext1Click(self, sender, e):
                self.Pages.SelectedTab = self.optionPage
        def buttonNext2Click(self, sender, e):
                self.Pages.SelectedTab = self.optionPage
#here we select paths of landuse and DEM file 
        def butDemDirClick(self, sender, e):
                self.openFileDialog1.Filter= "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
                if self.openFileDialog1.ShowDialog() == DialogResult.OK:
                   print "DEM path is defined, as:" +"\n"+ self.openFileDialog1.FileName
                   self.TboxdemDir.Text= self.openFileDialog1.FileName
       
        def butsoilmapDirClick(self, sender, e):
                self.openFileDialog1.Filter= "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
                if self.openFileDialog1.ShowDialog() == DialogResult.OK:
                   print "Soil map path is defined, as:" +"\n"+ self.openFileDialog1.FileName
                   self.TboxsoilmapDir.Text= self.openFileDialog1.FileName 
                   
        def butlanduseClick(self, sender, e):
                self.openFileDialog1.Filter= "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
                if self.openFileDialog1.ShowDialog() == DialogResult.OK:
                   print "Slope map path is defined, as:" +"\n"+ self.openFileDialog1.FileName
                   self.TboxLandusfile.Text= self.openFileDialog1.FileName                      
        def butSlopemapDirClick(self, sender, e):
                self.openFileDialog1.Filter= "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
                if self.openFileDialog1.ShowDialog() == DialogResult.OK:
                   print "Slope map path is defined, as:" +"\n"+ self.openFileDialog1.FileName
                   self.TboxSlopemapDir.Text= self.openFileDialog1.FileName  
        def butOservClick(self, sender, e):
                self.openFileDialog1.Filter= "Table files (*.tbl)|*.tbl|txt files (*.txt)|*.txt|All files (*.*)|*.*"
                if self.openFileDialog1.ShowDialog() == DialogResult.OK:
                   print "File " +"\n"+ self.openFileDialog1.FileName +"\n"+" has setted as observation"
                   self.TboxObseved.Text= self.openFileDialog1.FileName  
                   
        def butEstimatClick(self, sender, e):
                self.openFileDialog1.Filter= "Table files (*.tbl)|*.tbl|txt files (*.txt)|*.txt|All files (*.*)|*.*"
                if self.openFileDialog1.ShowDialog() == DialogResult.OK:
                   print "File " +"\n"+ self.openFileDialog1.FileName +"\n"+" has setted as observation"
                   self.TboxEstimted.Text= self.openFileDialog1.FileName                     
        def ClickSlopFromDem(self, sender, e):
                
                if sender.Checked == True:
                    self.butSlopemapDir.Enabled = False
                    self.TboxSlopemapDir.Enabled = False
                    print "Slope map will be calculated from digital elevation model automatically"
                else:
                    self.butSlopemapDir.Enabled = True
                    self.TboxSlopemapDir.Enabled = True
                    print "Slope map will be picked up from above path"

        def butLAIClick(self, sender, e):
                self.openFileDialog1.Filter= "ESRI ASCII files (*.asc)|*.asc|txt files (*.txt)|*.txt|All files (*.*)|*.*"
                if self.openFileDialog1.ShowDialog() == DialogResult.OK:
                   print "LIA map path is defined, as:" +"\n"+ self.openFileDialog1.FileName
                   self.textLAIdir.Text= self.openFileDialog1.FileName

        def ClickcheckSim(self, sender, e):
                
                if sender.Checked == True:
                    self.TxtSimulations.Enabled = True                    
                    print "Create simulation file automatically, this file is required for calibration."
                else:
                    self.TxtSimulations.Enabled = False                    
                    print "Run without creating simulation file."   
        def ClickcheckFrac(self, sender, e):                
                if sender.Checked == True:
                    self.TxtSimulations.Enabled = True                    
                    print "The model will read fraction from disk."
                else:
                    self.TxtSimulations.Enabled = False                    
                    print "Fraction will be generated according to the lookups."    
        def ClickcheckIrrg(self, sender, e):                
                if sender.Checked == True:
                    self.TxtSimulations.Enabled = True                    
                    print "Irrigated water will read from the folder."
                else:
                    self.TxtSimulations.Enabled = False                    
                    print "No consideration for irrigated water."                                                               

        def ClickcheckSnow(self, sender, e):
                
                if sender.Checked == True: 
                    self.snowGroup.Enabled = True
                    print "Snow processing is activated. You may set the parameters or accept the defaults."
                else:                    
                    print "Snow component is inactive now" 
                    self.snowGroup.Enabled = False
#here we choose folders for inputs and outputs of model 
        def ButworkdirClick(self, sender, e):
                if self.folderBrowserDialog1.ShowDialog() == DialogResult.OK:
                   self.AutoLoad(self.folderBrowserDialog1.SelectedPath)                   
                   
                else:
                       print "Note there is no folder ...\\inputs\\maps\\ in selected directory!" 
        def DbClickAutofinder(self, sender, e):
                
                if len(self.Tboxworkingdir.Text)>0:
                   self.AutoLoad(self.Tboxworkingdir.Text)                   
                   
                else:
                   self.ButworkdirClick(sender,e)
                        
        def AutoLoad(self, tagetpath):
              
                   self.Tboxworkingdir.Text= tagetpath
                   if IO.Directory.Exists(self.Tboxworkingdir.Text+"\\outputs")==False:
                       IO.Directory.CreateDirectory(self.Tboxworkingdir.Text+"\\outputs")
                   
                   self.Tboxotputdir.Text=self.Tboxworkingdir.Text+"\\outputs"
                   if IO.Directory.Exists(self.Tboxworkingdir.Text+"\\inputs\\maps\\"):
                       print "working directory is selected ,now"
                       for  FL in IO.Directory.GetFiles(self.Tboxworkingdir.Text+"\\inputs\\maps\\"):
                           FIL=IO.Path.GetFileNameWithoutExtension(FL).lower()
                           Exten=IO.Path.GetExtension(FL).lower()
                           if  str(Exten).endswith(".asc") or str(Exten).endswith(".txt") :                               
                                   if str(FIL).startswith("elevation"):
                                       self.TboxdemDir.Text=FL
                                   elif str(FIL).startswith("dem"):
                                       self.TboxdemDir.Text=FL
                                   elif str(FIL).startswith("landuse"):
                                       self.TboxLandusfile.Text=FL
                                   elif str(FIL).startswith("slop"):
                                       self.TboxSlopemapDir.Text=FL
                                   elif str(FIL).startswith("lai"):
                                       self.textLAIdir.Text=FL    
                                   elif str(FIL).startswith("soil"):
                                       self.TboxsoilmapDir.Text=FL
  

        def butOutDirClick(self, sender, e):
                if self.folderBrowserDialog1.ShowDialog() == DialogResult.OK:
                   print "output folder selected, now"
                   self.Tboxotputdir.Text= self.folderBrowserDialog1.SelectedPath                   
        def buttonPreveClick(self, sender, e):
                self.Pages.SelectedTab =self.inputPage

        def buttondefualtsClick(self, _, __):
                
                #MessageBox.Show("You clicked on " + self.TboxPrefixPET.Text) 
                self.TboxPrefixLAI.Text="lai"
                self.TboxPrefixrainfall.Text="rain"
                self.TboxPrefixPET.Text="pet"
                self.TboxPrefixTemperature.Text="temp"
                self.TboxWind.Text="wind"
                self.Tboxgwdepth.Text="gwdepth"
                self.Tboxsnowcover.Text="snowcover"
                self.TboxPrefixIrrigatedArea.Text="Irrigationcover"
                self.Tboxnodata.Text="-9999"
                self.TxtFirstStepNo.Text="1"
                
        def buttonDefualtParmClick(self, _, __):
                self.IntensitytextBox.Text ="4"
                self.LPtextBox.Text ="0.85"
                self.TboxAlfaCoef.Text ="1.5"
                self.TboxCoefAintercetion.Text ="4.5"
                self.TboxwSoil.Text ="0.3"
                self.TboxwLanduse.Text ="0.3"
                self.TboxwSlop.Text ="0.4"                
                self.ContribtextBox.Text ="0.5"                             
                self.XtextBox.Text ="0.5"
                self.BetatextBox.Text ="0.75"
                self.AreatextBox.Text ="10"
                self.MeltFacttextBox.Text ="0.02"
                self.BaseTemp.Text ="0"
                self.Snowdensity.Text ="0.1"
        def buttonNextClick(self, sender, e):
            self.Pages.SelectedTab =self.runPage
        def buttonParmPgClick(self, sender, e):
            self.Pages.SelectedTab =self.optionPage
        def loadpage(self):
                self.MYcomponents = ComponentModel.Container()
                self.toolTip1 = ToolTip(self.MYcomponents)
                #this sub loads page objects
                print "Starting WetSpass ..."
                #Define a variable to store run reports
                report="" 
                #if we get an error let stop
                self.gotError=False
                #set value of progress out of 100
                self.progress=0
                #Getting the root directory to access some resources like Icon
                rootpath=IO.Path.GetDirectoryName( Application.ExecutablePath)+"\\"+IO.Path.GetFileNameWithoutExtension( Application.ExecutablePath) +"\\"
                #FolderBrowserDialog
                self.folderBrowserDialog1 = FolderBrowserDialog()
                #openFileDialog
                self.openFileDialog1=OpenFileDialog()

                # 
#===============Starting point of Gerphical Code of pages======================                
                self.Pages = TabControl()      #let define a cotainer for our pages
                self.inputPage = TabPage()         #page 1
                self.optionPage = TabPage()        #page 2
                self.runPage = TabPage()           #page 3
                self.lookupEditorPage = TabPage()    #page 4
                self.ParamPage = TabPage()         #page 5
                self.CalibPage = TabPage()         #page 6
                self.ResultsPage = TabPage()         #page 7
                self.aboutPage = TabPage()         #page 8
                
                self.Pages.Controls.Add(self.inputPage)
                self.Pages.Controls.Add(self.optionPage)                
                self.Pages.Controls.Add(self.ParamPage)
                self.Pages.Controls.Add(self.runPage)
                self.Pages.Controls.Add(self.lookupEditorPage)
                #We are not going to introduce automatic calibration in this version so the page is hidden
                #self.Pages.Controls.Add(self.CalibPage)
                self.Pages.Controls.Add(self.ResultsPage)
                self.Pages.Controls.Add(self.aboutPage)
                
                #< Page1 objects>  inputPage
                self.butworkingdir = Button()    
                self.Tboxworkingdir = TextBox()
                self.labelworkindir = Label()
                self.checkSlopFromDem = CheckBox()
                self.labelNoOfTimeSteps = Label()
                self.Tboxnooftimsteps = TextBox()
                self.Tboxnooftimsteps.Text=str(12)
                self.Tboxstarttimestep = TextBox()
                self.labelStartTimeSteps = Label()
                self.Tboxstarttimestep.Text=str(1)
                self.Q0surfLabel = Label()
                self.Q0BaseLabel = Label() 
                self.QBaseTextBox = TextBox()
                self.Q0surfTextBox = TextBox()
                self.Tboxendtimestep = TextBox()
                self.Tboxendtimestep.Text=str(2)
                self.labelFinalTimeSteps = Label()
                self.qbaseGroup = GroupBox()    
                self.buttonNext1 = Button()
                self.buttonNext = Button()
                self.butRun = Button()
                self.labelrainfall = Label()
                self.TboxPrefixrainfall = TextBox()
                self.TboxPrefixTemperature = TextBox()
                self.labeltemperature = Label()
                self.TboxPrefixPET = TextBox()
                self.labelpet = Label()
                self.TboxPrefixLAI = TextBox()
                self.labelLAIprefix = Label()
                self.TboxPrefixIrrigatedArea = TextBox()
                self.labelIrrigationcover = Label()
                self.buttonPreve = Button()
                self.buttondefualts = Button()
                self.buteditmodel = Button()
                self.butsoilmapDir = Button()
                self.butSlopemapDir = Button()
                self.labelDEM = Label()
                self.labelsoilmap = Label()
                self.labelSlopemap = Label()
                self.TboxLandusfile = TextBox()
                self.butlanduse = Button()
                self.labellanduse = Label()
                self.qbaseGroup.SuspendLayout()   
                
                # runPage 
                self.labelworkindir1 = Label()
                self.labelworkindir2 = Label()
                self.labelworkindir3 = Label()
                self.butOutDir = Button()
                self.label3 = Label()
                self.Tboxotputdir = TextBox()
                self.TxtSimulations = TextBox()
                self.checFracFromDir = CheckBox() 
                self.checAddIrrig = CheckBox() 
                self.checkPenman = CheckBox()                
                self.checkSimulations = CheckBox()     
                self.checIncludSnow = CheckBox()
                self.TboxdemDir = TextBox()
                self.TboxsoilmapDir = TextBox()
                self.TboxSlopemapDir = TextBox()
                self.butDemDir = Button()                
                self.Tboxnodata = TextBox()
                self.TxtFirstStepNo = TextBox()
                self.TxtPeriodicNos = TextBox()
                self.TboxWind = TextBox()
                self.Tboxgwdepth = TextBox()
                self.Tboxsnowcover = TextBox()
                self.labelnodata = Label()
                self.labelFirstStepNo = Label()
                self.labelPeriodic  = Label()
                self.labelwind = Label()
                self.labelgwdepth = Label()
                self.labelsnowcover = Label()
                self.Pages.SuspendLayout()
                self.inputPage.SuspendLayout()
                self.optionPage.SuspendLayout()
                self.runPage.SuspendLayout()
                # aboutPage 
                self.aboutPage.SuspendLayout()
                self.SuspendLayout()
                
                
                # ParamPage 
                self.Globalgroup = GroupBox()
                self.LocalgroupBox = GroupBox()
                self.Interactgroup = GroupBox()
                self.snowGroup = GroupBox()                            
                self.ParamPage.SuspendLayout()
                self.butRun = Button()
                self.labelParamDiscript = Label()
                self.labelCalibrData = Label()
                 #XXXXXXXXXXXXXXX
                self.buttonParPg = Button() 
                self.Globalgroup.SuspendLayout()
                self.LocalgroupBox.SuspendLayout()
                self.Interactgroup.SuspendLayout()
                self.snowGroup.SuspendLayout()
                
                
                # CalibPage 
                self.buttonPreveCal = Button()
                self.buttonNextCal = Button()
                self.buttonDefualtsCal = Button()
                self.butSetObservData = Button()
                self.buteDoCalibr = Button()
                self.TboxObseved = TextBox()
                self.TboxEstimted = TextBox()
                self.butSetSimulatedata = Button()
                # ResultsPage
                
                self.labResults = Label()
                self.Keep_total_Interception = CheckBox()
                self.Keep_Interception = CheckBox()
                self.Keep_Csr = CheckBox()
                self.Keep_Cell_runoff = CheckBox()
                self.Keep_vegrunoff = CheckBox()
                self.Keep_barerunoff = CheckBox()
                self.Keep_imperrunoff = CheckBox()
                self.Keep_owrunoff = CheckBox()
                self.Keep_Cell_actualtranspiration = CheckBox()
                self.Keep_Cell_actual_baresoil_evapo = CheckBox()
                self.Keep_Cell_ow_evaporation = CheckBox()
                self.Keep_Cell_imper_evaporation = CheckBox()
                self.Keep_Cell_gw_transpiration = CheckBox()
                self.Keep_Cell_gw_evaporation = CheckBox()
                self.Keep_Cell_evapotranspiration = CheckBox()
                self.Keep_recharge = CheckBox()
                self.Keep_soilwater_storage = CheckBox()
                self.Keep_penmann_coefficient = CheckBox()
                
                # 
                # Pages
                #   
                self.Pages.Dock = DockStyle.Fill
                self.Pages.Location = Point(0, 0)
                self.Pages.Name = "Pages"
                self.Pages.SelectedIndex = 0
                self.Pages.Size = Drawing.Size(696, 434)
             
                #< Page object>  inputPage
                # 
                self.inputPage.Controls.Add(self.TboxLandusfile)
                self.inputPage.Controls.Add(self.butlanduse)
                self.inputPage.Controls.Add(self.labelDEM)
                self.inputPage.Controls.Add(self.labelsoilmap)
                self.inputPage.Controls.Add(self.labelSlopemap)
                self.inputPage.Controls.Add(self.TboxdemDir)
                self.inputPage.Controls.Add(self.TboxsoilmapDir)
                self.inputPage.Controls.Add(self.TboxSlopemapDir)
                self.inputPage.Controls.Add(self.butDemDir)
                self.inputPage.Controls.Add(self.butsoilmapDir)
                self.inputPage.Controls.Add(self.butSlopemapDir)
                self.inputPage.Controls.Add(self.labellanduse)
                self.inputPage.Controls.Add(self.buttonNext1)
                self.inputPage.Controls.Add(self.labelFinalTimeSteps)
                self.inputPage.Controls.Add(self.Tboxendtimestep)
                self.inputPage.Controls.Add(self.Tboxstarttimestep)
                self.inputPage.Controls.Add(self.labelStartTimeSteps)
                self.inputPage.Controls.Add(self.Tboxnooftimsteps)
                self.inputPage.Controls.Add(self.labelNoOfTimeSteps)
                self.inputPage.Controls.Add(self.labelworkindir)
                self.inputPage.Controls.Add(self.Tboxworkingdir)
                self.inputPage.Controls.Add(self.butworkingdir)
                self.inputPage.Controls.Add(self.checkSlopFromDem)
                self.inputPage.Controls.Add(self.qbaseGroup)
               

                self.inputPage.Location = Point(4, 22)
                self.inputPage.Name = "inputPage"
                self.inputPage.Padding = Padding(3)
                self.inputPage.Size = Drawing.Size(688, 408)
                self.inputPage.Text = "Inputs"
                self.inputPage.UseVisualStyleBackColor = True
                self.qbaseGroup.Controls.Add(self.Q0surfLabel)
                self.qbaseGroup.Controls.Add(self.Q0surfTextBox)
                self.qbaseGroup.Controls.Add(self.Q0BaseLabel)
                self.qbaseGroup.Controls.Add(self.QBaseTextBox)
                self.qbaseGroup.Location = Point(360, 216)
                self.qbaseGroup.Name = "qbaseGroup"
                self.qbaseGroup.Size = Size(235, 115)
                self.qbaseGroup.TabIndex = 4
                self.qbaseGroup.TabStop = False
                #self.qbaseGroup.Text = "Intial values"
                self.qbaseGroup.Enabled = False
                
                # 
                #< Page object>  optionPage
                # 
                self.optionPage.Controls.Add(self.TxtFirstStepNo)
                self.optionPage.Controls.Add(self.TxtPeriodicNos)
                self.optionPage.Controls.Add(self.Tboxnodata)
                self.optionPage.Controls.Add(self.TboxWind)
                self.optionPage.Controls.Add(self.Tboxgwdepth)
                self.optionPage.Controls.Add(self.Tboxsnowcover)
                self.optionPage.Controls.Add(self.labelnodata)
                self.optionPage.Controls.Add(self.labelFirstStepNo)
                self.optionPage.Controls.Add(self.labelPeriodic)
                self.optionPage.Controls.Add(self.labelwind)
                self.optionPage.Controls.Add(self.labelgwdepth)
                self.optionPage.Controls.Add(self.labelsnowcover)
                self.optionPage.Controls.Add(self.buttondefualts)
                self.optionPage.Controls.Add(self.buteditmodel)
                self.optionPage.Controls.Add(self.buttonPreve)
                self.optionPage.Controls.Add(self.TboxPrefixIrrigatedArea)
                self.optionPage.Controls.Add(self.labelIrrigationcover)
                self.optionPage.Controls.Add(self.TboxPrefixLAI)
                self.optionPage.Controls.Add(self.labelLAIprefix)
                self.optionPage.Controls.Add(self.TboxPrefixPET)
                self.optionPage.Controls.Add(self.labelpet)
                self.optionPage.Controls.Add(self.TboxPrefixTemperature)
                self.optionPage.Controls.Add(self.labeltemperature)
                self.optionPage.Controls.Add(self.TboxPrefixrainfall)
                self.optionPage.Controls.Add(self.labelrainfall)
                self.optionPage.Controls.Add(self.buttonNext)
                self.optionPage.Location = Point(4, 22)
                self.optionPage.Name = "optionPage"
                self.optionPage.Padding = Padding(3)
                self.optionPage.Size = Drawing.Size(688, 408)
                self.optionPage.Text = "Settings"
                self.optionPage.UseVisualStyleBackColor = True
           
                
                #< Page object>  runPage
                # 
                self.groupRunMod = GroupBox()
                self.radioLaiFromLanduse = RadioButton()
                self.radioLaiFromInputs = RadioButton()
                self.button1 = Button()
                self.butLAI = Button()
                self.checkLAIFroDir = CheckBox()
                self.labLAI = Label()
                self.textLAIdir = TextBox()
                self.groupRunMod.SuspendLayout()
                self.runPage.Controls.Add(self.checFracFromDir) 
                self.runPage.Controls.Add(self.checAddIrrig)
                #We are not going to introduce this functionality in the current version so it is hidden
                #self.runPage.Controls.Add(self.checkPenman)
                self.runPage.Controls.Add(self.checkSimulations)
                self.runPage.Controls.Add(self.checIncludSnow)                
                self.runPage.Controls.Add(self.butOutDir)
                self.runPage.Controls.Add(self.label3)
                self.runPage.Controls.Add(self.Tboxotputdir)
                self.runPage.Controls.Add(self.TxtSimulations)
                self.runPage.Controls.Add(self.butRun)
                self.runPage.Controls.Add(self.groupRunMod)
                self.runPage.Location = Point(4, 22)
                self.runPage.Name = "runPage"
                self.runPage.Padding = Padding(3)
                self.runPage.Size = Drawing.Size(688, 408)
                self.runPage.Text = "Run"
                self.runPage.UseVisualStyleBackColor = True
                
                
                #< Page object>  ParamPage
                # 
                self.buttonNextParam= Button()
                self.ParamPage.Controls.Add(self.labelParamDiscript)
                self.checkSurfinteract = CheckBox()
                self.ParamPage.Controls.Add(self.checkSurfinteract)                
                #GroupBox
                self.IntensitytextBox = TextBox()
                self.rainadjustlabel = Label()
                self.LPlabel = Label()
                self.LPtextBox = TextBox()
                self.TboxAlfaCoef = TextBox()
                self.TboxCoefAintercetion = TextBox()
                self.alfalabel = Label()
                self.labelCoefAintercetion = Label()
                #GroupBox
                self.slopfactlabel = Label()
                self.TboxwSoil = TextBox()
                self.TboxwLanduse = TextBox()
                self.TboxwSlop = TextBox()
                self.soilfactlabel = Label()
                self.lanfactorlabel = Label()
                #Interactgroup 
                self.ContribtextBox = TextBox()
                self.ContribLabel = Label()
                self.BetaLabel = Label()                
                self.XtextBox = TextBox()
                self.BetatextBox = TextBox()
                self.AreatextBox = TextBox()
                self.Xlabel = Label()
                self.Arealabel = Label()                
                #snowGroup 
                self.MeltFacttextBox = TextBox()
                self.MeltFactLabel = Label()
                self.BaseTemp = TextBox()
                self.Snowdensity = TextBox()                
                self.BaseTemplabel = Label() 
                self.Snowdensitylabel = Label()
                self.ParamPage.Controls.Add(self.buttonNextParam)
                self.ParamPage.Controls.Add(self.buttonDefualtsCal)
                self.ParamPage.Controls.Add(self.buttonParPg)
                self.ParamPage.Controls.Add(self.Globalgroup)
                self.ParamPage.Controls.Add(self.LocalgroupBox)
                self.ParamPage.Controls.Add(self.Interactgroup)
                self.ParamPage.Controls.Add(self.snowGroup)
                
                
                
                
                #< Page object>  CalibPage
                # 
                self.CalibPage.Controls.Add(self.labelCalibrData)
                self.CalibPage.Controls.Add(self.buttonPreveCal)
                self.CalibPage.Controls.Add(self.buttonNextCal)                
                self.CalibPage.Controls.Add(self.butSetObservData)
                self.CalibPage.Controls.Add(self.buteDoCalibr)
                self.CalibPage.Controls.Add(self.TboxObseved)
                self.CalibPage.Controls.Add(self.TboxEstimted)
                self.CalibPage.Controls.Add(self.butSetSimulatedata) 
                
                # 
                #< Page object>  ResultsPage
                #                
                self.ResultsPage.Controls.Add( self.labResults)
                self.ResultsPage.Controls.Add( self.Keep_total_Interception ) 
                self.ResultsPage.Controls.Add( self.Keep_Csr )
                self.ResultsPage.Controls.Add( self.Keep_Interception )                
                self.ResultsPage.Controls.Add( self.Keep_Cell_runoff )
                self.ResultsPage.Controls.Add( self.Keep_vegrunoff )
                self.ResultsPage.Controls.Add( self.Keep_barerunoff )
                self.ResultsPage.Controls.Add( self.Keep_imperrunoff )
                self.ResultsPage.Controls.Add( self.Keep_owrunoff )
                self.ResultsPage.Controls.Add( self.Keep_Cell_actualtranspiration )
                self.ResultsPage.Controls.Add( self.Keep_Cell_actual_baresoil_evapo )
                self.ResultsPage.Controls.Add( self.Keep_Cell_ow_evaporation )
                self.ResultsPage.Controls.Add( self.Keep_Cell_imper_evaporation )
                self.ResultsPage.Controls.Add( self.Keep_Cell_gw_transpiration )
                self.ResultsPage.Controls.Add( self.Keep_Cell_gw_evaporation )
                self.ResultsPage.Controls.Add( self.Keep_Cell_evapotranspiration )
                self.ResultsPage.Controls.Add( self.Keep_recharge )
                self.ResultsPage.Controls.Add( self.Keep_soilwater_storage )
                self.ResultsPage.Controls.Add( self.Keep_penmann_coefficient )
                self.ResultsPage.Text = "Results"


#######################################################   PAGE 1: Inputs (Controls)    #####################################################################################################
                
                #< Page object>  labelworkindir
                self.labelworkindir.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelworkindir.Location = Point(8, 34)
                self.labelworkindir.Name = "labelworkindir"
                self.labelworkindir.Size = Drawing.Size(150, 23)
                self.labelworkindir.Text = "Working Directory:"
                #< Page object>  Tboxworkingdir
                self.Tboxworkingdir.Location = Point(182, 34)
                self.Tboxworkingdir.Name = "Tboxworkingdir"
                self.Tboxworkingdir.Size = Drawing.Size(411, 20)
                self.Tboxworkingdir.Text=""
                self.Tboxworkingdir.DoubleClick += self.DbClickAutofinder

                #< Page object>  butworkingdir
                self.butworkingdir.Location = Point(610, 34)
                self.butworkingdir.Name = "butworkingdir"
                self.butworkingdir.Size = Drawing.Size(30, 23)
                self.butworkingdir.Text = "..."
                self.butworkingdir.UseVisualStyleBackColor = True
                self.butworkingdir.Click += self.ButworkdirClick
                
 
                #< Page object>  labelDEM
                self.labelDEM.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelDEM.Location = Point(8, 68)
                self.labelDEM.Name = "labelDEM"
                self.labelDEM.Size = Drawing.Size(106, 23)
                self.labelDEM.Text = "DEM map:"
                #< Page object>  TboxdemDir
                self.TboxdemDir.Location = Point(182, 68)
                self.TboxdemDir.Name = "TboxdemDir"
                self.TboxdemDir.Size = Drawing.Size(411, 20)
                #< Page object>  butDemDir
                self.butDemDir.Location = Point(610, 68)
                self.butDemDir.Name = "butDemDir"
                self.butDemDir.Size = Drawing.Size(30, 23)
                self.butDemDir.Text = "..."
                self.butDemDir.UseVisualStyleBackColor = True
                self.butDemDir.Click += self.butDemDirClick
                
 
                 # < Page object>  labellanduse
                self.labellanduse.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labellanduse.Location = Point(8, 102)
                self.labellanduse.Name = "labellanduse"
                self.labellanduse.Size = Drawing.Size(106, 23)
                self.labellanduse.Text = "Land use map:"
                #< Page object>  TboxLandusfile
                self.TboxLandusfile.Location = Point(182, 102)
                self.TboxLandusfile.Name = "TboxLandusfile"
                self.TboxLandusfile.Size = Drawing.Size(411, 20)
                self.TboxLandusfile.Text=""
                #< Page object>  butlanduse
                self.butlanduse.Location = Point(610, 102)
                self.butlanduse.Name = "butlanduse"
                self.butlanduse.Size = Drawing.Size(30, 23)
                self.butlanduse.Text = "..."
                self.butlanduse.UseVisualStyleBackColor = True
                self.butlanduse.Click += self.butlanduseClick
                 
                
                #< Page object> labelsoilmap
                self.labelsoilmap.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelsoilmap.Location = Point(8, 136)
                self.labelsoilmap.Name = "labelsoilmap"
                self.labelsoilmap.Size = Drawing.Size(106, 23)
                self.labelsoilmap.Text = "Soil map:"
                #< Page object>  TboxsoilmapDir
                self.TboxsoilmapDir.Location = Point(182, 136)
                self.TboxsoilmapDir.Name = "TboxsoilmapDir"
                self.TboxsoilmapDir.Size = Drawing.Size(411, 20)
                #< Page object>  butsoilmapDir
                self.butsoilmapDir.Location = Point(610, 136)
                self.butsoilmapDir.Name = "butsoilmapDir"
                self.butsoilmapDir.Size = Drawing.Size(30, 23)
                self.butsoilmapDir.Text = "..."
                self.butsoilmapDir.UseVisualStyleBackColor = True
                self.butsoilmapDir.Click += self.butsoilmapDirClick
                
                
                #< Page object> labelSlopemap
                self.labelSlopemap.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelSlopemap.Location = Point(8, 170)
                self.labelSlopemap.Name = "labelSlopemap"
                self.labelSlopemap.Size = Drawing.Size(106, 23)
                self.labelSlopemap.Text = "Slope map:"
                #< Page object>  TboxSlopemapDir
                self.TboxSlopemapDir.Location = Point(182, 170)
                self.TboxSlopemapDir.Name = "TboxSlopemapDir"
                self.TboxSlopemapDir.Size = Drawing.Size(411, 20)
                #< Page object>  butSlopemapDir
                self.butSlopemapDir.Location = Point(610, 170)
                self.butSlopemapDir.Name = "butSlopemapDir"
                self.butSlopemapDir.Size = Drawing.Size(30, 23)
                self.butSlopemapDir.Text = "..."
                self.butSlopemapDir.UseVisualStyleBackColor = True
                self.butSlopemapDir.Click += self.butSlopemapDirClick
                
                #< Page object>  checkSlopFromDem
                # 
                self.checkSlopFromDem.Location = Point(8, 204)
                self.checkSlopFromDem.Name = "checkSlopFromDem"
                self.checkSlopFromDem.Size = Drawing.Size(304, 24)
                self.checkSlopFromDem.Text = "Create slope map frome DEM directly"
                self.checkSlopFromDem.UseVisualStyleBackColor = True
                self.checkSlopFromDem.CheckedChanged += self.ClickSlopFromDem
                # 
                
                #< Page object>  labelNoOfTimeSteps
                self.labelNoOfTimeSteps.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelNoOfTimeSteps.Location = Point(8, 250)
                self.labelNoOfTimeSteps.Name = "labelNoOfTimeSteps"
                self.labelNoOfTimeSteps.Size = Drawing.Size(129, 23)
                self.labelNoOfTimeSteps.Text = "No of time steps:"
                #< Page object>  Tboxnooftimsteps
                self.Tboxnooftimsteps.Location = Point(182, 250)
                self.Tboxnooftimsteps.Name = "Tboxnooftimsteps"
                self.Tboxnooftimsteps.Size = Drawing.Size(50, 20)


                #< Page object>  labelStartTimeSteps
                self.labelStartTimeSteps.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelStartTimeSteps.Location = Point(8, 284)
                self.labelStartTimeSteps.Name = "labelStartTimeSteps"
                self.labelStartTimeSteps.Size = Drawing.Size(129, 23)
                self.labelStartTimeSteps.Text = "Starting time step:"
                #< Page object>  Tboxstarttimestep
                self.Tboxstarttimestep.Location = Point(182, 284)
                self.Tboxstarttimestep.Name = "Tboxstarttimestep"
                self.Tboxstarttimestep.Size = Drawing.Size(50, 20)
                 
                
                #< Page object>  Tboxendtimestep
                self.Tboxendtimestep.Location = Point(182, 318)
                self.Tboxendtimestep.Name = "Tboxendtimestep"
                self.Tboxendtimestep.Size = Drawing.Size(50, 20)
                #< Page object>  labelFinalTimeSteps
                self.labelFinalTimeSteps.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelFinalTimeSteps.Location = Point(8, 318)
                self.labelFinalTimeSteps.Name = "labelFinalTimeSteps"
                self.labelFinalTimeSteps.Size = Drawing.Size(129, 23)
                self.labelFinalTimeSteps.Text = "Final time step:"
                
                
                #< Page object>  Q0surfLabel
                self.Q0surfLabel.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.Q0surfLabel.Location = Point(5, 25)
                self.Q0surfLabel.Name = "Q0surfLabel"
                self.Q0surfLabel.Size = Drawing.Size(170, 23)
                self.Q0surfLabel.Text = "Q0 Surface[m³/month]:"
               
                #< Page object>  Q0BaseLabel
                self.Q0BaseLabel.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.Q0BaseLabel.Location = Point(5, 80)
                self.Q0BaseLabel.Name = "Q0BaseLabel"
                self.Q0BaseLabel.Size = Drawing.Size(170, 23)
                self.Q0BaseLabel.Text = "Q0 Sub-surf.[m³/month]:"
            
            
                #< Page object>  buttonNext1
                self.buttonNext1.Location = Point(565, 367)
                self.buttonNext1.Name = "buttonNext1"
                self.buttonNext1.Size = Drawing.Size(75, 23)
                self.buttonNext1.Text = "Next >>"
                self.buttonNext1.UseVisualStyleBackColor = True
                self.buttonNext1.Click += self.buttonNext1Click
                
                
                
#######################################################   END OF PAGE 1 ##############################################################################################                                 
                               
#######################################################   PAGE 2: Settings (Controls)    #####################################################################################
                
          
                
                
                #< Page object>  labelrainfall
                self.labelrainfall.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelrainfall.Location = Point(8, 20)
                self.labelrainfall.Name = "labelrainfall"
                self.labelrainfall.Size = Drawing.Size(139, 23)
                self.labelrainfall.Text = "Prefix rainfall files:"
                #< Page object>  TboxPrefixrainfall
                self.TboxPrefixrainfall.Location = Point(170, 20)
                self.TboxPrefixrainfall.Name = "TboxPrefixrainfall"
                self.TboxPrefixrainfall.Size = Drawing.Size(65, 20)

                
                #< Page object>  labelsnowcover
                self.labelsnowcover.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelsnowcover.Location = Point(8, 50)
                self.labelsnowcover.Name = "labelsnowcover"
                self.labelsnowcover.Size = Drawing.Size(156, 23)
                self.labelsnowcover.Text = "Prefix SnowCover file:"
                #< Page object>  Tboxsnowcover
                self.Tboxsnowcover.Location = Point(170, 50)
                self.Tboxsnowcover.Name = "Tboxgwdepth"
                self.Tboxsnowcover.Size = Drawing.Size(65, 20)

                #< Page object>  labelpet
                self.labelpet.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelpet.Location = Point(8, 80)
                self.labelpet.Name = "labelpet"
                self.labelpet.Size = Drawing.Size(129, 23)
                self.labelpet.Text = "Prefix PET file:"
                #< Page object>  TboxPrefixPET
                self.TboxPrefixPET.Location = Point(170, 80)
                self.TboxPrefixPET.Name = "TboxPrefixPET"
                self.TboxPrefixPET.Size = Drawing.Size(65, 20)

                                
                #< Page object>  labeltemperature
                self.labeltemperature.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labeltemperature.Location = Point(8, 110)
                self.labeltemperature.Name = "labeltemperature"
                self.labeltemperature.Size = Drawing.Size(149, 23)
                self.labeltemperature.Text = "Prefix Temperature:"
                #< Page object>  TboxPrefixTemperature
                self.TboxPrefixTemperature.Location = Point(170, 110)
                self.TboxPrefixTemperature.Name = "TboxPrefixTemperature"
                self.TboxPrefixTemperature.Size = Drawing.Size(65, 20)
               
                
                #< Page object>  labelwind
                self.labelwind.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelwind.Location = Point(8, 140)
                self.labelwind.Name = "labelwind"
                self.labelwind.Size = Drawing.Size(156, 23)
                self.labelwind.Text = "Prefix Wind file:"
                #< Page object>  TboxWind
                self.TboxWind.Location = Point(170, 140)
                self.TboxWind.Name = "TboxWind"
                self.TboxWind.Size = Drawing.Size(65, 20)
                
                
                #< Page object>  labelgwdepth
                self.labelgwdepth.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelgwdepth.Location = Point(8, 170)
                self.labelgwdepth.Name = "labelgwdepth"
                self.labelgwdepth.Size = Drawing.Size(156, 23)
                self.labelgwdepth.Text = "Prefix GWDepth file:"
                #< Page object>  Tboxgwdepth
                self.Tboxgwdepth.Location = Point(170, 170)
                self.Tboxgwdepth.Name = "Tboxgwdepth"
                self.Tboxgwdepth.Size = Drawing.Size(65, 20)                               

                
                
                #< Page object>  labelIrrigationcover
                self.labelIrrigationcover.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelIrrigationcover.Location = Point(8, 200)
                self.labelIrrigationcover.Name = "labelIrrigationcover"
                self.labelIrrigationcover.Size = Drawing.Size(139, 23)
                self.labelIrrigationcover.Text = "Prefix Irrigation cover file:" 
                #
                #< Page object>  TboxPrefixIrrigatedArea
                self.TboxPrefixIrrigatedArea.Location = Point(170, 200)
                self.TboxPrefixIrrigatedArea.Name = "TboxPrefixIrrigatedArea"
                self.TboxPrefixIrrigatedArea.Size = Drawing.Size(65, 20)
                #
                #< Page object>  labelLAIprefix
                self.labelLAIprefix.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelLAIprefix.Location = Point(8, 230)
                self.labelLAIprefix.Name = "labelLAIprefix"
                self.labelLAIprefix.Size = Drawing.Size(166, 23)
                self.labelLAIprefix.Text = "Prefix LAI file:"
                #< Page object>  TboxPrefixLAI
                self.TboxPrefixLAI.Location = Point(170, 230)
                self.TboxPrefixLAI.Name = "TboxPrefixLAI"
                self.TboxPrefixLAI.Size = Drawing.Size(65, 20)
                #
                
                #< Page object>  labelnodata
                self.labelnodata.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelnodata.Location = Point(8, 270)
                self.labelnodata.Name = "labelnodata"
                self.labelnodata.Size = Drawing.Size(156, 23)
                self.labelnodata.Text = "No data value of grids:"

                 #< Page object>  Tboxnodata
                self.Tboxnodata.Location = Point(170, 270)
                self.Tboxnodata.Name = "Tboxnodata"
                self.Tboxnodata.Size = Drawing.Size(65, 20)
                
                #< Page object>  labelFirstStepNo
                self.labelFirstStepNo.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelFirstStepNo.Location = Point(8, 300)
                self.labelFirstStepNo.Name = "labelFirstStepNo"
                self.labelFirstStepNo.Size = Drawing.Size(196, 20)
                self.labelFirstStepNo.Text = "First Step Number:"

                #< Page object>  TxtFirstStepNo
                self.TxtFirstStepNo.Location = Point(170, 300)
                self.TxtFirstStepNo.Name = "TxtFirstStepNo"
                self.TxtFirstStepNo.Size = Drawing.Size(65, 20)

                
                #< Page object>  labelPeriodic
                self.labelPeriodic.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelPeriodic.Location = Point(8, 330)
                self.labelPeriodic.Name = "labelFirstStepNo"
                self.labelPeriodic.Size = Drawing.Size(196, 20)
                self.labelPeriodic.Text = "Steps per Period:"

                #< Page object>  TxtPeriodicNos
                self.TxtPeriodicNos.Location = Point(170, 330)
                self.TxtPeriodicNos.Name = "TxtPeriodicNos"
                self.TxtPeriodicNos.Size = Drawing.Size(65, 20)
                self.TxtPeriodicNos.Text="12"        
                
                
                #< Page object>  Q0surfTextBox
                self.Q0surfTextBox.Location = Point(176, 25)
                self.Q0surfTextBox.Name = "Q0surfTextBox"
                self.Q0surfTextBox.Size = Drawing.Size(50, 20)
                self.Q0surfTextBox.Text="0"  
                
                #< Page object>  QBaseTextBox
                self.QBaseTextBox.Location = Point(176, 80)
                self.QBaseTextBox.Name = "QBaseTextBox"
                self.QBaseTextBox.Size = Drawing.Size(50, 20)
                self.QBaseTextBox.Text="0"        
               
                                
                #< Page object>  buttonNext
                self.buttonNext.Location = Point(581, 367)
                self.buttonNext.Name = "buttonNext"
                self.buttonNext.Size = Drawing.Size(75, 23)
                self.buttonNext.Text = "Next >>"
                self.buttonNext.UseVisualStyleBackColor = True
                self.buttonNext.Click += self.buttonNextClick
                
                #< Page object>  buttonPreve
                self.buttonPreve.Location = Point(25, 367)
                self.buttonPreve.Name = "buttonPreve"
                self.buttonPreve.Size = Drawing.Size(75, 23)
                self.buttonPreve.Text = "<< Previous"
                self.buttonPreve.UseVisualStyleBackColor = True
                self.buttonPreve.Click += self.buttonPreveClick
                
                # صفحه پارامتر اشیا کالیبراسیون
                # Globalgroup
                # 
                self.Globalgroup.Controls.Add(self.IntensitytextBox)
                self.Globalgroup.Controls.Add(self.rainadjustlabel)
                self.Globalgroup.Controls.Add(self.LPlabel)
                self.Globalgroup.Controls.Add(self.LPtextBox)
                self.Globalgroup.Controls.Add(self.TboxAlfaCoef)
                self.Globalgroup.Controls.Add(self.TboxCoefAintercetion)
                self.Globalgroup.Controls.Add(self.alfalabel)
                self.Globalgroup.Controls.Add(self.labelCoefAintercetion)
                self.Globalgroup.Location = Point(28, 40)
                self.Globalgroup.Name = "Globalgroup"
                self.Globalgroup.Size = Size(236, 144)
                self.Globalgroup.TabIndex = 0
                self.Globalgroup.TabStop = False
                self.Globalgroup.Text = "Global parameters"
                
                # LocalgroupBox
                # 
                self.LocalgroupBox.Controls.Add(self.slopfactlabel)
                self.LocalgroupBox.Controls.Add(self.TboxwSoil)
                self.LocalgroupBox.Controls.Add(self.TboxwLanduse)
                self.LocalgroupBox.Controls.Add(self.TboxwSlop)
                self.LocalgroupBox.Controls.Add(self.soilfactlabel)
                self.LocalgroupBox.Controls.Add(self.lanfactorlabel)
                self.LocalgroupBox.Location = Point(425, 40)
                self.LocalgroupBox.Name = "LocalgroupBox"
                self.LocalgroupBox.Size = Size(236, 144)
                self.LocalgroupBox.TabIndex = 1
                self.LocalgroupBox.TabStop = False
                self.LocalgroupBox.Text = "Local parameters"

                # Interactgroup
                # 
                self.Interactgroup.Controls.Add(self.ContribtextBox)
                self.Interactgroup.Controls.Add(self.ContribLabel)
                self.Interactgroup.Controls.Add(self.BetaLabel)                
                self.Interactgroup.Controls.Add(self.XtextBox)                 
                self.Interactgroup.Controls.Add(self.BetatextBox)
                self.Interactgroup.Controls.Add(self.AreatextBox)
                self.Interactgroup.Controls.Add(self.Xlabel)
                self.Interactgroup.Controls.Add(self.Arealabel)
                self.Interactgroup.Enabled = False
                self.Interactgroup.Location = Point(28, 216)
                self.Interactgroup.Name = "Interactgroup"
                self.Interactgroup.Size = Size(236, 144)
                self.Interactgroup.TabIndex = 2
                self.Interactgroup.TabStop = False
                self.Interactgroup.Text = "Surface water ineraction"
                
                # 
                # snowGroup
                # گروه برف نمایش داده نمیشه
                self.snowGroup.Controls.Add(self.MeltFacttextBox)
                self.snowGroup.Controls.Add(self.MeltFactLabel)
                self.snowGroup.Controls.Add(self.BaseTemp)
                self.snowGroup.Controls.Add(self.Snowdensity)                
                self.snowGroup.Controls.Add(self.BaseTemplabel)
                self.snowGroup.Controls.Add(self.Snowdensitylabel)
                self.snowGroup.Location = Point(425, 216)
                self.snowGroup.Name = "snowGroup"
                self.snowGroup.Size = Size(236, 144)
                self.snowGroup.TabIndex = 4
                self.snowGroup.TabStop = False
                self.snowGroup.Text = "Snowmelt processing"
                self.snowGroup.Enabled = False
                
                                
                # 
                # checkSurfinteract
                # 
                self.checkSurfinteract.Location = Point(28, 189)
                self.checkSurfinteract.Margin = Padding(0)
                self.checkSurfinteract.Name = "checkSurfinteract"
                self.checkSurfinteract.Size = Size(304, 24)
                self.checkSurfinteract.TabIndex = 3
                self.checkSurfinteract.Text = "Simulate surface water in the teraction  in the result file"
                self.checkSurfinteract.UseVisualStyleBackColor = True
                self.checkSurfinteract.CheckedChanged += self.CheckBaseFlowChanged                
                
                #self.labelParamDiscript
                self.labelParamDiscript.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelParamDiscript.Location = Point(8, 12)
                self.labelParamDiscript.Name = "labelParamDiscript"
                self.labelParamDiscript.Size = Drawing.Size(450, 20)
                self.labelParamDiscript.Text = "Specify the model parameters:"
                

               # Globalgroup
                # 

                # 
                # IntensitytextBox
                # 
                self.IntensitytextBox.Location = Point(136, 105)
                self.IntensitytextBox.Name = "IntensitytextBox"
                self.IntensitytextBox.Size = Size(60, 20)
                self.IntensitytextBox.TabIndex = 7
                self.IntensitytextBox.Text = "4"
                self.toolTip1.SetToolTip(self.IntensitytextBox, "The long term average rainfall intensity during the wet days (days with 1mm or more of rain)  as aggrigated indicator.")
                # 
                # rainadjustlabel
                # 
                self.rainadjustlabel.Location = Point(8, 108)
                self.rainadjustlabel.Name = "rainadjustlabel"
                self.rainadjustlabel.Size = Size(122, 23)
                self.rainadjustlabel.TabIndex = 6
                self.rainadjustlabel.Text = "Average intensity[mm/h]"
                # 
                # LPlabel
                # 
                self.LPlabel.Location = Point(8, 75)
                self.LPlabel.Name = "LPlabel"
                self.LPlabel.Size = Size(99, 23)
                self.LPlabel.TabIndex = 5
                self.LPlabel.Text = "LP coefficient"
                # 
                # LPtextBox
                # 
                self.LPtextBox.Location = Point(136, 75)
                self.LPtextBox.Name = "LPtextBox"
                self.LPtextBox.Size = Size(60, 20)
                self.LPtextBox.TabIndex = 4
                self.LPtextBox.Text = "0.85"                
                self.toolTip1.SetToolTip(self.LPtextBox, "A calibration parameter depending on the soil moisture (normally 0.5-0.85) ")
                # 
                # TboxAlfaCoef
                # 
                self.TboxAlfaCoef.Location = Point(136, 46)
                self.TboxAlfaCoef.Name = "TboxAlfaCoef"
                self.TboxAlfaCoef.Size = Size(60, 20)
                self.TboxAlfaCoef.TabIndex = 3
                self.TboxAlfaCoef.Text = "1.5"
                self.toolTip1.SetToolTip(self.TboxAlfaCoef, "A calibration cofficient is used [as the power] for the equation of evaporative efficiency ratio ")
                 
                # 
                # TboxCoefAintercetion
                # 
                self.TboxCoefAintercetion.Location = Point(136, 17)
                self.TboxCoefAintercetion.Name = "TboxCoefAintercetion"
                self.TboxCoefAintercetion.Size = Size(60, 20)
                self.TboxCoefAintercetion.TabIndex = 2
                self.TboxCoefAintercetion.Text = "4.5"
                self.toolTip1.SetToolTip(self.TboxCoefAintercetion, "interception threshold parameter[mm/day] ")
                # 
                # alfalabel
                # 
                self.alfalabel.Location = Point(7, 43)
                self.alfalabel.Name = "alfalabel"
                self.alfalabel.Size = Size(100, 23)
                self.alfalabel.TabIndex = 1
                self.alfalabel.Text = "alfa coefficient"
                # 
                # labelCoefAintercetion
                # 
                self.labelCoefAintercetion.Location = Point(7, 20)
                self.labelCoefAintercetion.Name = "labelCoefAintercetion"
                self.labelCoefAintercetion.Size = Size(100, 23)
                self.labelCoefAintercetion.TabIndex = 0
                self.labelCoefAintercetion.Text = "\"a\" interception"
                # 
                # LocalgroupBox
                # 

                # 
                # slopfactlabel
                # 
                self.slopfactlabel.Location = Point(9, 26)
                self.slopfactlabel.Name = "slopfactlabel"
                self.slopfactlabel.Size = Size(99, 23)
                self.slopfactlabel.TabIndex = 6
                self.slopfactlabel.Text = "Slope factor:"
                # 
                # TboxwSoil
                # 
                self.TboxwSoil.BackColor = Color.FromArgb(224, 224, 224)
                self.TboxwSoil.Location = Point(136, 90)
                self.TboxwSoil.Name = "TboxwSoil"
                self.TboxwSoil.Size = Size(76, 20)
                self.TboxwSoil.TabIndex = 4
                self.TboxwSoil.Text = "0.3"
                # 
                # TboxwLanduse
                # 
                self.TboxwLanduse.BackColor = Color.FromArgb(224, 224, 224)
                self.TboxwLanduse.Location = Point(136, 56)
                self.TboxwLanduse.Name = "TboxwLanduse"
                self.TboxwLanduse.Size = Size(76, 20)
                self.TboxwLanduse.TabIndex = 3
                self.TboxwLanduse.Text = "0.3"
                # 
                # TboxwSlop
                # 
                self.TboxwSlop.BackColor = Color.FromArgb(224, 224, 224)
                self.TboxwSlop.Location = Point(136, 23)
                self.TboxwSlop.Name = "TboxwSlop"
                self.TboxwSlop.Size = Size(76, 20)
                self.TboxwSlop.TabIndex = 2
                self.TboxwSlop.Text = "0.4"
                # 
                # soilfactlabel
                # 
                self.soilfactlabel.Location = Point(9, 90)
                self.soilfactlabel.Name = "soilfactlabel"
                self.soilfactlabel.Size = Size(100, 23)
                self.soilfactlabel.TabIndex = 1
                self.soilfactlabel.Text = "Soil factor:"
                # 
                # lanfactorlabel
                # 
                self.lanfactorlabel.Location = Point(8, 58)
                self.lanfactorlabel.Name = "lanfactorlabel"
                self.lanfactorlabel.Size = Size(100, 23)
                self.lanfactorlabel.TabIndex = 0
                self.lanfactorlabel.Text = "Land factor:"
                # 
                # Interactgroup
                # 

                # 
                # ContribtextBox
                # 
                self.ContribtextBox.Location = Point(136, 110)
                self.ContribtextBox.Name = "ContribtextBox"
                self.ContribtextBox.Size = Size(60, 20)
                self.ContribtextBox.TabIndex = 7
                self.ContribtextBox.Text = "0.5"
                self.toolTip1.SetToolTip(self.ContribtextBox, "Recharge contribution parameter has dependency on several factors namely area of the basin, drainage network, slope and surface the saturation hydraulic conductivity of upper zone of the soil. ")
                # 
                # ContribLabel
                # 
                self.ContribLabel.Location = Point(8, 113)
                self.ContribLabel.Name = "ContribLabel"
                self.ContribLabel.Size = Size(122, 23)
                self.ContribLabel.TabIndex = 6
                self.ContribLabel.Text = "Contribution factor"
                # 
                # BetaLabel
                # 
                self.BetaLabel.Location = Point(8, 80)
                self.BetaLabel.Name = "BetaLabel"
                self.BetaLabel.Size = Size(122, 23)
                self.BetaLabel.TabIndex = 5
                self.BetaLabel.Text = "Beta coefficient (0-1)"
                #                
                # XtextBox
                # 
                self.XtextBox.Location = Point(136, 51)
                self.XtextBox.Name = "XtextBox"
                self.XtextBox.Size = Size(60, 20)
                self.XtextBox.TabIndex = 3
                self.XtextBox.Text = "0.5"
                
                
                #                
                # BetatextBox
                # 
                self.BetatextBox.Location = Point(136, 80)
                self.BetatextBox.Name = "BetatextBox"
                self.BetatextBox.Size = Size(60, 20)
                self.BetatextBox.TabIndex = 3
                self.BetatextBox.Text = "0.75"
                
                
                
                # 
                # AreatextBox
                # 
                self.AreatextBox.Location = Point(136, 22)
                self.AreatextBox.Name = "AreatextBox"
                self.AreatextBox.Size = Size(94, 20)
                self.AreatextBox.TabIndex = 2
                self.AreatextBox.Text = "10"
                # 
                # Xlabel
                # 
                self.Xlabel.Location = Point(7, 48)
                self.Xlabel.Name = "Xlabel"
                self.Xlabel.Size = Size(100, 23)
                self.Xlabel.TabIndex = 1
                self.Xlabel.Text = "\"x\" coefficient(0-1)"
                # 
                # Arealabel
                # 
                self.Arealabel.Location = Point(7, 25)
                self.Arealabel.Name = "Arealabel"
                self.Arealabel.Size = Size(100, 23)
                self.Arealabel.TabIndex = 0
                self.Arealabel.Text = "Basin area (Km²)"
 
                # 
                # snowGroup
                # 

                # 
                # MeltFacttextBox
                # 
                self.MeltFacttextBox.Location = Point(136, 51)
                self.MeltFacttextBox.Name = "MeltFacttextBox"
                self.MeltFacttextBox.Size = Size(60, 20)
                self.MeltFacttextBox.TabIndex = 7
                self.MeltFacttextBox.Text = "0.02"
                # 
                # MeltFactLabel
                # 
                self.MeltFactLabel.Location = Point(8, 51)
                self.MeltFactLabel.Name = "MeltFactLabel"
                self.MeltFactLabel.Size = Size(122, 23)
                self.MeltFactLabel.TabIndex = 6
                self.MeltFactLabel.Text = "Melt factor"
                # 
                # BaseTemp
                # 
                self.BaseTemp.Location = Point(136, 22)
                self.BaseTemp.Name = "BaseTemp"
                self.BaseTemp.Size = Size(60, 20)
                self.BaseTemp.TabIndex = 3
                self.BaseTemp.Text = "0"
                # Snowdensity
                # 
                self.Snowdensity.Location = Point(136, 80)
                self.Snowdensity.Name = "BaseTemp"
                self.Snowdensity.Size = Size(60, 20)
                self.Snowdensity.TabIndex = 3
                self.Snowdensity.Text = "0.1"
                # 
                # Snowdensitylabel
                # 
                self.Snowdensitylabel.Location = Point(7, 80)
                self.Snowdensitylabel.Name = "BaseTemplabel"
                self.Snowdensitylabel.Size = Size(100, 23)
                self.Snowdensitylabel.TabIndex = 0
                self.Snowdensitylabel.Text = "Snow density"
                #
                
                # 
                # BaseTemplabel
                # 
                self.BaseTemplabel.Location = Point(7, 25)
                self.BaseTemplabel.Name = "BaseTemplabel"
                self.BaseTemplabel.Size = Size(100, 23)
                self.BaseTemplabel.TabIndex = 0
                self.BaseTemplabel.Text = "Base temperature"
                #
                #buttonNextParam
                #
                self.buttonNextParam.Location = Point(581, 367)
                self.buttonNextParam.Name = "buttonNext"
                self.buttonNextParam.Size = Drawing.Size(75, 23)
                self.buttonNextParam.Text = "Next >>"
                self.buttonNextParam.UseVisualStyleBackColor = True
                self.buttonNextParam.Click += self.buttonNextClick

                #< Page object>  buttonParPg
                self.buttonParPg.Location = Point(25, 367)
                self.buttonParPg.Name = "buttonParPg"
                self.buttonParPg.Size = Drawing.Size(75, 23)
                self.buttonParPg.Text = "<< Settings"
                self.buttonParPg.UseVisualStyleBackColor = True
                self.buttonParPg.Click += self.buttonParmPgClick                                           

                #buttonDefualtsCal
                self.buttonDefualtsCal.Location = Point(200, 367)
                self.buttonDefualtsCal.Name = "buttonDefualtsCal"
                self.buttonDefualtsCal.Size = Drawing.Size(110, 23)
                self.buttonDefualtsCal.Text = "Load Defealts"
                self.buttonDefualtsCal.UseVisualStyleBackColor = True
                self.buttonDefualtsCal.Click += self.buttonDefualtParmClick                                
                #self.buttonPreveCal
                self.buttonPreveCal.Location = Point(25, 367)
                self.buttonPreveCal.Name = "buttonPreve"
                self.buttonPreveCal.Size = Drawing.Size(85, 23)
                self.buttonPreveCal.Text = "<< Run Page"
                self.buttonPreveCal.UseVisualStyleBackColor = True
                self.buttonPreveCal.Click += self.buttonNextClick                
                #< Page object>  buttonNextCal
                self.buttonNextCal.Location = Point(581, 367)
                self.buttonNextCal.Name = "buttonNext"
                self.buttonNextCal.Size = Drawing.Size(75, 23)
                self.buttonNextCal.Text = "Inputs"
                self.buttonNextCal.UseVisualStyleBackColor = True
                self.buttonNextCal.Click +=self.buttonPreveClick
 
                
                #TboxObseved
                self.TboxObseved.Location = Point(100, 280)
                self.TboxObseved.Name = "TboxObseved"
                self.TboxObseved.Size = Drawing.Size(450, 20)
                
                #self.labelCalibrData
                self.labelCalibrData.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelCalibrData.Location = Point(8, 245)
                self.labelCalibrData.Name = "labelCalibrData"
                self.labelCalibrData.Size = Drawing.Size(650, 30)
                self.labelCalibrData.Text = "Specify the path of observed and Simulated time series in Tab delimited file format:"
                
                #butSetObservData
                self.butSetObservData.Location = Point(550, 280)
                self.butSetObservData.Name = "butSetObservData"
                self.butSetObservData.Size = Drawing.Size(120, 23)
                self.butSetObservData.Text = "Load Observed Data"
                self.butSetObservData.UseVisualStyleBackColor = True
                self.butSetObservData.Click += self.butOservClick
                #TboxEstimted
                self.TboxEstimted.Location = Point(100, 315)
                self.TboxEstimted.Name = "TboxEstimted"
                self.TboxEstimted.Size = Drawing.Size(450, 20)
                #butSetSimulatedata
                self.butSetSimulatedata.Location = Point(550, 315)
                self.butSetSimulatedata.Name = "butSetSimulatedata"
                self.butSetSimulatedata.Size = Drawing.Size(120, 23)
                self.butSetSimulatedata.Text = "Set Simulated Data"
                self.butSetSimulatedata.UseVisualStyleBackColor = True
                self.butSetSimulatedata.Click += self.butEstimatClick
                
                #buteDoCalibr:  calibration of model
                # 
                self.buteDoCalibr.Location = Point(417, 367)
                self.buteDoCalibr.Name = "buteDoCalibr"
                self.buteDoCalibr.Size = Drawing.Size(110, 23)
                self.buteDoCalibr.Text = "Calibrate Model"
                self.buteDoCalibr.UseVisualStyleBackColor = True
                self.buteDoCalibr.Click += self.buteDoCalibrClick

                
                
 #######################################################   END OF PAGE 2 ##################################################################################################               
 ######################################## #Start Page  Run  ##################################################################################################                                          
                #< Page object>  butRun
                self.butRun.BackgroundImage  = resourcesimage( "run")
                self.butRun.BackgroundImageLayout = ImageLayout.None
                self.butRun.Location = Point(296, 353)
                self.butRun.Name = "butRun"
                self.butRun.Size = Drawing.Size(75, 23)
                self.butRun.Text = "Run"
                self.butRun.UseVisualStyleBackColor = True
                self.butRun.Click += self.buttonRunClick
                		
                # 
                # groupRunMod
                # 
                self.groupRunMod.Controls.Add(self.textLAIdir)
                self.groupRunMod.Controls.Add(self.labLAI)
                self.groupRunMod.Controls.Add(self.checkLAIFroDir)
                self.groupRunMod.Controls.Add(self.butLAI)
                self.groupRunMod.Controls.Add(self.radioLaiFromInputs)
                self.groupRunMod.Controls.Add(self.radioLaiFromLanduse)
                self.groupRunMod.Location = Point(95, 195)
                self.groupRunMod.Name = "groupRunMod"
                self.groupRunMod.Size = Drawing.Size(584, 120)
                self.groupRunMod.TabIndex = 0
                self.groupRunMod.TabStop = False
                self.groupRunMod.Text = "Leaf Area Index (LAI) Mode:"
                
                # 
                # radioLaiFromLanduse
                # 
                self.radioLaiFromLanduse.Location = Point(28, 20)
                self.radioLaiFromLanduse.Name = "radioLaiFromLanduse"
                self.radioLaiFromLanduse.Size = Drawing.Size(220, 24)
                self.radioLaiFromLanduse.TabIndex = 0
                self.radioLaiFromLanduse.Text = "Automatically from Landuse Map lookups"
                self.radioLaiFromLanduse.TextAlign = Drawing.ContentAlignment.TopLeft
                self.radioLaiFromLanduse.UseVisualStyleBackColor = True
                self.radioLaiFromLanduse.CheckedChanged += self.radioLaiFromLanduseCheckedChanged
                self.radioLaiFromLanduse.Checked = True
                # 
                # radioLaiFromInputs
                # 
                
                self.radioLaiFromInputs.Location = Point(28, 50)
                self.radioLaiFromInputs.Name = "radioLaiFromInputs"
                self.radioLaiFromInputs.Size = Drawing.Size(287, 24)
                self.radioLaiFromInputs.TabIndex = 1
                self.radioLaiFromInputs.TabStop = True
                self.radioLaiFromInputs.Text = "Read LAI from 'Inputs'"
                self.radioLaiFromInputs.UseVisualStyleBackColor = True
                self.radioLaiFromInputs.CheckedChanged += self.radioLaiFromInputsCheckedChanged
                # 
                # butLAI
                # 
                self.butLAI.Location = Point(543, 85)
                self.butLAI.Name = "butLAI"
                self.butLAI.Size = Drawing.Size(35, 22)
                self.butLAI.TabIndex = 4
                self.butLAI.Text = "..."
                self.butLAI.UseVisualStyleBackColor = True
                self.butLAI.Click += self.butLAIClick
                # 
                # checkLAIFroDir
                # 
                self.checkLAIFroDir.Location = Point(305, 51)
                self.checkLAIFroDir.Name = "checkBox1"
                self.checkLAIFroDir.Size = Drawing.Size(291, 24)
                self.checkLAIFroDir.TabIndex = 5
                self.checkLAIFroDir.Text = "Read LAI per step from '..\Inputs\Maps\LAI' folder"
                self.checkLAIFroDir.UseVisualStyleBackColor = True
                self.checkLAIFroDir.CheckedChanged += self.ClickLAIfromDir
                #self.checkLAIFroDir.Checked = True
                # 
                # labLAI
                # 
                self.labLAI.Font = Drawing.Font("Microsoft Sans Serif", 8.25, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labLAI.Location = Point(7, 90)
                self.labLAI.Name = "labLAI"
                self.labLAI.Size = Drawing.Size(100, 23)
                self.labLAI.TabIndex = 6
                self.labLAI.Text = "LAI map:"
                # 
                # textLAIdir
                # 
                self.textLAIdir.Location = Point(86, 88)
                self.textLAIdir.Name = "textLAIdir"
                self.textLAIdir.Size = Drawing.Size(451, 20)
                self.textLAIdir.TabIndex = 7
                # 
                
                #< Page object>  buttondefualts
                # 
                self.buttondefualts.Location = Point(200, 367)
                self.buttondefualts.Name = "buttondefualts"
                self.buttondefualts.Size = Drawing.Size(110, 23)
                self.buttondefualts.Text = "Load Defealts"
                self.buttondefualts.UseVisualStyleBackColor = True
                self.buttondefualts.Click += self.buttondefualtsClick
                # 
                #< Page object>  Start editting of model
                # 
                self.buteditmodel.Location = Point(417, 367)
                self.buteditmodel.Name = "buteditmodel"
                self.buteditmodel.Size = Drawing.Size(110, 23)
                self.buteditmodel.Text = "Edit Model"
                self.buteditmodel.UseVisualStyleBackColor = True
                self.buteditmodel.Click += self.buteditmodelClick
                #
                # labResults
                # 
                self.labResults.Font = Drawing.Font("Microsoft Sans Serif", 8.25, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labResults.Location = Point(4, 10)
                self.labResults.Name = "labResults"
                self.labResults.Size = Drawing.Size(650, 45)
                self.labResults.TabIndex = 6
                self.labResults.Text = "Tick the check box next to each item of interest in model outputs. By default due to disk space issuies, WetSpass removes most of the generated intermediate results."
                #                 
                
#1
                #< Page object>  Keep_Interception CheckBox
                # 
                self.Keep_Interception.Location = Point(12, 50)
                self.Keep_Interception.Size = Drawing.Size(304, 24)
                self.Keep_Interception.Text = "Interception of the Cell (Interception)"
                self.Keep_Interception.UseVisualStyleBackColor = True
                self.Keep_Interception.CheckState = CheckState.Checked
#2

                #< Page object>  Keep_Csr CheckBox
                # 
                self.Keep_Csr.Location = Point(12, 75)
                self.Keep_Csr.Size = Drawing.Size(304, 24)
                self.Keep_Csr.Text = "Runoff Coefficient (Csr)"
                self.Keep_Csr.UseVisualStyleBackColor = True                
                
                


#3

                #< Page object>  Keep_Cell_runoff CheckBox
                # 
                self.Keep_Cell_runoff.Location = Point(12, 100)
                self.Keep_Cell_runoff.Size = Drawing.Size(304, 24)
                self.Keep_Cell_runoff.Text = "Runoff of the Cell (Cell_runoff)"
                self.Keep_Cell_runoff.UseVisualStyleBackColor = True
                self.Keep_Cell_runoff.CheckState = CheckState.Checked
#2

#4

                #< Page object>  Keep_vegrunoff CheckBox
                # 
                self.Keep_vegrunoff.Location = Point(12, 125)
                self.Keep_vegrunoff.Size = Drawing.Size(304, 24)
                self.Keep_vegrunoff.Text = "Runoff in Vegetated Area(vegrunoff)"
                self.Keep_vegrunoff.UseVisualStyleBackColor = True


#5

                #< Page object>  Keep_Cell_evapotranspiration CheckBox
                # 
                self.Keep_Cell_evapotranspiration.Location = Point(12, 150)
                self.Keep_Cell_evapotranspiration.Size = Drawing.Size(304, 24)
                self.Keep_Cell_evapotranspiration.Text = "Evapotranspiration of the Cell(Cell_evapotranspiration)"
                self.Keep_Cell_evapotranspiration.UseVisualStyleBackColor = True
                self.Keep_Cell_evapotranspiration.CheckState = CheckState.Checked


#6
                #< Page object>  Keep_recharge CheckBox
                # 
                self.Keep_recharge.Location = Point(12, 175)
                self.Keep_recharge.Size = Drawing.Size(304, 24)
                self.Keep_recharge.Text = "Recharge of the Cell(recharge)"
                self.Keep_recharge.UseVisualStyleBackColor = True             
                self.Keep_recharge.CheckState = CheckState.Checked


#7

                #< Page object>  Keep_barerunoff CheckBox
                # 
                self.Keep_barerunoff.Location = Point(12, 200)
                self.Keep_barerunoff.Size = Drawing.Size(304, 24)
                self.Keep_barerunoff.Text = "Runoff of Bare Soil(barerunoff)"
                self.Keep_barerunoff.UseVisualStyleBackColor = True

#8

                #< Page object>  Keep_imperrunoff CheckBox
                # 
                self.Keep_imperrunoff.Location = Point(12, 225)
                self.Keep_imperrunoff.Size = Drawing.Size(304, 24)
                self.Keep_imperrunoff.Text = "Runoff of Impervious Area (imperrunoff)"
                self.Keep_imperrunoff.UseVisualStyleBackColor = True

#9

                #< Page object>  Keep_owrunoff CheckBox
                # 
                self.Keep_owrunoff.Location = Point(12, 250)
                self.Keep_owrunoff.Size = Drawing.Size(304, 24)
                self.Keep_owrunoff.Text = "Runoff on Open Water (owrunoff)"
                self.Keep_owrunoff.UseVisualStyleBackColor = True                
                


#10

                #< Page object>  Keep_Cell_actualtranspiration CheckBox
                # 
                self.Keep_Cell_actualtranspiration.Location = Point(12, 275)
                self.Keep_Cell_actualtranspiration.Size = Drawing.Size(304, 24)
                self.Keep_Cell_actualtranspiration.Text = "Total Actual Transpiration of Pixel (Cell_actualtranspiration)"
                self.Keep_Cell_actualtranspiration.UseVisualStyleBackColor = True

#11

                #< Page object>  Keep_Cell_actual_baresoil_evapo CheckBox
                # 
                self.Keep_Cell_actual_baresoil_evapo.Location = Point(12, 300)
                self.Keep_Cell_actual_baresoil_evapo.Size = Drawing.Size(304, 24)
                self.Keep_Cell_actual_baresoil_evapo.Text = "Evaporation from Bare Soil (Cell_actual_baresoil_evapo)"
                self.Keep_Cell_actual_baresoil_evapo.UseVisualStyleBackColor = True

#12

                #< Page object>  Keep_Cell_ow_evaporation CheckBox
                # 
                self.Keep_Cell_ow_evaporation.Location = Point(12, 325)
                self.Keep_Cell_ow_evaporation.Size = Drawing.Size(304, 24)
                self.Keep_Cell_ow_evaporation.Text = "Evaporation from Open Water (Cell_ow_evaporation)"
                self.Keep_Cell_ow_evaporation.UseVisualStyleBackColor = True

#13


                #< Page object>  Keep_Cell_imper_evaporation CheckBox
                # 
                self.Keep_Cell_imper_evaporation.Location = Point(12, 350)
                self.Keep_Cell_imper_evaporation.Size = Drawing.Size(304, 24)
                self.Keep_Cell_imper_evaporation.Text = "Evaporation from Impervious Surface (imper_evaporation)"
                self.Keep_Cell_imper_evaporation.UseVisualStyleBackColor = True

#14


                #< Page object>  Keep_Cell_gw_transpiration CheckBox
                # 
                self.Keep_Cell_gw_transpiration.Location = Point(12, 375)
                self.Keep_Cell_gw_transpiration.Size = Drawing.Size(304, 24)
                self.Keep_Cell_gw_transpiration.Text = "Groundwater Transpiration (gw_transpiration)"
                self.Keep_Cell_gw_transpiration.UseVisualStyleBackColor = True                

#15


                #< Page object>  Keep_Cell_gw_evaporation CheckBox
                # 
                self.Keep_Cell_gw_evaporation.Location = Point(340, 50)
                self.Keep_Cell_gw_evaporation.Size = Drawing.Size(304, 24)
                self.Keep_Cell_gw_evaporation.Text = "Groundwater Evaporation(gw_evaporation)"
                self.Keep_Cell_gw_evaporation.UseVisualStyleBackColor = True
#16


                #< Page object>  Keep_soilwater_storage CheckBox
                # 
                self.Keep_soilwater_storage.Location = Point(340, 75)
                self.Keep_soilwater_storage.Size = Drawing.Size(304, 24)
                self.Keep_soilwater_storage.Text = "Soil-Water Storage (soilwater_storage)"
                self.Keep_soilwater_storage.UseVisualStyleBackColor = True

#17

                #< Page object>  Keep_penmann_coefficient CheckBox
                # 
                self.Keep_penmann_coefficient.Location = Point(340, 100)
                self.Keep_penmann_coefficient.Size = Drawing.Size(304, 24)
                self.Keep_penmann_coefficient.Text = "Penmann Coefficient (penmann_coefficient)"
                self.Keep_penmann_coefficient.UseVisualStyleBackColor = True
#18

                #< Page object>  Keep_total_Interception CheckBox
                # 
                self.Keep_total_Interception.Location = Point(340, 125)
                self.Keep_total_Interception.Size = Drawing.Size(304, 24)
                self.Keep_total_Interception.Text = "Total Interception (total_Interception)"
                self.Keep_total_Interception.UseVisualStyleBackColor = True

                
                
                
                
                
                
                # 
                #< Page object>  aboutPage
                # 
                self.aboutPage.Controls.Add(self.labelworkindir3)
                self.aboutPage.Controls.Add(self.labelworkindir2)
                self.aboutPage.Controls.Add(self.labelworkindir1)
                self.aboutPage.Location = Point(4, 22)
                self.aboutPage.Name = "aboutPage"
                self.aboutPage.Padding = Padding(3)
                self.aboutPage.Size = Drawing.Size(688, 408)
                self.aboutPage.Text = "About"
                self.aboutPage.UseVisualStyleBackColor = True
                # 
                
   
                #< Page object>  ParamPage
                # 
                
                self.ParamPage.Location = Point(4, 22)
                self.ParamPage.Name = "ParamPage"
                self.ParamPage.Padding = Padding(3)
                self.ParamPage.Size = Drawing.Size(688, 408)
                self.ParamPage.Text = "Parameters"
                self.ParamPage.UseVisualStyleBackColor = True
                # 

                
                #< Page object>  CalibPage
                # 
                
                self.CalibPage.Location = Point(4, 22)
                self.CalibPage.Name = "CalibPage"
                self.CalibPage.Padding = Padding(3)
                self.CalibPage.Size = Drawing.Size(688, 408)
                self.CalibPage.Text = "Calibration"
                self.CalibPage.UseVisualStyleBackColor = True
                # 
                                
                
                #< Page object>  labelworkindir1
                # 
                self.labelworkindir1.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.labelworkindir1.Location = Point(9, 7)
                self.labelworkindir1.Name = "labelworkindir1"
                self.labelworkindir1.Size = Drawing.Size(100, 23)
                self.labelworkindir1.Text = "WetSpass:"
                # 
                #< Page object>  labelworkindir2
                # 
                self.labelworkindir2.Location = Point(8, 39)
                self.labelworkindir2.Name = "labelworkindir2"
                self.labelworkindir2.Size = Drawing.Size(642, 94)
                self.labelworkindir2.Text = "WetSpass is a long term spatially distributed water balance model for simulating groundwater recharge, soil water storage, evapotranspiration (soil evaporation and transpiration also as separate outputs), runoff and Interception using climate input on monthly, seasonal and annual scale. The user will have output on same temporal scale as for the input, and is required to give input maps as ESRI-ascii grid files through Graphical User Interface (GUI). The landuse and soil parameters can be modified within the interface without opening the lookup tables. A sample data has been provided in the local installation folder of user computer system to familiarise and demonstrate the model features. Further details of the model can be found in the manual. The model has been applied satisfactorily in different areas in Belgium and several other locations." 
                # 
                #< Page object>  labelworkindir3
                # 
                self.labelworkindir3.Location = Point(9, 144)
                self.labelworkindir3.Name = "labelworkindir3"
                self.labelworkindir3.Size = Drawing.Size(642, 127)
                self.labelworkindir3.Text = "The WetSpass model and its interface are freely available upon request for ACADEMIC USE. With academic use, it is implied for use by the students for course or thesis work and use by researchers for academic purposes. For other purposes or in case of doubt permission should be obtained from kabdolla@vub.ac.be and imtiaz.bashir@vub.ac.be. Use of WetSpass has to be acknowledged in reports, conference proceedings and journal papers, etc., giving co-authorship to the followings: K. Abdollahi, Bashir, I., Batelaan, O. At Vrije Universiteit Brussels, Belgium."
                # 
                #< Page object>  butOutDir
                # 
                self.butOutDir.Location = Point(613, 23)
                self.butOutDir.Name = "butOutDir"
                self.butOutDir.Click += self.butOutDirClick
                self.butOutDir.Size = Drawing.Size(30, 23)
                self.butOutDir.Text = "..."
                self.butOutDir.UseVisualStyleBackColor = True
                # 
                #< Page object>  label3
                # 
                  
                self.label3.Font = Drawing.Font("Microsoft Sans Serif", 9, Drawing.FontStyle.Bold, Drawing.GraphicsUnit.Point, 0)
                self.label3.Location = Point(3, 25)
                self.label3.Name = "label3"
                self.label3.Size = Drawing.Size(120, 23)
                self.label3.Text = "Ouput Directory:"
                # 
                #< Page object>  Tboxotputdir
                # 
                self.Tboxotputdir.Location = Point(125, 25)
                self.Tboxotputdir.Name = "Tboxotputdir"
                self.Tboxotputdir.Size = Drawing.Size(485, 20)
               
               #< Page object>  TxtSimulations
                # 
                self.TxtSimulations.Location = Point(515, 130)
                self.TxtSimulations.Name = "Tboxotputdir"
                self.TxtSimulations.Size = Drawing.Size(90, 20)
                self.TxtSimulations.Text="Simulated.tbl"
                # 

                #< Page object>  checFracFromDir
                # 
                self.checFracFromDir.Location = Point(125, 75)
                self.checFracFromDir.Name = "checFracFromDir"
                self.checFracFromDir.Size = Drawing.Size(330, 20)
                self.checFracFromDir.Text = "Read fractions from provided Fractions in '..\inputs\Fractions' folder."
                self.checFracFromDir.UseVisualStyleBackColor = True
                self.checFracFromDir.CheckedChanged += self.ClickcheckFrac
                # 
                #< Page object>  checAddIrrig
                # 
                self.checAddIrrig.Location = Point(125, 50)
                self.checAddIrrig.Name = "checAddIrrig"
                self.checAddIrrig.Size = Drawing.Size(330, 20)
                self.checAddIrrig.Text = "Add irrigated water to rainfall from '..\inputs\maps\irrigation' folder."
                self.checAddIrrig.CheckedChanged += self.ClickcheckIrrg
                #                 
                #< Page object>  checkPenman
                # 
                self.checkPenman.Location = Point(125, 120)
                self.checkPenman.Name = "checkPenman"
                self.checkPenman.Size = Drawing.Size(650, 24)
                self.checkPenman.Text = "For all time steps, calculate ETP using Penman-Monteith if the map is missing."
                self.checkPenman.UseVisualStyleBackColor = True
                self.checkPenman.Enabled= False
                # 

                #< Page object>  checkSimulations
                # 
                self.checkSimulations.Location = Point(125, 100)
                self.checkSimulations.Name = "checkSimulations"
                self.checkSimulations.Size = Drawing.Size(390, 20)
                self.checkSimulations.Text = "Create a simulation file for calibration with the provided name in the box:"
                self.checkSimulations.CheckState = CheckState.Checked
                self.checkSimulations.UseVisualStyleBackColor = True
                self.checkSimulations.CheckedChanged += self.ClickcheckSim
                # 
                #< Page object>  checIncludSnow
                # 
                self.checIncludSnow.Location = Point(125, 160)
                self.checIncludSnow.Name = "checIncludSnow"
                self.checIncludSnow.Size = Drawing.Size(330, 20)
                self.checIncludSnow.Text = "Include snow processes in the modelling"
                self.checIncludSnow.CheckedChanged += self.ClickcheckSnow
                #< Page object>  labellanduse
                # 
        
                # 
                # WetSpassMainPage
                # 
                self.ClientSize = Drawing.Size(696, 434)
                #Pages.Parent = self
                self.Controls.Add(self.Pages)
                self.Name = "WetSpassMainPage"
                self.Text = "WetSpass"
                self.Pages.ResumeLayout(False)
                self.inputPage.ResumeLayout(False)
                self.inputPage.PerformLayout()
                self.optionPage.ResumeLayout(False)
                self.optionPage.PerformLayout()
                self.runPage.ResumeLayout(False)
                self.runPage.PerformLayout()
                self.aboutPage.ResumeLayout(False)
                self.ParamPage.ResumeLayout(False)
                self.ResumeLayout(False)
                #Load defualt values to page             
                self.TboxPrefixLAI.Text="lai"
                self.TboxPrefixrainfall.Text="rain"
                self.TboxPrefixPET.Text="pet"
                self.TboxPrefixTemperature.Text="temp"
                self.TboxWind.Text="wind"
                self.Tboxgwdepth.Text="gwdepth"
                self.Tboxsnowcover.Text="snowcover"
                self.TboxPrefixIrrigatedArea.Text="irrig"
                self.Tboxnodata.Text="-9999" 
                self.TxtFirstStepNo.Text="1"
                         
                 
                # landuse lookupEditorPage
                # 

                self.lookupEditorPage.Name = "lookupEditorPage"
                self.lookupEditorPage.Padding = Padding(3)
                self.lookupEditorPage.Text = "Table Editor"
                self.lookupEditorPage.UseVisualStyleBackColor = True
                # 
                self.labellookup1 = Label()
                self.labellookup1.Name = "labellookup1"
                self.labellookup1.Text= "You may modify predefined lookup values of Wetspass model which used  to replace the runtime computation. Also, you can edit and make changes on the table elements of any kind of TBL and CSV tables."+ "\n" +"As it has been predefined edited table must be saved with '*.tbl' extension  in '~\\inputs\\tables\\' path; which '~' stands for working directory." 

                self.labellookup1.Size =  Drawing.Size(550, 75);
                self.labellookup1.Location = Point(10, 30)
                self.labellookup1.Dock = DockStyle.Top
     
                # linkOpen
                #
                self.linkOpen = LinkLabel()
                self.linkOpen.Location = Point(10, 55);
                self.linkOpen.Name = "linkOpen";
                self.linkOpen.Size =  Drawing.Size(66, 23);
                self.linkOpen.Text = "Open";
                self.linkOpen.Click += self.LinkOpenLinkClicked;
                # 
                # linkSave
                #
                self.linkSave = LinkLabel()
                self.linkSave.Location =  Point(90, 55);
                self.linkSave.Name = "linkSave";
                self.linkSave.TabStop = True;
                self.linkSave.Text = "Save";
                self.linkSave.Click += self.LinkSaveLinkClicked;
                self.linkSave.Enabled =False
                #	// 


                #
                # look up sheet for landuse
                # 		

                #sheettable1
                self.sheettable1 = DataViewer();
                self.sheettable1.AllowDrop = True;
                self.sheettable1.AllowUserToAddRows = True;
                self.sheettable1.AllowUserToDeleteRows = True;
                self.sheettable1.AllowUserToOrderColumns = False;
                self.sheettable1.AllowUserToResizeColumns = True;
                self.sheettable1.AllowUserToResizeRows = True;
                self.sheettable1.EditMode = DataGridViewEditMode.EditOnEnter;
                self.sheettable1.EnableHeadersVisualStyles = True;
                self.sheettable1.FirstDisplayedScrollingColumnIndex = 0;
                self.sheettable1.FirstDisplayedScrollingRowIndex = 0;
                self.sheettable1.GridColor = Color.LightGray;
                self.sheettable1.Name = "sheettable1";
                self.sheettable1.RowCount = 2;
                self.sheettable1.RowHeadersBorderStyle = DataGridViewHeaderBorderStyle.Raised;
                self.sheettable1.ScrollBars = ScrollBars.Both;
                self.sheettable1.SelectionMode = DataGridViewSelectionMode.RowHeaderSelect;
                self.sheettable1.ShowCellErrors = True;
                self.sheettable1.ShowCellToolTips = True;
                self.sheettable1.ShowEditingIcon = True;
                self.sheettable1.ShowRowErrors = True;
                self.sheettable1.Size =  Drawing.Size(315, 198);
                self.sheettable1.VirtualMode = False;
                self.sheettable1.Dock = DockStyle.Fill
                self.lookupEditorPage.Controls.Add(self.sheettable1)
                
                self.lookupEditorPage.Controls.Add(self.linkOpen)
                self.lookupEditorPage.Controls.Add(self.linkSave)
                self.lookupEditorPage.Controls.Add(self.labellookup1)
                
                # load headers
                self.sheettable1.ColumnCount=21
                #IO.Path.GetFileNameWithoutExtension( Application.ExecutablePath)  
                Filepathland=rootpath +"\\Landuses.TBL"
                #self.sheettable1.loadcsv( Filepathland ,  "\t")
              
                

                     
               
               
                              
             
#===============End of pages======================                
#Push all content of pages into MainForm                   
                self.Controls.Add(self.Pages)    
                # And finally what is MainForm
                # 
                self.Size = Size(720, 480)
                self.allowclose=0
                self.MinimizeBox = 1
                self.ShowInTakbar = 0
                self.FormBorderStyle = FormBorderStyle.Sizable
                self.GetStayOnTop = 1 
                     
                self.Icon= Icon(rootpath+IO.Path.GetFileNameWithoutExtension( Application.ExecutablePath)+".ico")
                self.Name = "WetSpassMainPage"
                self.Text = "WetSpass-M 1.2"
                self.Pages.ResumeLayout(False)
                self.inputPage.ResumeLayout(False)
                self.inputPage.PerformLayout()
                self.optionPage.ResumeLayout(False)
                self.optionPage.PerformLayout()
                self.runPage.ResumeLayout(False)
                self.runPage.PerformLayout()
                self.aboutPage.ResumeLayout(False)
                self.ParamPage.ResumeLayout(False)
                self.ParamPage.PerformLayout()
                self.ResumeLayout(False)
                self.FormClosing+=self.CloseModel
                self.FormClosed+=self.finalizClose
                self.FormBorderStyle = FormBorderStyle.FixedSingle;
WetSpassPage=WetSpassMainPage.Model().Show()
#WetSpassPage.Show()
