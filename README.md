
# Atomizer ToolBox

## How to use

IMPORTANT: This software has a few matlab features. In order to gurantee comparability to previous works, sometimes the matlab scripts have been directly implemented into the software. This is due to difference in matlab and python libaries, which should technically do the same. Spoiler: They don't.
If you want to use these features, make sure to have matlab installed.

Either you can download a compiled version from the release tab.
However, I would highly recommend to build your own executable file. This is required if matlab is not installed in the default location (`C:\Program Files\MATLAB`) or if issues occur.

#### Prerequisites:
Note: Python is only requiered if you want to compile your own version.

- [Python 3.11](https://www.python.org/downloads/release/python-3117/) (as of the time writing in late 2023, no newer python verion is supported for matlab functionalities)
- Matlab (optional, but recommended, must have Matlab engine for python support, usally most recent versions should have it)

Make sure the add Python to the PATH variable in Windows (set checkbox during Python installation)!

## Using the installer - The easiest way

DISCLAIMER: I don't have a Microsoft Developer License, which comes with an annual cost. 
The compiled installer and the compiled app can be detected by Microsoft defender as a virus. 
You can find the VirusTotal scan [here](https://www.virustotal.com/gui/file/2a27348e21ef5464707e7358ac525ea5ff7565bf7449eb9ffc5b2500553eb3e4?nocache=1).

The installer can be downloaded from the releases or via [this link](https://github.com/realize-1337/Atomizer-Toolbox/releases/download/1.68.3/AtomizerToolboxInstaller.exe).

Once downloaded you can just run the installer. 
The installer should be run as admin. 
You technically can run it as local user, however, the possible install locations may be limited. 

There are two options for installation: 
- Install: Downloads the current pre-compiled release and installs it as a software in Windows
- Compile: Downloads the current release source code and compiles it on the local machine. Afterwards, it will be installed as a software in windows. Note: [Python 3.11](https://www.python.org/downloads/release/python-3117/) must be installed.

## Download the portable version
Download the current [release.zip](https://github.com/realize-1337/Atomizer-Toolbox/releases/latest/download/release.zip).
Unzip the file and run the AtomizerToolbox.exe

## How to build your own .exe - The manual way
Python required!

If you are familiar with git, you can clone the repository. However, since you are reading this, you are probably not. 
Download the source code as a .zip file from the green button on the very top of this website. 
Unzip the file to a location of your choice. 

### Automatic compile (Windows only)
Run the `setup.bat` file (just double click it) in the folder and the process will run fully automatically.
After it has finished, you'll end up with a .exe file in the folder which you can move anywhere you want.

### Manual compile
be aware that this i writte for people without any python knowledge
1. In the unziped folder: Hold shift and press right click, from the dialog select "Open powershell window here"
2. A blue command terminal should appear. Alternatively you can open and command window by CTRL + R and then typing "cmd". If you have taken the "cmd" path, you have to navigate to the unziped folder by typing `cd PATH_TO_UNZIPED_FOLDER`. Make sure to replace `PATH_TO_UNZIPED_FOLDER` with your folder path.
3. Create a virtual environment. In your command window type `python -m venv venv` and press Enter.
4. Type `venv\Scripts\active` to move to the virtual environment. The command line should now start with `(venv)`. Technically the virtual environment is optional, but the programm requires many packages to be installed, which is usually unwanted on the global python installation on your computer, thus a venv acts as virtual python installation. 
5. Type `pip install -r .\requirements.txt` and press Enter. This downloads and installs all required packages. Depending on the internet speed, this can take a few minutes.
6. When the installation has finished you can run the compile. This is done by typing `python setup.py` and press Enter. This operation may take a few minutes.
7. In your folder you can now find your build executable.


