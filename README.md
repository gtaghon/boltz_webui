# boltz_webui
Basic streamlit webui for running Boltz-1 biomolecular structure generator. Supports automatic GPU acceleration with CUDA and Metal*.

https://github.com/jwohlwend/boltz

**Experimental support, tested on Apple M2/M2 Max*

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
The app should launch and be accessible in a browser at http://localhost:8501.
To change the default port (8501), use the flag `--server.port <port>`.

## Use
Enter a biosequence, select the correct input type (protein, dna, rna) and select an output file type, then click `Generate`. You may also adjust various generation parameters using the sliders.
If 'pdb' is selected as output type, you will be able to preview the generated model in 3D.
Preview is not available for MMCIF output.
Click the `Download` button to acquire the generated pdb/cif file.

All generated files are stored in `$repo_location/temp/` by default. Runs/files are named using the MD5 hash of the sequence; running the same input sequence twice should skip folding and load the existing prediction, if present in `temp`.

## Disclaimer
This is an alpha version of the webui and it may not behave as intended. Use it at your own risk.

### Known issues
- `Tried to instantiate class 'path.path'`: torch-streamlit error in stdio. Does not affect operation.
- `seed` resets to random int whenever touched (fix in progress).
- Currently no cleanup of temporary fasta/pdb files, implementation TODO.
