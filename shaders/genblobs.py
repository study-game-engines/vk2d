###################### genblobs.py ######################
#                  Author: Paolo Mazzon                 #
#                                                       #
# genblobs.py is a tool to compile glsl into spv then   #
# turn it into hex blobs in VK2D under VK2D/Blobs.h.    #
#                                                       #
# Usage: python genblobs.py <input files>               #
# Blobs.h will name the variables as follows:           #
#     VK2D<extension><name>                             #
# Where name and extension both have their first letter #
# capitalized.                                          #
#                                                       #
#     ONLY CALL THIS FROM THE ROOT PROJECT DIRECTORY    #
#########################################################
from subprocess import call
from os import listdir, path, remove
from sys import platform, argv

# Finds the exe for glslc, returning the full path
def find_glslc():
	sdk = ""
	if (platform == "linux" or platform == "linux2"):
		return "glslc" # TODO: Test this
	if (path.exists("/C/VulkanSDK")):
		for f in listdir("/C/VulkanSDK"):
			if (path.isdir("/C/VulkanSDK/" + f)):
				sdk = f
	
	if (sdk == ""):
		print("Failed to locate VulkanSDK")
	
	return "/C/VulkanSDK/" + sdk + "/Bin/glslc.exe"

# Converts a filename to a fancy variable name
def filename_to_variable(filename):
	period = filename.rfind(".")
	slash = filename.rfind("/")
	suffix = filename[slash + 1:period]
	prefix = filename[period+1:]
	return "VK2D" + prefix[0].upper() + prefix[1:] + suffix[0].upper() + suffix[1:]

# Reads a file into a byte array and returns it
def load_file_as_binary(file):
	s = ""
	with open(file, "rb") as f:
		s = f.read()
	return s

# Takes a list of filenames and turns them into spv files returning the files
# as strings in the form {"<variablename>": "<filecontents>", ...}
def compile_shaders(shaders):
	outmap = {}
	glslc = find_glslc()
	for filename in shaders:
		call([glslc, filename])
		outmap[filename_to_variable(filename)] = load_file_as_binary("a.spv")
	remove("a.spv")
	return outmap

# Converts an 8-bit number to a four-digit hex string (eg, 0x3E)
def bin_to_4hex(bin):
	out = hex(bin)
	if (len(out) == 3):
		return out[0] + out[1] + "0" + out[2]
	else:
		return out

# Turns the map from compile_shaders into a C header file and returns it as a string
def compile_blob_file(shader_map):
	outstring = """/// \\file Blobs.h
/// \\author Paolo Mazzon (via genblobs.py)
/// \\brief Shader binary blobs
#pragma once\n\n"""
	for key, val in shader_map.items():
		outstring += "const char " + key + "[] = {"
		counter = 0
		for i in val:
			if (counter % 15 == 0): outstring += "\n\t"
			counter += 1
			outstring += bin_to_4hex(i) + ", "
		outstring = outstring[:-2] + "\n};\n\n"
	
	return outstring[:-2]

def main():
	if (len(argv) > 1):
		header = compile_blob_file(compile_shaders(argv[1:]))
		with open("VK2D/Blobs.h", "w") as f:
			f.write(header)
		print("Done.")
	else:
		print("No input files.")

if (__name__ == "__main__"):
	main()