
# Atomizer ToolBox

## How to use

Currently there are two options to use the software.

Either you can download a compiled version from the release tab
However, I would highly recommend to build your own executable file. This is required if matlab is not installed in the default location (`C:\Program Files\MATLAB`)

## How to build your own .exe

IMPORTANT: This software can has a few matlab features. In order to gurantee comparability to previous works, sometimes the matlab scripts have been directly implemented into the software. This is due to difference in matlab and python libaries, which should technically do the same. Spoiler: They don't

If you want to use these features, make sure to have matlab installed

#### Prerequisites:
- [Python 3.11](https://www.python.org/downloads/release/python-3117/) (as of the time writing in late 2023, no newer python verion is supported for matlab functionalities)
- Matlab (optional, but recommended, must have Matlab engine for python support, usally most recent versions should have it)

The installation of these softwares is straight forward and needs to be conducted now.
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


