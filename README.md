# boltz_webui
Basic streamlit webui for running Boltz-1 biomolecular structure generator.

https://github.com/jwohlwend/boltz

## Installation
First, create a virtual environment:
```
python -m venv venv
```
Then, install the requirements and launch the webui:
```
pip install -r requirements.txt
streamlit run webui.py
```
The app should launch and be accessible in a broswer at http://localhost:8501.
To change the default port (8501), use the flag `--server.port <port>`.

## Use
Enter a biosequence and select the correct input type (protein, dna, rna) and an output file type, then click generate. You may also adjust various generation parameters using the sliders.
If 'pdb' is selected as output type, you will be able to preview the generated model in 3D.
Preview is not avaibale for MMCIF output.
Click the `Download` button to acquire the generated pdb/cif file.

## Disclaimer
This is an alpha version of the webui and it may not behave as intended. Use it at your own risk.
