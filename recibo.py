import time
import os
import file_mgmt
import subject_search

testlist = os.listdir("orders")
file_mgmt.remove_blank_lines(testlist)
while True:
    #check for a new email every 30 seconds
    print("Looking for new orders...")
    subject_search.findOrders()
    # list all order names in dir and remove blank lines from all text files
    orders = os.listdir("orders")
    file_mgmt.remove_blank_lines(orders)
    print("Found {} new orders...".format(len(orders)))
    time.sleep(3)
    # if found new orders then print all orders then delete all files and wait for new ones
    if len(orders) > 0:
        print("Printing {} orders...".format(len(orders)))
        file_mgmt.print_files(orders)
        time.sleep(10)
        print("Deleting {} files from orders folder...".format(len(orders)))
        file_mgmt.delete_all_orders(orders)
        orders = []

    print("========================================\n")
    time.sleep(20)