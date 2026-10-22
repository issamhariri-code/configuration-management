#!/usr/bin/env python3
import json
import argparse
with open('/home/issam/lab9/servers.json', 'r') as file:
	servers = json.load(file)

parser = argparse.ArgumentParser()
parser.add_argument("--list", action="store_true")
parser.add_argument("--host")
args = parser.parse_args()
if args.list:

	servers = json.dumps(servers)
	print(servers)
elif args.host:
	print(json.dumps({}))
