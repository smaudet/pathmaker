#!python

 # ...
 # ModuleFinder can't handle runtime changes to __path__, but win32com uses them
try:
  # py2exe 0.6.4 introduced a replacement modulefinder.
  # This means we have to add package paths there, not to the built-in
  # one.  If this new modulefinder gets integrated into Python, then
  # we might be able to revert this some day.
  # if this doesn't work, try import modulefinder
  try:
    import py2exe.mf as modulefinder
  except ImportError:
    import modulefinder
  import win32com, sys
  for p in win32com.__path__[1:]:
    print p
    modulefinder.AddPackagePath("win32com", p)
  for extra in ["win32com.shell"]: #,"win32com.mapi"
    __import__(extra)
    m = sys.modules[extra]
    for p in m.__path__[1:]:
      modulefinder.AddPackagePath(extra, p)
except ImportError:
  # no build path setup, no worries.
  pass

from distutils.core import setup
import py2exe

# Find GTK+ installation path
__import__('gtk')
m = sys.modules['gtk']
gtk_base_path = m.__path__[0]

setup(
  name="pathmaker"
  ,version='0.1'
  ,windows=[ {
    'script' : 'pathmaker.py',
    'uac_info' : "requireAdministrator"
  }]
  ,options={
    'py2exe':{
      'packages':'encodings',
      'includes':'cairo, pango, pangocairo, atk, gobject, gio, gtk.keysyms'
    }
  }
  ,data_files=[
    'pathmaker.glade'
  ]
)
