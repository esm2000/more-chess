#!/usr/bin/env bash
nginx 
# prevents stdout of container from being 
# spammed with request logging from reverse proxy
nginx -s reload 
python backend/server.py