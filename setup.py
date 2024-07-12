from setuptools import setup

setup(
    name="OctoPrint-PrintClogDetection",
    version="0.1",
    description="clogging detection",
    author="bravelyan",
    author_email="bravelyan.edgarin@gmail.com",
    url="https://github.com/Bravelyan/my-plugin",
    packages=["octoprint_printclogdetection"],
    install_requires=["octoprint", "opencv-python", "numpy"],
    entry_points={
        "octoprint.plugin": ["printclogdetection = octoprint_printclogdetection"]
    },
)
