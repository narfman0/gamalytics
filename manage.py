#!/usr/bin/env python
import os
import sys
import logging

def addLogHandler(handler):
    handler.setLevel(logging.INFO)
    handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s.%(funcName)s():%(lineno)s - %(levelname)s - %(message)s'))
    logging.getLogger('gamalytics').addHandler(handler)
    
if __name__ == "__main__":
    addLogHandler(logging.FileHandler('gamalytics.log'))
    addLogHandler(logging.StreamHandler(sys.stdout))
    
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "gamalytics.settings")
    from django.core.management import execute_from_command_line
    execute_from_command_line(sys.argv)