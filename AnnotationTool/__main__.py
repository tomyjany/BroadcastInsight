import argparse
import sys
from PyQt5.QtWidgets import QApplication
from AnnotationTool.annotation_view import AnnotationView

import os, pathlib, PyQt5
_qt = pathlib.Path(PyQt5.__file__).parent / 'Qt5'
os.environ['LD_LIBRARY_PATH']       = str(_qt / 'lib') + ':' + os.environ.get('LD_LIBRARY_PATH', '')
os.environ['QT_PLUGIN_PATH']        = str(_qt / 'plugins')
os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH', None)   # throw away stale overrides

def main():
    parser = argparse.ArgumentParser(description="Input file")
    parser.add_argument(
        "input_file", type=str, help="Name of the agent used to mine data"
    )
    args = parser.parse_args()
    input_file = args.input_file

    app = QApplication(sys.argv)

    window = AnnotationView(input_file)
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
