#!python

import os
import sys
import win32com.shell.shell as shell
import win32api,win32con
# import win32api, win32process
import subprocess
import tempfile
from time import sleep
ASADMIN = 'asadmin'

if sys.argv[-1] != ASADMIN:
  #find the current python script
  script = os.path.abspath(sys.argv[0])
  #re-create its argument list
  pathStr = win32api.GetEnvironmentVariable('PATH')
  pkgStr = win32api.GetEnvironmentVariable('PKG_CONFIG_PATH')
  f = tempfile.NamedTemporaryFile(delete=False)
  name = f.name
  f.write(pathStr+"\n")
  f.write(pkgStr+"\n")
  f.close()
  showCmd = win32con.SW_SHOWNORMAL

  params = ' '.join([script] + sys.argv[1:] + [name,ASADMIN])
  #re-run the script as admin
  #force a write of the relevant variable exports
  
  res = shell.ShellExecuteEx(nShow=showCmd,lpVerb='runas', lpFile=sys.executable, lpParameters=params)
#  print sys.executable
#  print params
#  for k in res:
#    print k,res[k]
  
  sys.exit(0)

fname = sys.argv[-2]
f = open(sys.argv[-2])
pathStr = f.readline()
pkgStr = f.readline()
win32api.SetEnvironmentVariable('PATH',pathStr)
win32api.SetEnvironmentVariable('PKG_CONFIG_PATH',pkgStr)
os.environ['path']=pathStr
os.environ['pkgStr']=pkgStr
f.close()
try:
  os.remove(fname)
except Exception as e:
  print e

try:
  import pygtk
  pygtk.require("2.0")
except:
  print "failed to load pygtk"

try:

  import gtk
  import gtk.glade
except:
  sys.exit(1)

  #from win32env import Win32Environment as Win32Env
import _winreg as winreg

class pathmaker:

  def __init__(self):
    self.gladefile="./pathmaker.glade"

    self.b = gtk.Builder()
    self.b.add_from_file(self.gladefile)

    #self.lst = self.b.get_object("userVarsData")
    
    self.window = self.b.get_object("pathmakerWindow")
    varUserView = self.b.get_object("userVarsView")
    varUserModel = self.b.get_object("userVarsData")
    varSysView = self.b.get_object("sysVarsView")
    varSysModel = self.b.get_object("sysVarsData")
    varUserModel.clear()
    varSysModel.clear()

    self.userKey = winreg.OpenKey(winreg.HKEY_CURRENT_USER,'Environment',0,winreg.KEY_ALL_ACCESS)
    self.sysKey = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',0,winreg.KEY_ALL_ACCESS)
    
    
    self.setupModel(varUserModel,self.userKey)
    self.setupModel(varSysModel,self.sysKey)

    varUserView.set_model(varUserModel)
    varSysView.set_model(varSysModel)

    self.varUserModel = varUserModel
    self.varSysModel = varSysModel

    self.window.show_all()

    self.b.connect_signals(self)

  def setupModel(self,model,key):
    (keys,vals,j) = winreg.QueryInfoKey(key)
    try:
      for i in range(0,vals):
        (name,value,t) = winreg.EnumValue(key,i)
        model.append((name,value))
    except Exception as e:
      print e

  def pathmakerWindow_destroy(self,ev):
    winreg.FlushKey(self.userKey)
    winreg.FlushKey(self.sysKey)
    winreg.CloseKey(self.userKey)
    winreg.CloseKey(self.sysKey)
    gtk.main_quit()
    
  def userVarEntry_changed_cb(self,entry):
    #print "userVar"
    self.userVar = entry.get_chars(0,-1)

  def userValEntry_changed_cb(self,entry):
    #print "userVal"
    self.userVal = entry.get_chars(0,-1)

  def sysVarEntry_changed_cb(self,entry):
    #print "sysVar"
    self.sysVar = entry.get_chars(0,-1)

  def sysValEntry_changed_cb(self,entry):
    #print "sysVal"
    self.sysVal = entry.get_chars(0,-1)
    
  def handleUserCreate(self,btn):
    print "user"
    self.addVar(self.userVar,self.userVal,self.varUserModel,self.userKey)

  def handleSysCreate(self,btn):
    print "sys"
    self.addVar(self.sysVar,self.sysVal,self.varSysModel,self.sysKey)
    
  #add var to set
  def addVar(self,varName,val,model,key):
    if(self.notExists(key,varName)):
      model.append((varName,val))
      winreg.SetValueEx(key,varName,None,winreg.REG_SZ,val)
      winreg.FlushKey(key)

  def notExists(self,key,varName):
    print varName
    print key
    try:
      (val,t) = winreg.QueryValueEx(key,varName)
      return val == None
    except Exception as e:
      print e
      return True

  def on_textcell_editing_canceled(self,cell):
    print "cancel"

  def on_textcell_editing_started(self,cell,editable,path):
    print "start"

  def on_textcell_userVar_edited(self,cell,path,new_text):
    if(self.notExists(self.userKey,new_text)):
      itr = self.varUserModel.get_iter_from_string(path)
      old = self.varUserModel.get(itr,0)[0]
      self.varUserModel.set(itr,0,new_text)
      self.setVarName(self.userKey,old,new_text)
      print new_text
    else:
      print "failed to set new value, key already exists"

  def on_textcell_userVal_edited(self,cell,path,new_text):
    itr = self.varUserModel.get_iter_from_string(path)
    self.varUserModel.set(itr,1,new_text)
    varName = self.varUserModel.get(iter,0)
    self.setUserVal(varName,new_text)
    print new_text

  def on_textcell_sysVar_edited(self,cell,path,new_text):
    if(self.notExists(self.sysKey,new_text)):
      itr = self.varSysModel.get_iter_from_string(path)
      old = self.varSysModel.get(itr,0)[0]
      self.varSysModel.set(itr,0,new_text)
      self.setVarName(self.sysKey,old,new_text)
      print new_text
    else:
      print "failed to set new value, key already exists"

  def on_textcell_sysVal_edited(self,cell,path,new_text):
    itr = self.varSysModel.get_iter_from_string(path)
    self.varSysModel.set(itr,0,new_text)
    varName = self.varUserModel.get(iter,0)
    self.setUserVal(varName,new_text)
    print new_text

  def setVarName(self,key,old,name):
    #get old data
    (data,t)=winreg.QueryValueEx(key,old)
    #set new value, if there are no conflicts
    winreg.SetValueEx(key,name,None,t,data)
    #delete old value
    winreg.DeleteValue(key,old)
    
    
    
if __name__ == "__main__":
  hw = pathmaker()
  gtk.main()
  print "done"
  
