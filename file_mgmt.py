import os, sys
import configparser
from contextlib import contextmanager
from escpos import printer

config = configparser.ConfigParser()
config.read('config.ini')

@contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:  
            yield
        finally:
            sys.stdout = old_stdout

def remove_blank_lines(order_names):
    # combine orders and file name to create path
    order_paths = []
    for i in order_names:
        order_paths.append(os.path.join("orders", i))

    # remove blank lines from all files in directory
    for file in order_paths:    
        if not os.path.isfile(file):
            print("{} does not exist ".format(file))
            return
        with open(file) as filehandle:
            lines = filehandle.readlines()

        with open(file, 'w') as filehandle:
            lines = filter(lambda x: x.strip(), lines)
            filehandle.writelines(lines)

def print_files(order_names):
    # combine orders and file name to create path
    order_paths = []
    for i in order_names:
        order_paths.append(os.path.join("orders", i))

    with suppress_stdout():
        rp = printer.Serial(config['CONFIG']['printer_serial_port'])

    for file in order_paths:
        with open(file, 'r') as f:
            data = f.read()
            rp.text(data)
            rp.cut()




def delete_all_orders(order_names):
    # combine orders and file name to create path
    order_paths = []
    for i in order_names:
        order_paths.append(os.path.join("orders", i))
    
    for file in order_paths:
        os.remove(file)