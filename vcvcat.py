#!/usr/bin/python3

'''
vcvcat v0.1
This program concatenates two .vcv patch files

vcvcat is copyright © 2020 S. Edel, https://se-it.eu

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Affero General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.

'''

import argparse
import os
import sys
import json

def eprint(*args, **kwargs):
	print(*args, file=sys.stderr, **kwargs)

def bye(msg=None, code=1):
	if msg:
		eprint(msg)
	else:
		parser.print_help(sys.stderr)
	sys.exit(code)

class minmax:
	def __init__(self, obj):
		self.maxrow = self.minrow = obj["modules"][0]["pos"][1]
		self.maxcol = self.mincol = obj["modules"][0]["pos"][0]
		for mod in obj["modules"]:
			self.maxrow = max(self.maxrow, mod["pos"][1])
			self.minrow = min(self.minrow, mod["pos"][1])
			self.maxcol = max(self.maxcol, mod["pos"][0])
			self.mincol = min(self.mincol, mod["pos"][0])

class ids:
	def __init__(self, obj):
		self.values = set()
		for mod in obj["modules"]:
			self.values.add(mod["id"])
		for cab in obj["cables"]:
			self.values.add(cab["id"])

def warn_keys(d, filename):
	known_keys = [ "version", "modules", "cables"]
	for key in d.keys():
		if key not in known_keys:
			eprint("Warning: unknown key '" + key + "' in " + filename  + " - merge may be incomplete.")
			eprint(" Please check for a new version of this script")

def main():
	parser = argparse.ArgumentParser(prog='vcvcat', description="Combine two vcv patches into a new one")
	parser.add_argument('in1', type=argparse.FileType('r'), help='first input file name')
	parser.add_argument('in2', type=argparse.FileType('r'), help='second input file name')
	parser.add_argument('out', type=str, help='output file name')
	args = parser.parse_args()

	in1 = json.load(args.in1)
	args.in1.close()
	in2 = json.load(args.in2)
	args.in2.close()

	if in1["version"] != in2["version"]:
		bye("These patches come from different versions of VCVRack.\n Please save them with the same version of VCVRack and retry")
	warn_keys(in1, args.in1.name)
	warn_keys(in2, args.in2.name)

	mm1 = minmax(in1)
	mm2 = minmax(in2)
	for mod in in2["modules"]:
		mod["pos"][1] += mm1.maxrow + 1

	ids1 = ids(in1)
	ids2 = ids(in2)
	inter = sorted(ids1.values.intersection(ids2.values))
	maxid = max(ids1.values.union(ids2.values))
	replace = dict()
	for x in inter:
		maxid += 1
		replace[x] = maxid

	for mod in in2["modules"]:
		for key in ["id", "leftModuleId", "rightModuleId"]:
			if key in mod:
				if mod[key] in inter:
					mod[key] = replace[mod[key]];

	for cab in in2["cables"]:
		for key in ["id", "inputModuleId", "outputModuleId"]:
			if key in cab:
				if cab[key] in inter:
					cab[key] = replace[cab[key]];

	out = dict()
	out["version"] = in1["version"]
	out["modules"] = in1["modules"] + in2["modules"]
	out["cables"] = in1["cables"] + in2["cables"]
	with open(args.out, 'x') as f:
		json.dump(out, f, indent=2, sort_keys=True)

if __name__ == "__main__":
	main()
