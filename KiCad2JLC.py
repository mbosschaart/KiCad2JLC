import csv
import os
import argparse
import re

def parse_bom_file(bom_filename):
    components = []
    with open(bom_filename, newline='') as bom_file:
        reader = csv.DictReader(bom_file)
        for row in reader:
            component = {
                'quantity': row.get('Quantity', 1),
                'reference': row.get('Reference', ''),
                'value': row.get('Value', ''),
                'footprint': row.get('Footprint', ''),
                'part_number': row.get('Mfg Part #', ''),
                'designation': row.get('Designation', ''),
            }
            components.append(component)
    return components

def parse_pos_file(pos_filename):
    placements = []
    with open(pos_filename, newline='') as pos_file:
        reader = csv.DictReader(pos_file)
        for row in reader:
            try:
                if '﻿pos_x' not in row or 'pos_y' not in row or 'designator' not in row or 'rotation' not in row or 'side' not in row:
                    print(f"Error: Missing expected columns in row: {row}")
                    continue

                x = round(float(row['﻿pos_x']), 2)
                y = round(float(row['pos_y']), 2)
                rotation = int(float(row['rotation']))
                # Convert -90 to 270
                if rotation == -90:
                    rotation = 270
                layer = row['side'].strip().lower()
                if layer == 'top':
                    layer = 'top'
                elif layer == 'bottom':
                    layer = 'bottom'
                else:
                    layer = 'top'  # Default to top if the value is unrecognized
                placement = {
                    'reference': row['designator'],
                    'x': x,
                    'y': y,
                    'rotation': rotation,
                    'layer': layer
                }
                placements.append(placement)
            except ValueError as e:
                print(f"Error parsing row: {row}, Error: {e}")
    return placements

def convert_to_jlcpcb_bom(bom_components):
    jlcpcb_bom_data = []
    for component in bom_components:
        jlcpcb_component = [
            component['reference'],
            component['quantity'],
            component['value'],
            component['footprint'],
            component['part_number'],
        ]
        jlcpcb_bom_data.append(jlcpcb_component)
    return jlcpcb_bom_data

def convert_to_jlcpcb_cpl(placements):
    jlcpcb_cpl_data = []
    for placement in placements:
        jlcpcb_placement = [
            placement['reference'],
            f"{placement['x']:.2f}mm",
            f"{placement['y']:.2f}mm",
            str(placement['rotation']),
            placement['layer'],
        ]
        jlcpcb_cpl_data.append(jlcpcb_placement)
    return jlcpcb_cpl_data

def write_csv(filename, data, header):
    if not data:
        print(f"Warning: No data to write for file {filename}")
        return
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
        print(f"Data written to {filename} successfully.")

def validate_jlcpcb_files(bom_filename, cpl_filename):
    # Validate BOM file
    if not os.path.exists(bom_filename):
        print(f"Error: BOM file '{bom_filename}' does not exist.")
        return False
    with open(bom_filename, newline='') as bom_file:
        reader = csv.DictReader(bom_file)
        bom_headers = ['Designator', 'Quantity', 'Value', 'Footprint', 'Part Number']
        if set(reader.fieldnames) != set(bom_headers):
            print(f"Error: BOM file '{bom_filename}' has incorrect headers.")
            return False

    # Validate CPL file
    if not os.path.exists(cpl_filename):
        print(f"Error: CPL file '{cpl_filename}' does not exist.")
        return False
    with open(cpl_filename, newline='') as cpl_file:
        reader = csv.DictReader(cpl_file)
        cpl_headers = ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer']
        if reader.fieldnames != cpl_headers:
            print(f"Error: CPL file '{cpl_filename}' has incorrect headers.")
            return False

    print("JLCPCB BOM and CPL files are valid.")
    return True

def determine_file_type(filename):
    # Updated to handle filenames and various header names
    # Check file name to infer possible type
    lower_filename = filename.lower()
    if 'bom' in lower_filename:
        expected_headers = {'reference', 'quantity', 'value', 'footprint'}
    elif 'cpl' in lower_filename or 'pos' in lower_filename:
        expected_headers = {'pos_x', 'pos_y', 'rotation', 'side', 'designator'}
    else:
        expected_headers = None

    with open(filename, newline='') as file:
        reader = csv.DictReader(file)
        headers = [re.sub(r'[^a-zA-Z0-9_]', '', header.strip().lower().replace(' ', '_')) for header in reader.fieldnames if header]

        if expected_headers and all(expected in headers for expected in expected_headers if expected in headers):
            if 'bom' in lower_filename:
                return 'bom'
            elif 'cpl' in lower_filename or 'pos' in lower_filename:
                return 'cpl'
        elif {'reference', 'value', 'footprint'}.issubset(headers):
            return 'bom'
        elif {'pos_x', 'pos_y', 'rotation', 'side', 'designator'}.issubset(headers):
            return 'cpl'
        else:
            print(f"Warning: Unknown file type for file: {filename}. Skipping.")
            return None
        bom_headers = {'reference', 'quantity', 'value', 'footprint'}
        cpl_headers = {'pos_x', 'pos_y', 'rotation', 'side', 'designator'}
        if bom_headers.issubset(headers):
            return 'bom'
        elif cpl_headers.issubset(headers):
            return 'cpl'
        else:
            print(f"Warning: Unknown file type for file: {filename}. Skipping.")
            return None
        

def main():
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Convert KiCad BOM and POS files to JLCPCB format.')
    parser.add_argument('input_files', nargs='+', help='Path to the input CSV file(s)')
    args = parser.parse_args()

    # Parse input files
    bom_components = []
    placements = []

    for filename in args.input_files:
        file_type = determine_file_type(filename)
        if file_type is None:
            continue
        if file_type == 'bom':
            bom_components = parse_bom_file(filename)
        elif file_type == 'cpl':
            placements = parse_pos_file(filename)

    # Convert BOM and CPL to JLCPCB format
    jlcpcb_bom_data = []
    jlcpcb_cpl_data = []

    if bom_components:
        jlcpcb_bom_data = convert_to_jlcpcb_bom(bom_components)
        jlcpcb_bom_filename = 'jlcpcb_bom.csv'
        jlcpcb_bom_header = ['Designator', 'Quantity', 'Value', 'Footprint', 'Part Number']
        write_csv(jlcpcb_bom_filename, jlcpcb_bom_data, jlcpcb_bom_header)
        print(f"Processed {len(bom_components)} BOM components.")

    if placements:
        jlcpcb_cpl_data = convert_to_jlcpcb_cpl(placements)
        jlcpcb_cpl_filename = 'jlcpcb_cpl.csv'
        jlcpcb_cpl_header = ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer']
        write_csv(jlcpcb_cpl_filename, jlcpcb_cpl_data, jlcpcb_cpl_header)
        print(f"Processed {len(placements)} CPL placements.")

    # Validate JLCPCB output files
    if bom_components and placements:
        validate_jlcpcb_files('jlcpcb_bom.csv', 'jlcpcb_cpl.csv')
    
    if bom_components and not placements:
        print("Conversion to JLCPCB BOM file completed successfully!")
    elif placements and not bom_components:
        print("Conversion to JLCPCB CPL file completed successfully!")
    else:
        print("Conversion to JLCPCB BOM and CPL files completed successfully!")

if __name__ == '__main__':
    main()
