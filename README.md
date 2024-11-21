# KiCad to JLCPCB Converter

This script converts Bill of Materials (BOM) and Component Placement List (CPL) files exported from KiCad into formats compatible with JLCPCB's requirements. It reads the BOM and CPL files, processes them, and outputs CSV files that can be directly used for PCB assembly by JLCPCB.

## Features

- Converts KiCad BOM and CPL (POS) files into JLCPCB-compatible formats.
- Handles specific adjustments like converting `-90` rotation to `270`.
- Provides validation to ensure the output files meet JLCPCB's formatting standards.
- Logs the number of BOM components and CPL placements processed during the conversion.

## Requirements

- Python 3.x
- Required Python packages: `pandas`

Install the required packages using:

```sh
pip install pandas
```

## Usage

To use this script, run it from the command line with the following arguments:

```sh
python kicad_to_jlcpcb.py <bom_filename> <pos_filename>
```

- `<bom_filename>`: Path to the BOM CSV file exported from KiCad.
- `<pos_filename>`: Path to the POS (Component Placement List) CSV file exported from KiCad.

### Example

```sh
python kicad_to_jlcpcb.py sample_bom.csv sample_pos.csv
```

This command will generate two output files:

- `jlcpcb_bom.csv`: The BOM file formatted for JLCPCB.
- `jlcpcb_cpl.csv`: The CPL file formatted for JLCPCB.

## Output File Format

- **BOM Output (jlcpcb_bom.csv)**:

  - `Designator`, `Quantity`, `Value`, `Footprint`, `Part Number`

- **CPL Output (jlcpcb_cpl.csv)**:

  - `Designator`, `Mid X`, `Mid Y`, `Rotation`, `Layer`

## Example Input Files

Here are example BOM and CPL input files:

- **Example BOM File (sample_bom.csv)**:
  ```csv
  Reference,Quantity,Value,Footprint,Part Number
  C1,1,10uF,Capacitor_SMD:C_0805_2012Metric,
  R1,2,1k,Resistor_SMD:R_0805_2012Metric,
  U1,1,ATmega328P,IC_SMD:TQFP-32_7x7mm_P0.8mm,
  ```

- **Example CPL File (sample_pos.csv)**:
  ```csv
  pos_x,pos_y,rotation,side,designator
  12.34,-45.67,90,top,C1
  23.45,67.89,0,top,R1
  34.56,78.90,-90,top,U1
  ```

## Notes

- The script converts any `-90` rotation values to `270` to match JLCPCB's expectations.
- The script logs the number of BOM components and CPL placements processed during the conversion.
- The BOM input file must contain the following columns: `Reference`, `Quantity`, `Value`, `Footprint`, `Part Number`.
- The CPL file requires the following columns from the input POS file: `pos_x`, `pos_y`, `rotation`, `side`, and `designator`. Make sure these headers are present.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.

