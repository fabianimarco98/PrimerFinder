**PrimerFinder - A Tool for Designing Primers Based on DNA Sequences**

### Description
PrimerFinder is a Python tool that facilitates the design of primers for DNA sequences. Utilizing the `primer3` library, this program allows you to import sequences from FASTA files, define fragments of interest, and generate optimal primers according to specified parameters.

### Features
- **FASTA File Input**: Load DNA sequences directly from FASTA files.
- **Fragment Definition**: Specify the fragments of the sequence for which you want to design primers.
- **Parameter Customization**: Modify global parameters for primer design.
- **Primer Feedback**: Obtain feedback on GC content and melting temperature (Tm) of the designed primers.
- **Save Primers**: Save the designed primers to a specified file.

### Usage
1. **Input the Path**: Provide the path to your FASTA file containing the DNA sequence.
2. **Specify the Gene Region**: Define the start and end positions of the gene within the sequence.
3. **Design Primers**: Input the number of primers, amplicon size range, and other parameters to generate primers.
4. **Save Results**: Optionally save the designed primers to a file for future use.

### License
This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

### Installation
To install the necessary dependencies, run:
```sh
pip install primer3-py
```

### Example
```python
import os
import primer3

# Example usage code here
```

### Contributions
Contributions are welcome! Please fork this repository and submit a pull request with your changes.

### Authors
- Marco Fabiani

This description should give potential users and contributors a clear understanding of what your tool does, how to use it, and the terms under which it can be used and modified.
