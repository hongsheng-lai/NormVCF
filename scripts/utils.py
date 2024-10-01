import pandas as pd
from Bio import SeqIO
import gzip

def read_vcf(vcf_path):
    # Check if the file ends with .gz
    is_gzip = vcf_path.lower().endswith('.gz')
    
    # Open the file with the appropriate method
    open_func = gzip.open if is_gzip else open
    mode = 'rt' if is_gzip else 'r'
    
    # Get the header
    with open_func(vcf_path, mode) as ifile:
        header_lines = []
        for line in ifile:
            if line.startswith("#"):
                header_lines.append(line)
                
        vcf_names = header_lines[-1].strip().split('\t')
    
    # Read the file into a DataFrame
    compression = 'gzip' if is_gzip else None
    df = pd.read_csv(
        vcf_path,
        compression=compression,
        comment='#',
        delim_whitespace=True,
        header=None,
        names=vcf_names
    )
    
    return header_lines, df

def read_fasta(file_path):
    """Read a FASTA file using Biopython and return the sequence."""
    for record in SeqIO.parse(file_path, "fasta"):
        return str(record.seq)

def write_vcf(output_file, header_lines, vcf_df):
    with open(output_file, 'w') as fout:
        fout.writelines(header_lines)
        vcf_df.to_csv(fout, sep='\t', index=False, header=False)