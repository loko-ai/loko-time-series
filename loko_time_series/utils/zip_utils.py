import os
import zipfile
from tempfile import NamedTemporaryFile


def make_zipfile(output_path, dir_to_zip):
    parent_dir = os.path.abspath(os.path.join(dir_to_zip, os.pardir))
    with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for dir_name, sub_dirs, files in os.walk(dir_to_zip):
            zip_file.write(dir_name, os.path.relpath(dir_name, parent_dir))
            for f in files:
                filename = os.path.join(dir_name, f)
                if os.path.isfile(filename):
                    archive_name = os.path.join(os.path.relpath(dir_name, parent_dir), f)
                    zip_file.write(filename, archive_name)


def import_zipfile(file, path):
    with NamedTemporaryFile(suffix=".zip") as temp_file:
        temp_file.write(file.body)
        temp_file.seek(0)
        with zipfile.ZipFile(temp_file.name, 'r') as zip_ref:
            zip_ref.extractall(path)
