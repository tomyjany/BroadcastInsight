import sys
import os, pathlib, PyQt5
_qt = pathlib.Path(PyQt5.__file__).parent / 'Qt5'
os.environ['LD_LIBRARY_PATH']       = str(_qt / 'lib') + ':' + os.environ.get('LD_LIBRARY_PATH', '')
os.environ['QT_PLUGIN_PATH']        = str(_qt / 'plugins')
os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH', None)   # throw away stale overrides

from PyQt5.QtWidgets import QApplication

# from Annocr.components.main_window import MainWindow
from Annocr.components.main_window import MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
