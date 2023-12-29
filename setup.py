import subprocess
import sys
import venv
import os

# Function to create a virtual environment
def create_venv(venv_name):
    venv.create(venv_name, with_pip=True)
    print(f"Virtual environment '{venv_name}' created successfully!")

# Function to activate the virtual environment
def activate_venv(venv_name):
    activate_script = os.path.join(venv_name, 'Scripts' if sys.platform.startswith('win') else 'bin', 'activate')
    activate_cmd = f"source {activate_script}"
    subprocess.run(activate_cmd, shell=True)
    print(f"Activated virtual environment '{venv_name}'!")

# Function to install requirements using pip
def install_requirements(requirements_file):
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", requirements_file])
    print("Requirements installed successfully!")

# Function to run setup.py
def run_setup():
    subprocess.run([sys.executable, "compile.py"])
    print("Setup.py executed successfully!")

if __name__ == "__main__":
    # Define the name of the virtual environment
    venv_name = "venv"

    # Create a virtual environment
    create_venv(venv_name)

    # Activate the virtual environment
    activate_venv(venv_name)

    # Install requirements.txt
    requirements_file = "requirements.txt"  # Change this to your requirements file path
    install_requirements(requirements_file)

    # Run setup.py
    run_setup()