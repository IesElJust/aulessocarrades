#!/bin/bash

pgrep -f "/home/admin/dht11_send.py" > /dev/null || /home/admin/dht11_send.py >> /home/admin/dht11_send.log 2>&1
