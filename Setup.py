import cx_Freeze

executables = [cx_Freeze.Executable('ListenNow - App.pyw', icon='View/QRC/logo.ico', base='Win32GUI')]

cx_Freeze.setup(
    name="ListenNow",
    options={'build_exe': {'packages': ['PyQt5.QtCore', 'PyQt5.QtGui', 'PyQt5.QtWidgets', 'youtube_dl', 'pygame', 'sys', 'os', 'shutil', 'eyed3', 'tkinter', 'pytube', 'moviepy'],
                           'include_files': ['View/', 'bank_music']}},
    executables=executables
)