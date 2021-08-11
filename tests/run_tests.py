import argparse
import os
import platform
import shutil
import subprocess
import tempfile
import uuid

ROOT_DIRECTORY = os.path.normpath(os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."))


def get_maya_location(maya_version):
    """Get the location where Maya is installed.

    @param maya_version The maya version number.
    @return The path to where Maya is installed.
    """
    if "MAYA_LOCATION" in os.environ.keys():
        return os.environ["MAYA_LOCATION"]
    if platform.system() == "Windows":
        return "C:/Program Files/Autodesk/Maya{0}".format(maya_version)
    elif platform.system() == "Darwin":
        return "/Applications/Autodesk/maya{0}/Maya.app/Contents".format(maya_version)
    else:
        location = "/usr/autodesk/maya{0}".format(maya_version)
        if maya_version < 2016:
            # Starting Maya 2016, the default install directory name changed.
            location += "-x64"
        return location


def mayapy(maya_version):
    """Get the mayapy executable path.

    @param maya_version The maya version number.
    @return: The mayapy executable path.
    """
    python_exe = "{0}/bin/mayapy".format(get_maya_location(maya_version))
    if platform.system() == "Windows":
        python_exe += ".exe"
    return python_exe


def create_clean_maya_app_dir():
    """Creates a copy of the clean Maya preferences so we can create predictable results.

    @return: The path to the clean MAYA_APP_DIR folder.
    """
    app_dir = os.path.join(ROOT_DIRECTORY, "tests", "clean_maya_app_dir")
    temp_dir = tempfile.gettempdir()
    if not os.path.exists(temp_dir):
        os.makedirs(temp_dir)
    dst = os.path.join(temp_dir, "maya_app_dir{0}".format(uuid.uuid4()))
    shutil.copytree(app_dir, dst)
    return dst


def main():
    parser = argparse.ArgumentParser(description="Runs unit tests for a Maya module")
    parser.add_argument("-m", "--maya", help="Maya version", type=int, default=2020)
    parsed_args = parser.parse_args()
    tests_module = os.path.join(ROOT_DIRECTORY, "tests", "maya_standalone_tests.py")
    cmd = [mayapy(parsed_args.maya), tests_module]
    if not os.path.exists(cmd[0]):
        raise RuntimeError("Maya {0} is not installed on this system.".format(parsed_args.maya))

    maya_app_dir = create_clean_maya_app_dir()
    os.environ["MAYA_APP_DIR"] = maya_app_dir
    os.environ["MAYA_SCRIPT_PATH"] = ""
    os.environ["MAYA_MODULE_PATH"] = ""
    try:
        subprocess.check_call(cmd)
    except subprocess.CalledProcessError:
        pass
    finally:
        shutil.rmtree(maya_app_dir)


if __name__ == "__main__":
    main()
