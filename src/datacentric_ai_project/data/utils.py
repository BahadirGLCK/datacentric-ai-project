import os
import zipfile

def extract_all_zip_files(zip_folder_path, extract_to, prefix='dock'):
    """
    Extracts all .zip files from the given folder into the extract_to directory.

    Args:
        zip_folder_path (str): Path to the folder containing zip files.
        extract_to (str): Destination folder to extract files.
        prefix (str): Prefix filter for zip files.

    Returns:
        str: The destination folder where the files are extracted.
    """
    if not os.path.exists(extract_to):
        os.makedirs(extract_to)

    for file_name in os.listdir(zip_folder_path):
        if file_name.endswith('.zip') and prefix in file_name:
            zip_path = os.path.join(zip_folder_path, file_name)
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                extracted_folder = os.path.join(extract_to, os.path.splitext(file_name)[0])
                zip_ref.extractall(extracted_folder)
                print(f"Extracted {file_name} to {extracted_folder}")

    return extract_to

def get_factory_names(dataset_path):
    """
    Get factory_names from folder names. Those folder contains images and annotation files as PascalVOC format.

    Args:
        dataset_path (str): Maşn path.

    Returns:
        list: Cleaned names list.
    """

    factory_name_list = set()

    for folder_name in sorted(os.listdir(dataset_path)):
        splitted_name = folder_name.split('_')[1:]
        factory_name = ''

        for word in splitted_name:
            if 'task' in word:
                break
            factory_name += word
        
        factory_name_list.add(factory_name)
        
    return factory_name_list

def extract_factory_name(folder_name):
    """
    Extracts the factory name from the folder name.

    Args:
        folder_name (str): Name of the folder.

    Returns:
        str: Extracted factory name.
    """
    splitted_name = folder_name.split('_')[1:]
    factory_name = ''

    for word in splitted_name:
        if 'task' in word:
            break
        factory_name += word

    return factory_name

def collect_desired_files_and_factory_names_from_dataset_folder(dataset_path, file_type):
    """
    Collect files and factory names from the dataset folder. Factory_names are in the folder names.

    Args:
        file_type (str): 'image' or 'label'.

    Returns:
        tuple: List of file paths and list of corresponding factory names.
    """
    factory_files_dict = {}

    folder_type = 'JPEGImages' if file_type == 'image' else 'Annotations'
    file_extention = '.jpg' if file_type == 'image' else '.xml'

    processed_files = set()

    for folder_name in sorted(os.listdir(dataset_path)):
        folder_path = os.path.join(dataset_path, folder_name)

        # Extract factory name from folder name
        factory_name = extract_factory_name(folder_name)

        if 'weather' in factory_name or 'augment' in factory_name or 'rotated' in factory_name:
            continue

        if factory_name not in list(factory_files_dict.keys()):
            factory_files_dict[factory_name] = []

        # Collect files from the folder
        path = os.path.join(folder_path, folder_type)
        if os.path.exists(path):
            for file_name in sorted(os.listdir(path)):
                if file_name.endswith(file_extention) and file_name not in processed_files:
                    factory_files_dict[factory_name].append(os.path.join(path, file_name))
                    processed_files.add(file_name)

    return factory_files_dict