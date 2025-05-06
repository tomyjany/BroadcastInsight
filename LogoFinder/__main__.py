from LogoFinder.LogoFinder import LogoFinder
from matplotlib import pyplot as plt


def main():
    paths = ["LogoFinder/example1.jpg", "LogoFinder/example2.jpg"]
    finder = LogoFinder()

    for img_path in paths:
        logo = finder.find_logo(img_path)
        logo.show()


if __name__ == "__main__":
    main()
