import csv
import os
import argparse
import re
import logging

logging.basicConfig(level=logging.INFO)

def parse_bom_file(bom_filename):
    components = []
    with open(bom_filename, newline='', encoding='utf-8-sig') as bom_file:
        reader = csv.DictReader(bom_file)
        header_mapping = {
            'reference': ['Reference', 'reference', 'designator'],
            'quantity': ['Quantity', 'quantity', 'qty', 'Mfg Qty'],
            'value': ['Value', 'value'],
            'footprint': ['Footprint', 'footprint'],
            'part_number': ['Mfg Part #', 'part_number', 'Part Number', 'mpn'],
            'designation': ['Designation', 'designation']
        }

        for row in reader:
            component = {}
            for key, aliases in header_mapping.items():
                for alias in aliases:
                    if alias in row:
                        component[key] = row[alias]
                        break
                else:
                    component[key] = ''  # Default to empty if not found
            components.append(component)

    return components

def parse_pos_file(pos_filename):
    placements = []
    with open(pos_filename, newline='', encoding='utf-8-sig') as pos_file:
        reader = csv.DictReader(pos_file)
        header_mapping = {
            'pos_x': ['pos_x', 'PosX', 'x', 'Mid X'],
            'pos_y': ['pos_y', 'PosY', 'y', 'Mid Y'],
            'rotation': ['rotation', 'Rotation'],
            'side': ['side', 'Side'],
            'reference': ['designator', 'Designator', 'reference']
        }
        for row in reader:
            try:
                parsed_row = {
                    key: row.get(next((alias for alias in aliases if alias in row), ''), '')
                    for key, aliases in header_mapping.items()
                }
                if any(value == '' for value in parsed_row.values()):
                    logging.info(f"Error: Missing expected columns in row: {row}")
                    continue

                x = round(float(parsed_row['pos_x']), 2)
                y = round(float(parsed_row['pos_y']), 2)
                rotation = int(float(parsed_row['rotation']))
                # Convert -90 to 270
                if rotation == -90:
                    rotation = 270
                layer = parsed_row['side'].strip().lower()
                layer = 'top' if layer not in ['top', 'bottom'] else layer
                placement = {
                    'reference': parsed_row['reference'],
                    'x': x,
                    'y': y,
                    'rotation': rotation,
                    'layer': layer
                }
                placements.append(placement)
            except ValueError as e:
                logging.info(f"Error parsing row: {row}, Error: {e}")
    return placements

def convert_to_jlcpcb_bom(bom_components):
    grouped_components = {}
    for component in bom_components:
        key = (component['value'], component['footprint'], component['part_number'])
        if key not in grouped_components:
            grouped_components[key] = {
                'reference': component['reference'],
                'quantity': int(component['quantity']) if component['quantity'].isdigit() else 1,
                'value': component['value'],
                'footprint': component['footprint'],
                'part_number': component['part_number']
            }
        else:
            grouped_components[key]['reference'] += f", {component['reference']}"
            if component['quantity'].isdigit():
                grouped_components[key]['quantity'] += int(component['quantity'])

    jlcpcb_bom_data = []
    for component in grouped_components.values():
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
        if 'reference' not in placement or not placement['reference']:
            logging.warning(f"Skipping placement due to missing 'reference' key: {placement}")
            continue
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
        logging.warning(f"No data to write for file {filename}")
        return
    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(data)
        logging.info(f"Data written to {filename} successfully.")

def main():
    parser = argparse.ArgumentParser(description='Convert KiCad BOM and POS files to JLCPCB format.')
    parser.add_argument('input_files', nargs='+', help='Path to the input CSV file(s)')
    args = parser.parse_args()

    bom_components = []
    placements = []

    for filename in args.input_files:
        if 'bom' in filename.lower():
            bom_components = parse_bom_file(filename)
        elif 'pos' in filename.lower() or 'cpl' in filename.lower():
            placements = parse_pos_file(filename)

    # Convert BOM and CPL to JLCPCB format
    if bom_components:
        jlcpcb_bom_data = convert_to_jlcpcb_bom(bom_components)
        jlcpcb_bom_filename = 'jlcpcb_bom.csv'
        jlcpcb_bom_header = ['Designator', 'Quantity', 'Value', 'Footprint', 'Part Number']
        write_csv(jlcpcb_bom_filename, jlcpcb_bom_data, jlcpcb_bom_header)
        logging.info(f"Processed {len(bom_components)} BOM components.")

    if placements:
        jlcpcb_cpl_data = convert_to_jlcpcb_cpl(placements)
        jlcpcb_cpl_filename = 'jlcpcb_cpl.csv'
        jlcpcb_cpl_header = ['Designator', 'Mid X', 'Mid Y', 'Rotation', 'Layer']
        write_csv(jlcpcb_cpl_filename, jlcpcb_cpl_data, jlcpcb_cpl_header)
        logging.info(f"Processed {len(placements)} CPL placements.")

    if bom_components and not placements:
        logging.info("Conversion to JLCPCB BOM file completed successfully!")
    elif placements and not bom_components:
        logging.info("Conversion to JLCPCB CPL file completed successfully!")
    else:
        logging.info("Conversion to JLCPCB BOM and CPL files completed successfully!")

if __name__ == '__main__':
    main()
