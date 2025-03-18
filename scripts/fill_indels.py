import argparse
from utils import read_vcf, read_fasta

def fill_indels_with_reference_check(vcf_df, reference_sequence):
    """Fill indels in the VCF DataFrame and store all relevant information, handling optional columns."""
    fill_snps = []
    sample_column = vcf_df.columns[-1] if len(vcf_df.columns) > 9 else 'SAMPLE'  # Use last column if it exists, else default to 'SAMPLE'

    for _, row in vcf_df.iterrows():
        # Extract mandatory columns with defaults for missing ones
        chrom = row.get('#CHROM', '.')
        pos = int(row.get('POS', 0)) - 1  # Convert to 0-based position
        ref = row.get('REF', '-').upper()
        alt = row.get('ALT', '-').upper()

        # Extract optional columns with default values
        variant_id = row.get('ID', '.')
        qual = row.get('QUAL', '.')
        filter_ = row.get('FILTER', '.')
        info = row.get('INFO', '.')
        format_ = row.get('FORMAT', '.')
        sample_data = row.get(sample_column, '.')

        # Handle different variant types
        if alt == "-":  # Deletion
            ref = reference_sequence[pos-1:pos + len(ref)]
            alt = reference_sequence[pos-1]
            pos = pos - 1
        elif ref == "-":  # Insertion
            ref = reference_sequence[pos]
            alt = reference_sequence[pos] + alt
        else:  # SNP or already filled indel
            if ref != reference_sequence[pos:pos + len(ref)]:
                print(f"Warning: Reference allele at position {pos + 1} does not match the reference sequence")
                continue  # Skip this variant

        # Append all relevant data as a dictionary
        fill_snps.append({
            'CHROM': chrom,
            'POS': pos + 1,  # Convert back to 1-based position
            'ID': variant_id,
            'REF': ref,
            'ALT': alt,
            'QUAL': qual,
            'FILTER': filter_,
            'INFO': info,
            'FORMAT': format_,
            sample_column: sample_data  # Use detected or default sample column
        })

    return fill_snps, sample_column  # Return the detected or default sample column

def write_filled_vcf(header_lines, filled_snps, sample_column, output_file):
    """Write filled SNPs to an output VCF file, handling optional columns."""
    with open(output_file, 'w') as f:
        # Write header lines
        for line in header_lines:
            f.write(line)
        # Write filled SNPs
        for snp in filled_snps:
            f.write(f"{snp.get('CHROM', '.')}\t{snp.get('POS', '.')}\t{snp.get('ID', '.')}\t"
                    f"{snp.get('REF', '.')}\t{snp.get('ALT', '.')}\t{snp.get('QUAL', '.')}\t"
                    f"{snp.get('FILTER', '.')}\t{snp.get('INFO', '.')}\t{snp.get('FORMAT', '.')}\t"
                    f"{snp.get(sample_column, '.')}\n")

def main():
    parser = argparse.ArgumentParser(description="Fill indels in a VCF file using a reference FASTA.")
    parser.add_argument("-r", "--reference", required=True, help="Path to the reference FASTA file")
    parser.add_argument("-i", "--input", required=True, help="Path to the input VCF file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output VCF file")
    args = parser.parse_args()

    # Read reference sequence
    reference_sequence = read_fasta(args.reference)
    reference_sequence = reference_sequence.upper()  # Ensure consistency in case

    # Read VCF
    header_lines, vcf_df = read_vcf(args.input)

    # Fill indels
    filled_snps, sample_column = fill_indels_with_reference_check(vcf_df, reference_sequence)

    # Write filled SNPs to output VCF file
    write_filled_vcf(header_lines, filled_snps, sample_column, args.output)
    print(f"Filled VCF has been written to {args.output}")

if __name__ == "__main__":
    main()
