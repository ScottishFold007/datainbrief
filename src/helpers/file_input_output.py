import os
import csv
import pickle


def save_object(name, object):
    try:
        print("saving the data structure.. ")
        with open('obj/' + name + '.pkl', 'wb') as f:
            pickle.dump(object, f, pickle.HIGHEST_PROTOCOL)
    except IOError as e:
        print(e)


def load_object(name):
    content = None
    try:
        print("reading the data structure.. ")
        with open('obj/' + name + '.pkl', 'rb') as f:
            content = pickle.load(f)
    except FileNotFoundError as e:
        print(e)

    return content


def read_file(file_path):
    content = None
    try:
        with open(file_path, 'r') as f:
            print('reading file ', file_path)
            content = f.read()
    except IOError as e:
        print(e)
    return content


def write_file(filename, data):
    try:
        with open(filename, 'w') as f:
            print('writing to ', filename)
            f.write(data)
    except IOError as e:
        print(e.message)


def read_line_by_line(file_path):
    content = None
    try:
        with open(file_path, 'r') as f:
            print('reading file line by line ', file_path)
            content = f.read().splitlines()
    except IOError as e:
        print(e)
    return content


def write_line_by_line(file_path, data):
    try:
        with open(file_path, 'w') as f:
            print('writing line by line ', file_path)
            for line in data:
                f.write(str(line) + "\n")
    except IOError as e:
        print(e.message)
