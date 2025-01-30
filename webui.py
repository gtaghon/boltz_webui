"""
Streamlit WebUI for Running Boltz-1 Biomolecular Structure Simulation
(https://github.com/jwohlwend/boltz)

G Taghon
NIST-MML
Jan 2025

This app provides a Streamlit-based web interface for running biomolecular structure 
simulations using the Boltz-1 model. It allows users to input biological sequences, 
configure simulation parameters, visualize, and save the resulting structures.
"""


import os
import random
import logging
import subprocess
import hashlib
from pathlib import Path

import torch
import streamlit as st
import streamlit.components.v1 as components


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def get_accelerator() -> str:
    """
    Determines the appropriate accelerator to use for computations.

    Returns:
        str: The name of the accelerator device ('cpu', 'mps', or 'cuda').
    """

    if torch.cuda.is_available():
        return "cuda"
    elif torch.backends.mps.is_available():
        # Not all operations implemented on MPS yet, set fallback to CPU
        os.environ['PYTORCH_ENABLE_MPS_FALLBACK'] = '1'
        logger.warning("Enabled experimental MPS PyTorch Lightning support. Some operations are not implemented and will fall back to CPU.")
        return "gpu"
    else:
        return "cpu"

def validate_seq(seq, seq_type) -> bool:
    """
    Validates a biological sequence based on its type.

    Args:
        seq (str): The input biological sequence to be validated.
        seq_type (str): The type of sequence ('protein', 'dna', or 'rna').

    Returns:
        bool: True if the sequence is valid, False otherwise.
    """

    seq = seq.strip().replace(' ', '').upper()
    if seq_type == "rna" and set(seq) != {"A", "U", "C", "G"}:
        st.error("RNA sequence appears to contain noncanonical base characters.")
        return False
    if seq_type == "dna" and set(seq) != {"A", "T", "C", "G"}:
        st.error("DNA sequence appears to contain noncanonical base characters.")
        return False
    if seq_type == "protein" and {"B", "J", "O", "U", "X", "Z"}.intersection(set(seq)):
        st.error("Protein sequence appears to contain non-canonical amino acid characters.")
        return False
    
    return True

def make_fasta(seq: str, seq_type: str) -> str:
    """
    Creates a FASTA file for the given biological sequence.

    Args:
        seq (str): The input biological sequence.
        seq_type (str): The type of sequence ('protein', 'dna', or 'rna').

    Returns:
        str: Path to the created FASTA file or None if validation fails.
    """

    if validate_seq(seq, seq_type):

        fname = hashlib.md5(seq.encode('utf-8')).hexdigest()
        with open(f"temp/{fname}.fasta", 'w') as f:
            f.write(f">A|{seq_type}\n{seq}")
        
        return fname
    
    return

def main():
    """
    Main function that sets up and runs the Streamlit web interface.

    This function creates the UI components, handles user input, and manages the 
    simulation workflow. It uses Streamlit's API to create interactive widgets 
    and displays.
    """

    st.set_page_config(layout="wide")
    st.title("⚡️ Boltz-1 Biomolecular Simulation Interface ⚡️")
    
    # Input section
    seq = st.text_input(
        "Enter amino acid/nucleotide sequence",
        help="Example: MSADAMKSK..., GCTGACGTAC..."
    ).upper()

    radios = st.columns(2, vertical_alignment='bottom')
    sliders = st.columns(4, vertical_alignment='bottom')

    # String parameters
    seq_type = radios[0].radio("Sequence type", ["protein", "rna", "dna"])
    output_format = radios[1].radio("Output format", ["pdb", "mmcif"])

    # Numerical parameters
    sampling_steps = sliders[0].slider("Sampling steps", 50, 300, 200)
    diffusion_samples = sliders[1].slider("Diffusion samples", 1, 3, 1)
    num_workers = sliders[2].slider("Workers", 1, os.cpu_count(), os.cpu_count())
    rand_seed = random.randint(0, 9999)
    seed = sliders[3].slider("Seed", 0, 9999, rand_seed)

    # Generation call
    if st.button("Generate"):
        if not seq:
            st.error("Please enter a sequence.")
            return
        fname = make_fasta(seq, seq_type)
        if fname:
            st.write(f"Created temporary fasta: {fname}")
            try:
                with st.spinner(f"Folding {len(seq)}-mer {seq_type} sequence..."):
                    subprocess.run(["boltz",
                                    "predict",
                                    f"./temp/{fname}.fasta",
                                    "--out_dir",
                                    "./temp",
                                    "--accelerator",
                                    get_accelerator(),
                                    "--sampling_steps",
                                    str(sampling_steps),
                                    "--diffusion_samples",
                                    str(diffusion_samples),
                                    "--output_format",
                                    output_format,
                                    "--num_workers",
                                    str(num_workers),
                                    "--seed",
                                    str(seed),
                                    "--use_msa_server",
                                    ],
                                    capture_output=True).stdout.strip()
            
                    st.write("Structure generated.")

                    # Display model_0
                    if output_format == "pdb":
                        location = f"./temp/boltz_results_{fname}/predictions/{fname}/{fname}_model_0.pdb"
                        pdb_data = Path(location).read_text()

                        # Create a container for the viewer
                        viewer_container = st.container(border=True)
                        with viewer_container:
                            st.markdown("**Generated PDB Model**")
                            # Embed the 3Dmol React.js component
                            components.html(
                                f"""
                                <script src="https://3Dmol.org/build/3Dmol-min.js"></script>
                                <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
                                <div id="molecule-viewer" style="height: 600px; width: 100%; position: relative;"></div>
                                <script>
                                    $(document).ready(function() {{
                                        let element = $('#molecule-viewer');
                                        let config = {{ backgroundColor: 'white' }};
                                        let viewer = $3Dmol.createViewer(element, config);
                                        let data = `{pdb_data}`;
                                        
                                        viewer.addModel(data, "pdb");
                                        viewer.setStyle({{}}, {{cartoon: {{color: 'spectrum'}}}});
                                        viewer.zoomTo();
                                        viewer.render();
                                        viewer.zoom(1.2, 1000);
                                    }});
                                </script>
                                """,
                                height=600,
                            )

                        # Create download button
                        st.download_button("Download PDB",
                                           pdb_data,
                                           "model_0.pdb")
                    
                    elif output_format == "mmcif":
                        st.markdown("**MMCIF Preview Unavailable.**")
                        location = f"./temp/boltz_results_{fname}/predictions/{fname}/{fname}_model_0.mmcif"
                        cif_data = Path(location).read_text()

                        # Create download button
                        st.download_button("Download MMCIF",
                                           cif_data,
                                           "model_0.cif")
                
            except Exception as e:
                st.error(f"An unexpected error occurred: {str(e)}")
                logger.exception("Unexpected error in main workflow")
        
if __name__ == "__main__":
    main()
