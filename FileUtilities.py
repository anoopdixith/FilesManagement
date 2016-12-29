__author__ = 'adixith'
import os
import re
import datetime
import shutil
from pwd import getpwuid


class FileRetention:
    candidates = []
    directory = ""
    destination_directory = ""

    def __init__(self):
        pass

    def process_condition_results(self, condition_validations, condition_logic):
        # Check if no condition was given. If so, return True
        if not condition_validations:
            return True
        if condition_logic is "or":
            for result in condition_validations:
                if result is True:
                    return True
            return False
        if condition_logic is "and":
            for result in condition_validations:
                if result is False:
                    return False
            return True

    def validate_conditions(self, file_name,
                            containing_regex,
                            condition_logic,
                            only_files,
                            only_directories,
                            size_greater_than,
                            last_modified_before,
                            last_modified_after,
                            date_format,
                            owned_by):
        condition_validations = []
        if re.search(containing_regex, file_name):
            full_path = self.directory + "/" + file_name
            if only_files:
                condition_validations.append(os.path.isfile(full_path))
            if only_directories:
                condition_validations.append(os.path.isdir(full_path))
            if last_modified_before != "":
                condition_date = datetime.datetime.strptime(last_modified_before, date_format)
                condition_validations.append(self.find_last_modified_time(full_path) < condition_date)
            if last_modified_after != "":
                condition_date = datetime.datetime.strptime(last_modified_after, date_format)
                condition_validations.append(self.find_last_modified_time(full_path) > condition_date)
            if size_greater_than > 0:
                condition_validations.append(self.find_size(full_path) > size_greater_than)
            if owned_by != "":
                condition_validations.append(self.find_owner(full_path) == owned_by)
        else:
            return False

        return self.process_condition_results(condition_validations, condition_logic)

    def find_owner(self, full_path):
        return getpwuid(os.stat(full_path).st_uid).pw_name

    def find_size(self, full_path):
        return os.path.getsize(full_path)

    def find_last_modified_time(self, full_path):
        last_modified_time = os.path.getmtime(full_path)
        return datetime.datetime.fromtimestamp(last_modified_time)

    def list_operation(self):
        for file_name in self.candidates:
            full_path = self.directory + "/" + file_name
            file_size = str(self.find_size(full_path))
            file_owner = self.find_owner(full_path)
            last_modified_time = str(self.find_last_modified_time(full_path))
            print file_name + " " + file_size + " " + file_owner + " " + last_modified_time

    def remove_file(self, full_path):
        print("Deleting " + full_path)
        os.remove(full_path)

    def remove_dir(self, full_path):
        print("Deleting " + full_path)
        if not os.path.isdir(full_path):
            raise ValueError("Lib error: This is not a directory")
        for entity in os.listdir(full_path):
            full_inner_path = full_path + "/" + entity
            if os.path.isfile(full_inner_path):
                self.remove_file(full_inner_path)
            elif os.path.isdir(full_inner_path):
                self.remove_dir(full_inner_path)
        os.rmdir(full_path)

    def remove_operation(self):
        for entity in self.candidates:
            full_path = self.directory + "/" + entity
            if os.path.isfile(full_path):
                self.remove_file(full_path)
            elif os.path.isdir(full_path):
                self.remove_dir(full_path)

    def move_operation(self, copy=False):
        if self.destination_directory == "":
            raise ValueError("Please specify a valid destination directory for move/copy operation")
        for entity in self.candidates:
            full_path = self.directory + "/" + entity
            full_destination_path = self.destination_directory + "/" + entity
            if copy:
                shutil.copytree(full_path, full_destination_path)
            else:
                shutil.move(full_path, full_destination_path)

    def perform_operation(self, operation):
        if operation == "list":
            self.list_operation()
            return
        if operation == "remove" or operation == "delete":
            self.remove_operation()
        if operation == "move":
            self.move_operation()
        if operation == "copy":
            self.move_operation(copy=True)

    def find_all_files_containing(self,
                                  directory,
                                  containing_regex,  # don't want to give a default
                                  condition_logic="or",
                                  only_files=False,  # conditions start
                                  only_directories=False,
                                  size_greater_than=0,
                                  last_modified_before="",
                                  last_modified_after="",
                                  date_format="%m/%d/%y %H:%M",
                                  owned_by="",  # conditions end
                                  operation="list",
                                  destination_dir=""):
        if only_directories and only_files:
            raise ValueError("Only Directories and Only Files both cannot be True")
        self.directory = directory
        if destination_dir != "":
            self.destination_directory = destination_dir

        for file_name in os.listdir(directory):
            validation = self.validate_conditions(file_name,
                                                  containing_regex,
                                                  condition_logic,
                                                  only_files,
                                                  only_directories,
                                                  size_greater_than,
                                                  last_modified_before,
                                                  last_modified_after,
                                                  date_format,
                                                  owned_by)
            if validation:
                self.candidates.append(file_name)
        self.perform_operation(operation)
