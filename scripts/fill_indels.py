import argparse
from utils import read_vcf, read_fasta

def fill_indels(vcf_df, reference_sequence):
    """Fill indels in the VCF DataFrame."""
    fill_snps = []
    for _, row in vcf_df.iterrows():
        pos, ref, alt = row['POS'], row['REF'], row['ALT']
        pos = int(pos) - 1
        if alt == "-":
            # Extend REF to include the base before the deletion
            ref = reference_sequence[pos-1:pos+len(ref)]
            alt = reference_sequence[pos-1]
            pos -= 1
        # Handle insertion (REF is "-")
        elif ref == "-":
            # Extend ALT to include the base before the insertion
            alt = reference_sequence[pos-1] + alt
            ref = reference_sequence[pos-1]
            pos -= 1
        fill_snps.append((pos + 1, ref, alt))
    return fill_snps

def write_filled_vcf(header_lines, filled_snps, vcf_df, output_file):
    """Write filled SNPs to an output VCF file."""
    with open(output_file, 'w') as f:
        # Write header lines
        for line in header_lines:
            f.write(line)
        # Write filled SNPs
        for (pos, ref, alt), (_, row) in zip(filled_snps, vcf_df.iterrows()):
            f.write(f"{row['#CHROM']}\t{pos}\t{row['ID']}\t{ref}\t{alt}\t{row['QUAL']}\t{row['FILTER']}\t{row['INFO']}\n")

def main():
    parser = argparse.ArgumentParser(description="Fill indels in a VCF file using a reference FASTA.")
    parser.add_argument("-r", "--reference", required=True, help="Path to the reference FASTA file")
    parser.add_argument("-i", "--input", required=True, help="Path to the input VCF file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output VCF file")
    args = parser.parse_args()

    # Read reference sequence
    reference_sequence = read_fasta(args.reference)
    # Read VCF
    header_lines, vcf_df = read_vcf(args.input)
    # Fill indels
    filled_snps = fill_indels(vcf_df, reference_sequence)
    # Write filled SNPs to output VCF file
    write_filled_vcf(header_lines, filled_snps, vcf_df, args.output)
    print(f"Filled VCF has been written to {args.output}")

if __name__ == "__main__":
    main()