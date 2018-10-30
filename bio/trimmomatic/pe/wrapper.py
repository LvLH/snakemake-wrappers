"""
bio/trimmomatic/pe

Snakemake wrapper to trim reads with trimmomatic in PE mode with help of pigz.
pigz is the parallel implementation of gz. Trimmomatic spends most of the time
compressing and decompressing instead of trimming sequences. By using process
substitution (<(command), >(command)), we can accelerate trimmomatic a lot.
"""

__author__ = "Johannes Köster, Jorge Langa"
__copyright__ = "Copyright 2016, Johannes Köster"
__email__ = "koester@jimmy.harvard.edu"
__license__ = "MIT"


from snakemake.shell import shell


def compose_input_gz(filename, compressor="pigz"):
    """Compose the `compressor` command with process substitution.

    Compressor can be 'none', 'gzip', or 'pigz'.

    TODO:
        - ask for the number of jobs.

    > compose_input_gz("test", "none")
    'test'
    > compose_input_gz("test", "pigz")
    '<(pigz --decompress --stdout test)'
    > compose_input_gz("test", "gzip")
    '<(gzip --decompress --stdout test)'
    > compose_input_gz("test", "xz")
    RuntimeError: decompressor must be none, gzip or pigz, not bzip2
    """

    if compressor not in ["none", "gzip", "pigz"]:
        raise RuntimeError(
            "compression methods must be none, gzip or pigz, not {}".format(
                compressor
            )
        )

    if compressor in ["gzip", "pigz"]:
        return "<({compressor} --decompress --stdout {filename})".format(
            compressor=compressor,
            filename=filename
        )
    return filename


def compose_output_gz(filename, compressor="pigz", compression_level="-5"):
    """Compose the `compressor` command with level `compression_level` with
    process substitution.

    Compressor can be 'none', 'gzip', or 'pigz'.

    TODO:
        - ask for the number of threads

    > compose_output_gz("test", "none")
    'test'
    > compose_output_gz("test", "pigz")
    '>(pigz -5 > test)''
    > compose_output_gz("test", "gzip", "-9")
    '>(gzip -9 > test)'
    > compose_output_gz("test", "bzip2")
    RuntimeError: compressor must be none, gzip or pigz, not bzip2
    """

    if compressor not in ["none", "gzip", "pigz"]:
        raise RuntimeError(
            "compression methods must be none, gzip or pigz, not {}".format(
                compressor
            )
        )

    if compressor in ["gzip", "pigz"]:
        filename = ">({compressor} {compression_level} > {filename})".format(
            compressor=compressor,
            compression_level=compression_level,
            filename=filename
        )
    return filename


EXTRA = snakemake.params.get("extra", "")
LOG = snakemake.log_fmt_shell(stdout=True, stderr=True)
COMPRESSION_LEVEL = snakemake.params.get("compression_level", "-5")
TRIMMER = " ".join(snakemake.params.trimmer)

PIGZ = snakemake.params.get("pigz", "")  # none, input, output, both
if PIGZ not in ['none', 'input', 'output', 'both']:
    raise RuntimeError(
        "pigz must be 'none', 'input', 'output', 'both', not {}".format(PIGZ)
    )

# Collect files
INPUT_R1 = snakemake.input.r1
INPUT_R2 = snakemake.input.r2

OUTPUT_R1 = snakemake.output.r1
OUTPUT_R1_UNP = snakemake.output.r1_unpaired
OUTPUT_R2 = snakemake.output.r2
OUTPUT_R2_UNP = snakemake.output.r2_unpaired

# Modify 'filenames'
if PIGZ in ['input', 'both']:
    INPUT_R1 = compose_input_gz(INPUT_R1, "pigz")
    INPUT_R2 = compose_input_gz(INPUT_R2, "pigz")

if PIGZ in ['output', 'both']:
    OUTPUT_R1 = compose_output_gz(OUTPUT_R1, "pigz", COMPRESSION_LEVEL)
    OUTPUT_R1_UNP = compose_output_gz(OUTPUT_R1_UNP, "pigz", COMPRESSION_LEVEL)
    OUTPUT_R2 = compose_output_gz(OUTPUT_R2, "pigz", COMPRESSION_LEVEL)
    OUTPUT_R2_UNP = compose_output_gz(OUTPUT_R2_UNP, "pigz", COMPRESSION_LEVEL)


shell(
    "trimmomatic PE {EXTRA} "
    "{INPUT_R1} {INPUT_R2} "
    "{OUTPUT_R1} {OUTPUT_R1_UNP} "
    "{OUTPUT_R2} {OUTPUT_R2_UNP} "
    "{TRIMMER} "
    "{LOG}"
)
