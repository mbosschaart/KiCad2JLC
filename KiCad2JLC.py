import pandas as pd
import os
import argparse
import logging
from typing import List
import csv

logging.basicConfig(level=logging.INFO)

# Constants for header mappings and expected headers
BOM_HEADERS = {
    'reference': ['Reference', 'reference', 'designator', 'RefDes', 'Designator'],
    'quantity': ['Mfg Qty', 'Quantity', 'quantity', 'qty', 'Mfg qty'],
    'value': ['Value', 'value', 'Part Value', 'Designation'],
    'footprint': ['Footprint', 'footprint', 'Package'],
    'part_number': ['Mfg Part #', 'part_number', 'Part Number', 'mpn', 'Manufacturer Part Number', 'Supplier and ref']
}

CPL_HEADERS = {
    'Reference': ['Reference', 'Ref', 'designator', 'Designator', 'RefDes'],
    'Mid X': ['Mid X', 'PosX', 'X', 'x', 'Pos X', 'pos_x'],
    'Mid Y': ['Mid Y', 'PosY', 'Y', 'y', 'Pos Y', 'pos_y'],
    'Rotation': ['Rotation', 'Rot', 'rotation', 'angle', 'Angle'],
    'Layer': ['Layer', 'Side', 'side', 'layer']
}

class MissingColumnError(Exception):
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class BOMParser:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = self._read_input_file()
        self.header_mapping = self._get_header_mapping()
        self.output_data = self._create_output_dataframe()

    def _read_input_file(self) -> pd.DataFrame:
        """Read the input file and return a DataFrame"""
        with open(self.filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if ';' in lines[0]:
                delimiter = ';'
            else:
                delimiter = ','
    
        df = pd.read_csv(self.filename, 
                        sep=delimiter,
                        quoting=csv.QUOTE_ALL,
                        quotechar='"',
                        skipinitialspace=True,
                        engine='python',
                        index_col=False,
                        dtype=str)
        
        df = df.apply(lambda x: x.str.strip('" ') if x.dtype == "object" else x)
        return df

    def _get_header_mapping(self) -> dict:
        """Create a mapping between input headers and JLC headers"""
        input_headers = list(self.data.columns)
        input_headers = [h.strip('" ') for h in input_headers]
        
        header_mapping = {}
        
        # For each input header, find which output column it should map to
        for input_header in input_headers:
            input_header_lower = input_header.lower()
            for output_col, possible_headers in BOM_HEADERS.items():
                if input_header_lower in [h.lower() for h in possible_headers]:
                    # Map from input header to output header
                    header_mapping[input_header] = output_col
                    break
        
        logging.info(f"Header mapping: {header_mapping}")
        return header_mapping

    def _create_output_dataframe(self) -> pd.DataFrame:
        """Create the JLC-formatted output DataFrame"""
        output_df = pd.DataFrame()
        
        # The header_mapping maps from input columns to output columns
        # We need to copy from input columns to their corresponding output columns
        for input_col, output_col in self.header_mapping.items():
            output_df[output_col] = self.data[input_col]
        
        # Add empty part_number column if it doesn't exist
        if 'part_number' not in output_df.columns:
            output_df['part_number'] = ''
        
        # Ensure columns are in the correct order
        return output_df[['reference', 'quantity', 'value', 'footprint', 'part_number']]

    def parse(self) -> pd.DataFrame:
        """Return the JLC-formatted DataFrame"""
        return self.output_data

class CPLParser:
    def __init__(self, filename: str):
        self.filename = filename
        self.data = self._read_input_file()
        self.header_mapping = self._get_header_mapping()
        self.output_data = self._create_output_dataframe()

    def _read_input_file(self) -> pd.DataFrame:
        """Read the input file and return a DataFrame"""
        with open(self.filename, 'r', encoding='utf-8') as file:
            lines = file.readlines()
            if ';' in lines[0]:
                delimiter = ';'
            else:
                delimiter = ','
    
        df = pd.read_csv(self.filename, 
                        sep=delimiter,
                        quoting=csv.QUOTE_ALL,
                        quotechar='"',
                        skipinitialspace=True,
                        engine='python',
                        index_col=False,
                        dtype=str)
        
        df = df.apply(lambda x: x.str.strip('" ') if x.dtype == "object" else x)
        return df

    def _get_header_mapping(self) -> dict:
        """Create a mapping between input headers and JLC headers"""
        input_headers = list(self.data.columns)
        input_headers = [h.strip('" ') for h in input_headers]
        
        header_mapping = {}
        
        # For each input header, find which output column it should map to
        for input_header in input_headers:
            input_header_lower = input_header.lower()
            for output_col, possible_headers in CPL_HEADERS.items():
                if input_header_lower in [h.lower() for h in possible_headers]:
                    # Map from input header to output header
                    header_mapping[input_header] = output_col
                    break
        
        logging.info(f"Header mapping: {header_mapping}")
        return header_mapping

    def _create_output_dataframe(self) -> pd.DataFrame:
        """Create the JLC-formatted output DataFrame"""
        output_df = pd.DataFrame()
        
        # The header_mapping maps from input columns to output columns
        # We need to copy from input columns to their corresponding output columns
        for input_col, output_col in self.header_mapping.items():
            output_df[output_col] = self.data[input_col]
            
            # Add 'mm' suffix to coordinate columns while preserving input precision up to 4 decimals
            if output_col in ['Mid X', 'Mid Y']:
                # Convert to float, round to 4 decimals, convert to string and add 'mm'
                output_df[output_col] = pd.to_numeric(output_df[output_col]).round(4).astype(str) + 'mm'
        
        # Process rotation - convert to integer
        if 'Rotation' in output_df:
            output_df['Rotation'] = pd.to_numeric(output_df['Rotation']).apply(
                lambda r: 270 if float(r) == -90 else int(float(r))
            )
        
        # Process layer
        if 'Layer' in output_df:
            output_df['Layer'] = output_df['Layer'].str.lower()
            output_df['Layer'] = output_df['Layer'].apply(
                lambda s: 'top' if s not in ['top', 'bottom'] else s
            )
        
        # Ensure all required columns exist and are in the correct order
        required_columns = ['Reference', 'Mid X', 'Mid Y', 'Rotation', 'Layer']
        for col in required_columns:
            if col not in output_df.columns:
                raise MissingColumnError(f"Missing required column: {col}")
        
        return output_df[required_columns]

    def parse(self) -> pd.DataFrame:
        """Return the JLC-formatted DataFrame"""
        return self.output_data

def write_output(filename: str, data: pd.DataFrame, header: List[str]):
    """Write DataFrame to Excel file"""
    if data.empty:
        logging.warning(f"No data to write for file {filename}")
        return
    
    # Change extension to .xlsx
    filename = os.path.splitext(filename)[0] + '.xlsx'
    
    # Write to Excel using openpyxl engine
    data.to_excel(filename, index=False, header=header, engine='openpyxl')
    logging.info(f"Data written to {filename} successfully.")

def determine_file_type(filename: str) -> str:
    lower_filename = filename.lower()
    if 'bom' in lower_filename:
        return 'bom'
    elif 'pos' in lower_filename or 'cpl' in lower_filename:
        return 'cpl'
    else:
        logging.warning(f"Unknown file type for file: {filename}. Skipping.")
        return ''

def main():
    parser = argparse.ArgumentParser(description='Convert KiCad BOM and POS files to JLCPCB format.')
    parser.add_argument('input_files', nargs='+', help='Path to the input CSV file(s)')
    args = parser.parse_args()

    bom_data = pd.DataFrame()
    cpl_data = pd.DataFrame()

    for file in args.input_files:
        base_filename = os.path.splitext(file)[0]
        
        file_type = determine_file_type(file)
        if file_type == 'bom':
            bom_parser = BOMParser(file)
            bom_data = bom_parser.parse()
            if not bom_data.empty:
                output_filename = f"{base_filename}_JLC"
                write_output(output_filename, bom_data, bom_data.columns.tolist())
        elif file_type == 'cpl':
            cpl_parser = CPLParser(file)
            cpl_data = cpl_parser.parse()
            if not cpl_data.empty:
                output_filename = f"{base_filename}_JLC"
                write_output(output_filename, cpl_data, cpl_data.columns.tolist())

    # Summary of results
    if not bom_data.empty and not cpl_data.empty:
        logging.info("Conversion to JLCPCB BOM and CPL files completed successfully!")
    elif not bom_data.empty:
        logging.info("Conversion to JLCPCB BOM file completed successfully!")
    elif not cpl_data.empty:
        logging.info("Conversion to JLCPCB CPL file completed successfully!")
    else:
        logging.warning("No valid BOM or CPL data found. No files were written.")

if __name__ == "__main__":
    main()
