import csv

def csv_to_dict(csv_file_path):
    """
    Convierte un archivo CSV en un diccionario
    """
    with open(csv_file_path, 'r') as csv_file:
        reader = csv.DictReader(csv_file)
        data = list(reader)
    return data
