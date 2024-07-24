import pandas as pd
from Bio import SeqIO

def read_vcf(input_file):
    with open(input_file, 'r') as fin:
        header_lines = [line for line in fin if line.startswith('#')]
        vcf_df = pd.read_csv(
            input_file,
            comment='#',
            header=None,
            sep='\t',
            names=['#CHROM', 'POS', 'ID', 'REF', 'ALT', 'QUAL', 'FILTER', 'INFO']
        )
    return header_lines, vcf_df

def read_fasta(file_path):
    """Read a FASTA file using Biopython and return the sequence."""
    for record in SeqIO.parse(file_path, "fasta"):
        return str(record.seq)

def write_vcf(output_file, header_lines, vcf_df):
    with open(output_file, 'w') as fout:
        fout.writelines(header_lines)
        vcf_df.to_csv(fout, sep='\t', index=False, header=False)