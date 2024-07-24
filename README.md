# NormVCF

This script automates a VCF (Variant Call Format) processing pipeline, including optional steps for decomposition, indel filling, and normalization.

## Prerequisites

- Python 3.x
- bcftools
- Custom Python scripts: `decompose.py` and `fill_indels.py` (must be in the same directory as this script or in PATH)

## Usage
### Required Arguments:

- `-r <reference_fasta>`: Path to the reference FASTA file
- `-i <input_vcf>`: Path to the input VCF file

### Optional Arguments:

- `-d <decomposed_output>`: Path for the decomposed VCF output
- `-f <filled_output>`: Path for the filled VCF output
- `-n <normalized_output>`: Path for the final normalized VCF output

## Pipeline Steps

The script will perform only the steps for which output files are specified:

1. **Decomposition**: Runs `decompose.py` to decompose complex variants in the input VCF.
```
#CHROM   POS ID  REF ALT 
chr1     100 .   ATC ACC 
-> turn into 
chr1     101 .   T   C 
```
2. **Indel Filling**: Runs `fill_indels.py` to fill in missing information for indels.
 ```
#CHROM   POS ID REF ALT 
chr1     100 .  A   - 
-> turn into 
chr1     99  .  TA  T  
```
3. **Normalization**: Uses `bcftools norm` to normalize the VCF according to the reference genome.

Each step will use the output of the previous step as input if multiple steps are specified.