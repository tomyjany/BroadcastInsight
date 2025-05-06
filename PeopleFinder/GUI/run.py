import sys
from PyQt5.QtWidgets import QApplication
from PeopleFinder.GUI.people_finder_view import PeopleFinderView


def run():
    print("Starting People Finder application...")
    app = QApplication(sys.argv)
    window = PeopleFinderView()
    window.show()
    print("People Finder application is now running.")
    sys.exit(app.exec_())


if __name__ == "__main__":
    run()
