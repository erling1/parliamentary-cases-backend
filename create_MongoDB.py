import xml.etree.ElementTree as ET
from pymongo import MongoClient
from datetime import datetime
import os

def connect_to_mongodb():
    client = MongoClient('mongodb://localhost:27017/')
    db = client['political_cases']
    return db

def parse_xml_to_dict(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()
    ns = {'ns': 'http://data.stortinget.no'}
    cases = []
    
    for sak in root.findall('.//ns:sak', ns):
        case = {
            'id': sak.find('ns:id', ns).text,
            'tittel': sak.find('ns:tittel', ns).text,
            'korttittel': sak.find('ns:korttittel', ns).text,
            'status': sak.find('ns:status', ns).text,
            'type': sak.find('ns:type', ns).text
        }
        cases.append(case)
    print(f"Found {len(cases)} cases")
    return cases

def import_to_mongodb(db, cases):
    cases_collection = db['cases']
    result = cases_collection.insert_many(cases)
    return len(result.inserted_ids)

def main(xml_file):
    db = connect_to_mongodb()
    cases = parse_xml_to_dict(xml_file)
    imported_count = import_to_mongodb(db, cases)
    print(f"Imported {imported_count} cases successfully")

# Example usage
if __name__ == "__main__":

    folder_path = "."
    for file_path in os.listdir(folder_path):
        print("file_path:", file_path)
        if file_path.endswith('.xml'):
            full_path = os.path.join(folder_path, file_path)
            main(full_path)