import pyinstaller_versionfile

pyinstaller_versionfile.create_versionfile(
    output_file="version_sign/versionfile.txt",
    version="1.6.8.0",
    company_name="David Maerker",
    file_description="Utilities for atomizer research",
    internal_name="Atomizer Toolbox",
    legal_copyright="© David Maerker",
    original_filename="AtomizerToolbox.exe",
    product_name="Simple App",
    translations=[0, 1200]
)
