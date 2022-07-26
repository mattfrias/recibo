import time, os, sys
import configparser
import imaplib, email
from escpos import printer
from email.header import decode_header
from contextlib import contextmanager

class Recibo:
    def __init__(self):
        self._config = configparser.ConfigParser()
        self._config.read('config.ini')

    @contextmanager
    def suppress_stdout(self):
        with open(os.devnull, "w") as devnull:
            old_stdout = sys.stdout
            sys.stdout = devnull
            try:  
                yield
            finally:
                sys.stdout = old_stdout

    def clean(self, text):
        # clean text for creating a legal filename
        return "".join(c if c.isalnum() else "_" for c in text)

    def findOrders(self):
        # login into email and get any unread messages
        mail = imaplib.IMAP4_SSL(self._config['EMAIL']['server'])
        mail.login(self._config['EMAIL']['user'], self._config['EMAIL']['pass'])
        mail.select("INBOX")
        _, search_data = mail.search(None, 'UNSEEN')
        
        for num in search_data[0].split():
            res, msg = mail.fetch(num, "(RFC822)")
            for response in msg:
                if isinstance(response, tuple):
                    # parse a bytes email into a message object
                    msg = email.message_from_bytes(response[1])
                    # decode the email subject
                    subject, encoding = decode_header(msg["Subject"])[0]
                    if isinstance(subject, bytes):
                        # if it's a bytes, decode to str
                        subject = subject.decode(encoding)
                    if msg.is_multipart():
                        # iterate over email parts
                        for part in msg.walk():
                            # extract content type of email
                            content_type = part.get_content_type()
                            content_disposition = str(part.get("Content-Disposition"))
                            try:
                                # get the email body
                                body = part.get_payload(decode=True).decode()
                            except:
                                pass
                    else:
                        # extract content type of email
                        content_type = msg.get_content_type()
                        # get the email body
                        body = msg.get_payload(decode=True).decode()

                    # check if subject is equal to orderSubject
                    if subject == self._config['CONFIG']['order_subject']:
                        folder_name = "orders"
                        if not os.path.isdir(folder_name):
                            os.mkdir(folder_name)
                        filename = self.clean(msg["Date"]) + ".txt"
                        filepath = os.path.join(folder_name, filename)
                        with open(filepath, 'w') as f:
                            f.write(body)

    def remove_blank_lines(self, order_names):
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

    def print_files(self, order_names):
        # combine orders and file name to create path
        order_paths = []
        for i in order_names:
            order_paths.append(os.path.join("orders", i))

        with self.suppress_stdout():
            rp = printer.Serial(self._config['CONFIG']['printer_serial_port'])

        for file in order_paths:
            with open(file, 'r') as f:
                data = f.read()
                rp.text(data)
                rp.cut()
                
    def delete_all_orders(self, order_names):
        # combine orders and file name to create path
        order_paths = []
        for i in order_names:
            order_paths.append(os.path.join("orders", i))
        
        for file in order_paths:
            os.remove(file)

if (__name__ == "__main__"):
    r = Recibo()
    while True:
        # check for a new email every 30 seconds
        print("Looking for new orders...")
        r.findOrders()
        # list all order names in dir and remove blank lines from all text files
        orders = os.listdir("orders")
        r.remove_blank_lines(orders)
        print("Found {} new orders...".format(len(orders)))
        time.sleep(3)
        # if found new orders then print all orders then delete all files and wait for new ones
        if len(orders) > 0:
            print("Printing {} orders...".format(len(orders)))
            r.print_files(orders)
            time.sleep(10)
            print("Deleting {} files from orders folder...".format(len(orders)))
            r.delete_all_orders(orders)
            orders = []

        print("========================================\n")
        time.sleep(30)
        