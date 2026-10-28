#!/usr/bin/env python3
import json
import argparse
from pathlib import Path
with open(Path(__file__).resolve().with_name('servers.json'), 'r', encoding='utf-8') as file:
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
