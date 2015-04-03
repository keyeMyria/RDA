################################################################################
#
# File Name: MDCSMigration.py
# Purpose: Abstract class for Migration   
#
# Author: Guillaume SOUSA AMARAL
#         guillaume.sousa@nist.gov
#
# Sponsor: National Institute of Standards and Technology (NIST)
#
################################################################################

from pymongo import MongoClient
from collections import OrderedDict
from datetime import datetime
import subprocess
import os
import signal
import requests
import logging
import time
import platform
from abc import ABCMeta, abstractmethod

# Prerequisites:
# 
# - No MongoDB instance running
# - MongoDB added to PATH
# - current MDCS version running
# - copy/paste db.sqlite3 file in new mdcs folder
# - localhost
# - id will change / relations will be preserved
#
# Inputs:
# - path to original db directory
# - REST API URL
# - MDCS user/password
# 
# Algorithm:
# - connect to db_1
# - connect to new MDCS API
# - get required collections from db_1
# - for each record, send data to db_2 using rest api
#
#
# Versions:
# - unknown
# - 1
# - 1.1
# - 1.2

ORIG_DB_PORT = 27000

class MDCSMigration(object):
    
    __metaclass__ = ABCMeta
    
    def __init__(self, db_orig, server_dest, user_dest, pswd_dest):
        # initialization
        self.db_orig = db_orig
        self.server_dest = server_dest
        self.user_dest = user_dest
        self.pswd_dest = pswd_dest
        self.mongo_pid = None
        
        # initialize identifiers map that will keep track of ids from one system to another
        self.identifiers = {}
        
        # initialize logger        
        logging.basicConfig(filename='migration.log',level=logging.INFO, filemode='w')
        logging.info(str(datetime.now()))
    
    def run(self):
        try:            
            if self.connect():
                if self.ping():
                    logging.info("Start of data migration.")
                    self.migrate()
                    logging.info("End of data migration.")
                else:
                    logging.critical("Unable to reach MDCS API.")
            else:
                logging.critical("Unable to connect to original database.")
        except Exception,e:
            logging.critical(e.message)
        finally:
            self.clean()
        

    def connect(self):
        try:
            logging.info("Trying to connect to original database...")
            # Prepare command to run mongodb
            command = 'mongod --dbpath "{0}" --port {1} --bind_ip 127.0.0.1'.format(self.db_orig, ORIG_DB_PORT)                     
            # run mongodb instances            
            if platform.system() == 'Windows':
                logging.info("Windows system detected.")
                self.mongo_pid = subprocess.Popen(command).pid
            else:
                logging.info("System other than Windows detected.")
                self.mongo_pid = subprocess.Popen(command, shell=True).pid
            logging.info("Connection to original database command run in process PID: " + str(self.mongo_pid))
            # sleep for 3 seconds (arbitrary set) to let time to mongo daemon to run
            time.sleep(3)
            client = MongoClient('localhost', ORIG_DB_PORT)
            client.close()
            logging.info("Connected to original database.")
            return True
        except Exception, e:
            logging.critical(e.message)
            return False
    
    def ping(self):
        logging.info("Trying to reach MDCS API...")
        url = self.server_dest + "/rest/ping"
        r = requests.get(url, auth=(self.user_dest,self.pswd_dest))
        logging.info("Ping to MDCS API ended with code: " + str(r.status_code))
        if r.status_code == 200:
            logging.info("MDCS API reached with success.")
            return True
        else:
            logging.critical("Unable to reach MDCS API.")
            return False
        
    @abstractmethod
    def migrate(self):
        pass
    

    def clean(self):
        try:
            if self.mongo_pid is not None:
                try:
                    os.kill(self.mongo_pid, signal.SIGTERM)
                    logging.info("Running instance of Mongodb killed.")
                except:
                    logging.critical("Unable to end Mongodb instance.")
        except Exception, e:
            logging.critical(e.message)

    