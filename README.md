KiCad to JLCPCB Converter

This script converts Bill of Materials (BOM) and Component Placement List (CPL) files exported from KiCad into formats compatible with JLCPCB's requirements. It reads the BOM and CPL files, processes them, and outputs CSV files that can be directly used for PCB assembly by JLCPCB.

Features

Converts KiCad BOM and CPL (POS) files into JLCPCB-compatible formats.

Handles specific adjustments like converting -90 rotation to 270.

Provides validation to ensure the output files meet JLCPCB's formatting standards.

Requirements

Python 3.x

Required Python packages: pandas

Install the required packages using:

pip install pandas

Usage

To use this script, run it from the command line with the following arguments:

python kicad_to_jlcpcb.py <bom_filename> <pos_filename>

<bom_filename>: Path to the BOM CSV file exported from KiCad.

<pos_filename>: Path to the POS (Component Placement List) CSV file exported from KiCad.

Example

python kicad_to_jlcpcb.py sample_bom.csv sample_pos.csv

This command will generate two output files:

jlcpcb_bom.csv: The BOM file formatted for JLCPCB.

jlcpcb_cpl.csv: The CPL file formatted for JLCPCB.

Output File Format

BOM Output (jlcpcb_bom.csv):

Designator, Quantity, Value, Footprint, Part Number

CPL Output (jlcpcb_cpl.csv):

Designator, Mid X, Mid Y, Rotation, Layer

Notes

The script converts any -90 rotation values to 270 to match JLCPCB's expectations.

The BOM input file must contain the following columns: Reference, Quantity, Value, Footprint, Part Number.

The CPL file requires the following columns from the input POS file: pos_x, pos_y, rotation, side, and designator. Make sure these headers are present.

The CPL file requires the following columns from the input POS file: pos_x, pos_y, rotation, side, and designator. Make sure these headers are present.



License

This project is licensed under the MIT License. See the LICENSE file for more details.
