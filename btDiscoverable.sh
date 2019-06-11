#!/bin/sh
sleep 20
sudo hciconfig hci0 up
sudo hciconfig hci0 sspmode1
sudo hciconfig hci0 piscan
