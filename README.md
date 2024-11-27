# KiCad to JLCPCB Converter Script

This Python script is designed to convert KiCad BOM (Bill of Materials) and POS (Component Placement) files into formats compatible with JLCPCB's requirements. The script supports both BOM and CPL (Component Placement List) files, and it can process one or both files depending on what is provided.

## Features
- Converts KiCad BOM files to JLCPCB-compatible XLSX format.
- Converts KiCad POS files to JLCPCB-compatible XLSX format.
- Automatically detects file types based on filename and headers.
- Outputs the converted files as `<name>_JLC.xlsx` and `<name>_JLC.xlsx`.
- Validates the output files to ensure correctness.
- Puts the MFg part number in the output BOM for better parts matching if its populated, but always check the final match at JLC.

## Requirements
- Python 3.x

## Installation
1. Clone or download this repository.
2. Install the required Python libraries (if any). This script only uses the standard library, so no additional packages are required.

## Usage
To use the script, run it from the command line and provide the input files as arguments. You can provide a BOM file, a CPL file, or both.

```sh
python KiCad2JLC.py <input_file_1> <input_file_2>
```

### Example
```sh
python KiCad2JLC.py kicad_bom.csv kicad_pos.csv
```
This will generate `kicad_bom_JLC.xlsx` and `kicad_bom.xlsx` if both BOM and CPL files are provided.

## Input File Requirements
The script expects the input files to have the following columns:

### BOM File
- **Reference**: The reference designator for the component (e.g., R1, C1).
- **Quantity**: The number of components.
- **Value**: The value of the component (e.g., 10k, 0.1uF).
- **Footprint**: The footprint of the component.
- **Mfg Part #**: Manufacturer part number, which will be used as the "Part Number" in the output.

### CPL File (POS File)
- **Mid X**: X coordinate of the component.
- **Mid Y**: Y coordinate of the component.
- **rotation**: Rotation of the component in degrees. (Script converts -90 to 270)
- **side**: The side of the board where the component is placed (e.g., top or bottom).
- **designator**: The reference designator for the component.

## Output Files
The script generates the following files:

- **<name>_JLC.xlsx**: Contains the BOM information in a format compatible with JLCPCB.
  - Columns: Designator, Quantity, Value, Footprint, Part Number

- **<name>_JLC.xlsx**: Contains the CPL information for JLCPCB.
  - Columns: Designator, Mid X, Mid Y, Rotation, Layer

## Notes
- The script automatically detects whether an input file is a BOM or CPL file based on its filename and headers.
- If only a BOM file or only a CPL file is provided, only the respective output will be generated.
- The output messages will specify whether a BOM or CPL file was successfully generated.
- Slight variations of KiCad output files (with different colum headers) can be used. Modify mapping table if needed.

## Example Output Messages
- **"Conversion to JLCPCB BOM file completed successfully!"**: Generated only the BOM file.
- **"Conversion to JLCPCB CPL file completed successfully!"**: Generated only the CPL file.
- **"Conversion to JLCPCB BOM and CPL files completed successfully!"**: Generated both files.

## Troubleshooting
- Ensure the input files have the correct headers as specified in the requirements.
- If you encounter an "Unknown file type" warning, check the headers of your input files to ensure they match the expected format.

## License
This project is open source and available under the MIT License.

