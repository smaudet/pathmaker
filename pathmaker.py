#!python
#pylint: disable=C0330,C0111,C0103,R0902,R0904,W0311,W0703,W0613,W0612

import os
import sys
from win32com.shell import shell
import win32api, win32con  # lint:ok
import tempfile
ASADMIN = 'asadmin'


is_admin = False
was_admin = False
try:
  is_admin = sys.argv[-1] == ASADMIN
except IndexError as e:
  pass

#if we were given admin rights by e.g. sudo or a UAC manifest
if not is_admin:
  import ctypes
  try:
    is_admin = os.getuid() == 0
  except AttributeError:
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
  was_admin = is_admin

#attempt to run the script as an admin
if not is_admin:
  print "running routine"
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

  params = ' '.join([script] + sys.argv[1:] + [name, ASADMIN])
  #re-run the script as admin
  #force a write of the relevant variable exports

  res = shell.ShellExecuteEx(
    lpVerb='runas'
    , lpFile=sys.executable
    , lpParameters=params
    , nShow=showCmd
  )
  f = open('path.log', 'w')
  f.write(sys.executable)
  f.flush()

  f.write(params)

  f.close()

#  print sys.executable
#  print params

  print "exit admin runner"
  sys.exit(0)

if not was_admin:
  fname = sys.argv[-2]
  f = open(sys.argv[-2])
  pathStr = f.readline()
  pkgStr = f.readline()
  win32api.SetEnvironmentVariable('PATH', pathStr)
  win32api.SetEnvironmentVariable('PKG_CONFIG_PATH', pkgStr)
  os.environ['path'] = pathStr
  os.environ['pkgStr'] = pkgStr
  f.close()

  try:
    os.remove(fname)
  except NameError as e:
    print e
  except Exception as e:
    print "unknown error", e

try:
  import pygtk
  pygtk.require("2.0")
except Exception as e:
  sys.exit(1)

try:
  import gtk
except Exception as e:
  sys.exit(1)

  #from win32env import Win32Environment as Win32Env
import _winreg as winreg

class pathmaker(object):

  def __init__(self):
    self.gladefile = "./pathmaker.glade"

    self.b = gtk.Builder()
    self.b.add_from_file(self.gladefile)

    #self.lst = self.b.get_object("userVarsData")

    self.window = self.b.get_object("pathmakerWindow")

    varUserView = self.b.get_object("userVarsView")
    userSel = varUserView.get_selection()
    userSel.set_mode(gtk.SELECTION_MULTIPLE)
    userSel.set_select_function(self.handleSelect, full=True)
    varUserModel = self.b.get_object("userVarsData")
    varSysView = self.b.get_object("sysVarsView")
    sysSel = varSysView.get_selection()
    sysSel.set_mode(gtk.SELECTION_MULTIPLE)
    sysSel.set_select_function(self.handleSelect, full=True)
    varSysModel = self.b.get_object("sysVarsData")
    varUserModel.clear()
    varSysModel.clear()

    self.userKey = winreg.OpenKey(
      winreg.HKEY_CURRENT_USER,
      'Environment',
      0,
      winreg.KEY_ALL_ACCESS)
    self.sysKey = winreg.OpenKey(
      winreg.HKEY_LOCAL_MACHINE,
      r'SYSTEM\CurrentControlSet\Control\Session Manager\Environment',
      0,
      winreg.KEY_ALL_ACCESS)


    self.setupModel(varUserModel, self.userKey)
    self.setupModel(varSysModel, self.sysKey)

    varUserView.set_model(varUserModel)
    varSysView.set_model(varSysModel)

    self.varUserModel = varUserModel
    self.varSysModel = varSysModel

    self.popup = self.b.get_object("itempopup")
    self.wasRightClick = {}
    self.wasRightClick[varUserView] = False
    self.wasRightClick[varSysView] = False

    self.b.connect_signals(self)

    self.window.show_all()
    self.cur_sel = (None, None)
    #for the text entry at the bottom
    self.userVar = ""
    self.sysVar = ""
    self.userVal = ""
    self.sysVal = ""

  def handleSelect(self, selection, model, path, is_selected):
    if is_selected:
      if self.wasRightClick[selection.get_tree_view()]:
        return False
    return True

  def setupModel(self, model, key):
    (keys, vals, j) = winreg.QueryInfoKey(key)
    try:
      for i in range(0, vals):
        (name, value, t) = winreg.EnumValue(key, i)
        model.append((name, value))
    except Exception as e:
      print e

  def on_deleteAction_activate(self, ev):
    (model, paths) = self.cur_sel
    print paths
    rows = []
    for path in paths:
      rows.append(gtk.TreeRowReference(model, path))
    for row in rows:
      model.remove(model.get_iter(row.get_path()))

  def pathmakerWindow_destroy(self, ev):
    winreg.FlushKey(self.userKey)
    winreg.FlushKey(self.sysKey)
    winreg.CloseKey(self.userKey)
    winreg.CloseKey(self.sysKey)
    gtk.main_quit()

  def userVarEntry_changed_cb(self, entry):
    #print "userVar"
    self.userVar = entry.get_chars(0, -1)

  def userValEntry_changed_cb(self, entry):
    #print "userVal"
    self.userVal = entry.get_chars(0, -1)

  def sysVarEntry_changed_cb(self, entry):
    #print "sysVar"
    self.sysVar = entry.get_chars(0, -1)

  def sysValEntry_changed_cb(self, entry):
    #print "sysVal"
    self.sysVal = entry.get_chars(0, -1)

  def handleUserCreate(self, btn):
    self.addVar(self.userVar,
                self.userVal,
                self.varUserModel,
                self.userKey)

  def handleSysCreate(self, btn):
    self.addVar(self.sysVar,
                self.sysVal,
                self.varSysModel,
                self.sysKey)

  #add var to set
  def addVar(self, varName, val, model, key):
    if self.notExists(key, varName):
      model.append((varName, val))
      winreg.SetValueEx(key, varName, None, winreg.REG_SZ, val)
      winreg.FlushKey(key)

  def notExists(self, key, varName):
    try:
      (val, t) = winreg.QueryValueEx(key, varName)
      return val == None
    except Exception as e:
      print e
      return True

  def on_textcell_editing_canceled(self, cell):
    pass

  def on_textcell_editing_started(self, cell, editable, path):
    pass

  def on_textcell_userVar_edited(self, cell, path, new_text):
    if self.notExists(self.userKey, new_text):
      itr = self.varUserModel.get_iter_from_string(path)
      old = self.varUserModel.get(itr, 0)[0]
      self.varUserModel.set(itr, 0, new_text)
      self.setVarName(self.userKey, old, new_text)
      print new_text
    else:
      print "failed to set new value, key already exists"

  def on_textcell_userVal_edited(self, cell, path, new_text):
    itr = self.varUserModel.get_iter_from_string(path)
    self.varUserModel.set(itr, 1, new_text)
    varName = self.varUserModel.get(itr, 0)[0]
    self.setVarVal(self.userKey, varName, new_text)
    print new_text

  def on_textcell_sysVar_edited(self, cell, path, new_text):
    if self.notExists(self.sysKey, new_text):
      itr = self.varSysModel.get_iter_from_string(path)
      old = self.varSysModel.get(itr, 0)[0]
      self.varSysModel.set(itr, 0, new_text)
      self.setVarName(self.sysKey, old, new_text)
      print new_text
    else:
      print "failed to set new value, key already exists"

  def on_textcell_sysVal_edited(self, cell, path, new_text):
    itr = self.varSysModel.get_iter_from_string(path)
    self.varSysModel.set(itr, 0, new_text)
    varName = self.varUserModel.get(itr, 0)[0]
    self.setVarVal(self.sysKey, varName, new_text)
    print new_text

  def setVarName(self, key, old, name):
    #get old data
    (data, t) = winreg.QueryValueEx(key, old)
    #set new value, if there are no conflicts
    winreg.SetValueEx(key, name, None, t, data)
    #delete old value
    winreg.DeleteValue(key, old)

  def setVarVal(self, key, varName, val):
    print varName
    (oldVal, t) = winreg.QueryValueEx(key,varName)
    winreg.SetValueEx(key,varName,None,t,val)
  
  def on_list_button_press_event(self, treeview, event):
    self.wasRightClick[treeview] = False
    if event.button == 3:
      self.wasRightClick[treeview] = True
      x = int(event.x)
      y = int(event.y)
      time = event.time
      pthinfo = treeview.get_path_at_pos(x, y)
      if pthinfo is not None:
        path, col, cellx, celly = pthinfo
        treeview.grab_focus()
        treeview.set_cursor(path, col, 0)
        self.popup.popup(None, None, None, event.button, time)
        return False

  def on_list_button_release(self, treeview, event):
    if event.button == 1:
      self.cur_sel = treeview.get_selection().get_selected_rows()

  def on_saveAction_activate(self):
    pass

  def on_duplicateAction_activate(self):
    pass


if __name__ == "__main__":

  # enable threading
  gtk.threads_init()
  gtk.threads_enter()
  hw = pathmaker()
  gtk.main()
  # cleanup
  gtk.threads_leave()

