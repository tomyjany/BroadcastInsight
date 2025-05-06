from PeopleFinder.GUI.run import run
from PeopleFinder.finder import load_people_from_database, test_on_test_image

import os, pathlib, PyQt5
_qt = pathlib.Path(PyQt5.__file__).parent / 'Qt5'
os.environ['LD_LIBRARY_PATH']       = str(_qt / 'lib') + ':' + os.environ.get('LD_LIBRARY_PATH', '')
os.environ['QT_PLUGIN_PATH']        = str(_qt / 'plugins')
os.environ.pop('QT_QPA_PLATFORM_PLUGIN_PATH', None)   # throw away stale overrides
if __name__ == "__main__":
    # people = load_people_from_database("PeopleFinder/People/database")
    # for person in people:
    #     print(person.name_czech, str(person.encoding)[:10])
    # test_on_test_image()
    run()
