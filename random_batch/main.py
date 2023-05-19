import os
import shutil as sh
import random
import zipfile

if __name__ == '__main__':
    # zip archives - https://github.com/mwoper/signal_data

    zip_folder = os.path.join('.', 'signal_data')
    source_folder = os.path.join('.', 'data')
    dest_folder = os.path.join('.', 'batch')

    if not os.path.exists(zip_folder):
        raise Exception("Folder which must contains zip archives does not exist!")

    files = os.scandir(zip_folder)

    for file in files:
        if file.name.endswith('.zip'):
            with zipfile.ZipFile(os.path.join(zip_folder, file.name), 'r') as z:
                z.extractall(source_folder)

    if os.path.exists(dest_folder):
        sh.rmtree(dest_folder)

    os.mkdir(dest_folder)

    params = ["omega0", "a0_1"]
    params_0 = ["0.01", "0.02", "0.03", "0.04", "0.05", "0.06", "0.07", "0.08", "0.09"]
    params_1 = ["20.1", "20.2", "20.3", "20.4", "20.5", "20.6"]

    row_count, col_count = len(params_1), len(params_0)

    file_list = os.listdir(source_folder)
    samples = random.sample(range(len(file_list)), row_count*col_count)

    file_name_base = "signal"
    eq_delim = "="
    part_delim = "_"
    ext = ".txt"

    for i, param_0 in enumerate(params_0):
        for j, param_1 in enumerate(params_1):
            file_name = f'{file_name_base}{part_delim}{params[0]}{eq_delim}{param_0}{part_delim}{params[1]}{eq_delim}{param_1}{ext}'

            sh.copy(
                os.path.join(source_folder, file_list[row_count*i + j]), 
                os.path.join(dest_folder, file_name)
            )