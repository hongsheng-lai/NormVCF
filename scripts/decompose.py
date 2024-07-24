import argparse
import pandas as pd
from utils import read_vcf, write_vcf

def decompose_variant(chrom, pos, ref, alt, info):
    return [
        [chrom, pos + i, '.', ref[i], alt[i], '.', '.', info]
        for i in range(len(ref))
        if ref[i] != alt[i]
    ]

def process_variants(vcf_df):
    decomposed_variants = []
    for _, row in vcf_df.iterrows():
        chrom, pos, id_, ref, alt, qual, filter_, info = row
        pos = int(pos)
        if ref != alt:
            if len(ref) == len(alt) and len(ref) > 1:
                decomposed = decompose_variant(chrom, pos, ref, alt, info)
                if decomposed:  # Only add if there are differences
                    decomposed_variants.extend(decomposed)
            else:
                decomposed_variants.append([chrom, pos, id_, ref, alt, qual, filter_, info])
    return pd.DataFrame(decomposed_variants, columns=vcf_df.columns)

def main():
    parser = argparse.ArgumentParser(description="Decompose VCF variants")
    parser.add_argument('-i', '--input', required=True, help="Input VCF file")
    parser.add_argument('-o', '--output', required=True, help="Output VCF file")
    args = parser.parse_args()

    header_lines, vcf_df = read_vcf(args.input)
    decomposed_df = process_variants(vcf_df)
    write_vcf(args.output, header_lines, decomposed_df)

if __name__ == "__main__":
    main()