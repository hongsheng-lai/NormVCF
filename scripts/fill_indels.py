import argparse
from utils import read_vcf, read_fasta

def fill_indels_with_reference_check(vcf_df, reference_sequence):
    """Fill indels in the VCF DataFrame."""
    fill_snps = []
    for _, row in vcf_df.iterrows():
        pos, ref, alt = row['POS'], row['REF'], row['ALT']
        pos = int(pos) - 1  # Convert to 0-based position
        
        if alt == "-":  # Deletion
            pos -= 1
            ref = reference_sequence[pos:pos+len(ref)+1]
            alt = reference_sequence[pos]
        elif ref == "-":  # Insertion
            ref = reference_sequence[pos]
            alt = reference_sequence[pos] + alt
        else:  # SNP or already filled indel
            if ref != reference_sequence[pos:pos+len(ref)]:
                print(f"Warning: Reference allele at position {pos+1} does not match the reference sequence")
                continue  # Skip this variant
        
        fill_snps.append((pos + 1, ref, alt))
    
    return fill_snps

def write_filled_vcf(header_lines, filled_snps, vcf_df, output_file):
    """Write filled SNPs to an output VCF file."""
    with open(output_file, 'w') as f:
        sample = vcf_df.columns[-1]
        # Write header lines
        for line in header_lines:
            f.write(line)
        # Write filled SNPs
        for (pos, ref, alt), (_, row) in zip(filled_snps, vcf_df.iterrows()):
            # check if format or sample is present
            if "FORMAT" in row:
                f.write(f"{row['#CHROM']}\t{pos}\t{row['ID']}\t{ref}\t{alt}\t{row['QUAL']}\t{row['FILTER']}\t{row['INFO']}\t{row['FORMAT']}\t{row[sample]}\n")
            else:
                f.write(f"{row['#CHROM']}\t{pos}\t{row['ID']}\t{ref}\t{alt}\t{row['QUAL']}\t{row['FILTER']}\t{row['INFO']}\n")

def main():
    parser = argparse.ArgumentParser(description="Fill indels in a VCF file using a reference FASTA.")
    parser.add_argument("-r", "--reference", required=True, help="Path to the reference FASTA file")
    parser.add_argument("-i", "--input", required=True, help="Path to the input VCF file")
    parser.add_argument("-o", "--output", required=True, help="Path to the output VCF file")
    args = parser.parse_args()

    # Read reference sequence
    reference_sequence = read_fasta(args.reference)
    # turn all characters to uppercase
    reference_sequence = reference_sequence.upper()
    # Read VCF
    header_lines, vcf_df = read_vcf(args.input)
    # Fill indels
    filled_snps = fill_indels_with_reference_check(vcf_df, reference_sequence)
    # Write filled SNPs to output VCF file
    write_filled_vcf(header_lines, filled_snps, vcf_df, args.output)
    print(f"Filled VCF has been written to {args.output}")

if __name__ == "__main__":
    main()