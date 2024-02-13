import pyinstaller_versionfile

pyinstaller_versionfile.create_versionfile(
    output_file="versionfile_installer.txt",
    version="1.1.0.0",
    company_name="David Maerker",
    file_description="Installer for Atomiuzer ToolBox Software",
    internal_name="Atomizer Toolbox",
    legal_copyright="© David Maerker",
    original_filename="AtomizerToolbox.Installer.exe",
    product_name="Atomizer Toolbox",
    translations=[0, 1200]
)
