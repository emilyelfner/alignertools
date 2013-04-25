# relabel.py
# coding: utf8

# This script will take an experiment file and generate new lab files for
# all of the .wav files in a directory. Old .lab files, if present, are
# stored in a new directory called "0_old_labfiles"
# Erin Olson erin.daphne.olson@gmail.com
# Current date: 2013/04/05

import csv
import glob
import codecs
from sys import exit
from shutil import move
from os import makedirs
from os.path import exists

def unicode_csv_reader(data, **kwargs):
	"""Enables all cells in a .csv file to be read as unicode strings."""
	data_file = csv.reader(data, **kwargs)
	for row in data_file:
		yield [unicode(cell, 'utf-8') for cell in row]

def parse(string, sep):
	"""Parse a string into a list."""
	id_list = []
	while string is not "":
		if sep not in string:
			id_list.append(string)
			string = ""
		else:
			index = string.index(sep)
			newstring = string[:index]
			id_list.append(newstring)
			string = string[index+1:]
	return id_list

def indexer(list1, list2):
	"""Find the index of an object in list1 if it matches an object in list2"""
	index_list = []
	for x in list1:
		for y in list2:
			if x == y:
				index = list1.index(x)
				index_list.append(index)
	return index_list

def reader(list, index_list):
	"""Read in relevant data from a list using a list of indexes"""
	newlist = []
	for i in index_list:
		newlist.append(list[i])
	return newlist

def find_replace(text, list):
	"""Finds and replaces characters given in a string.
	Characters to be replaced must be given as a list of ordered pairs."""
	for pair in list:
		if pair[0] in text:
			text = text.replace(pair[0], pair[1])
	return text

# set replacement list
#	- regular punctuation (removed): . , ! ? : ; " / ellipsis(u2026) enter tab
#	- special quotations (removed): left-quotes(u201c) right-quotes(u201c) high-quotes(u201f) low-single-quote(u201a) low-quotes(u201e) double-prime(u2033) angled-single-quotes(u2039 and u203a) angled-double-quotes(xab and xbb)
#	- unicode space (space): xa0
#	- single quotations ('): single-left-quote(u2018) single-right-quote(u2019) single-high-quote(u201b) prime(u2032)
#	- hyphens (-): soft-hypen(xad) en-dash(u2013) no-break(u2011) em-dash(u2014) figure(u2012)
replist =[[u".",u""], [u",",u""], [u"!",u""], [u"?",u""], [u":",u""], [u";",u""], [u'"',u""], [u"/",u""], [u"\n",u""], [u"\\n",u""], [u"\t",u""], [u"\u2026",u""], [u"\\", u""], 
	[u"\u201c",u""], [u"\u201d",u""], [u"\u201f",u""], [u"\u201a",u""], [u"\u201e",u""], [u"\u2033",u""], [u"\u2039",u""], [u"\u203a",u""], [u"\xab",u""], [u"\xbb",u""], 
	[u"\xa0",u" "], [u"\u2018",u"'"],
	[u"\u2019",u"'"], [u"\u201b",u"'"], [u"\u2032",u"'"], 
	[u"\xad",u"-"], [u"\u2013",u"-"],[u"\u2011",u"-"], [u"\u2014",u"-"], [u"\u2012",u"-"]]

# user form
print """relabel\n
What are the experiment files? (must include directory)
You can drag and drop the files into the Terminal window to fill out this space
WARNING: No individual directory should include a space chacter
If so, please go back and replace any spaces with underscores"""
exp_file_names = raw_input("> ")
if exp_file_names[-1] == ' ':
	chars = list(exp_file_names)
	chars[-1] = ''
	exp_file_names = "".join(chars)
print """
What are the id columns of the experiment file?
Default is: experiment_item_condition
Press enter to use default"""
exp_string = unicode(raw_input("> "), 'utf-8')
if exp_string == '':
	exp_string = "experiment_item_condition"
print """
What is the sound directory?
You can drag and drop the file into the Terminal window to fill out this space"""
sounddir = raw_input("> ")
if sounddir[-1] == ' ':
	sounddir = sounddir.replace(" ", '')
if sounddir[-1] != '/':
	sounddir = sounddir + '/'
print """
What are the id columns of the sound file?
Default is: experiment_participant_item_condition
Press enter to use default"""
sound_string = unicode(raw_input("> "), 'utf-8')
if sound_string == '':
	sound_string = "experiment_participant_item_condition"
print """
What would you like to call the directory for the old lab files?
Default is: 0_old_labfile_relabel/
Press enter to use default"""
olddir = raw_input("> ")
if olddir == '':
	olddir = "0_old_labfile_relabel/"
if olddir[-1] != '/':
	olddir = olddir + "/"

# parse name formats; get indices for names
column_names = parse(exp_string, "_")
file_name_format = parse(sound_string, "_")
name_index = indexer(file_name_format, column_names)

# parse experiment files; assign labels
files = parse(exp_file_names, " "); exp_files = []
for file in files:
	exp_file = [x[:] for x in unicode_csv_reader(open(file,'rU'),delimiter='\t')]
	exp_files.append(exp_file)

# check to see if there is a directory of old lab files; make if not
goodname = False
while goodname == False:
	if exists(sounddir + olddir):
		print """Directory already exists!
Please pick a new directory name for old lab files:"""
		olddir = raw_input("> ")
		if olddir[-1] != '/':
			olddir = olddir + '/'
	else:
		goodname = True
makedirs(sounddir + olddir)

# get indices for columns
titles = []
for file in exp_files:
	title = file.pop(0)
	titles.append(title)
column_indices = []
for title in titles:
	c_index = indexer(title, column_names)
	column_indices.append(c_index)
		
# find the column index that will have the relevant text
lab_indices = []
for title in titles:
	if u"lab" in title:
		lab_index = title.index(u"lab")
	elif u"text" in title:
		lab_index = title.index(u"text")
	else:
		ind = titles.index(title)
		print files[ind]
		exit("This experiment file does not have a lab or a text column!")
	lab_indices.append(lab_index)

# make a list of the soundfiles in the directory
soundfiles = glob.glob(sounddir+"*.wav")

for file in soundfiles:
	# get a useable file name; make a lab file name
	filename = file.replace(sounddir, '')
	filename = filename.replace('.wav', '')
	labname = filename + '.lab'
	
	# parse file name; store useful parts to list
	parsed_filename = parse(filename, "_")
	bits = reader(parsed_filename, name_index)
	
	# find the right row in the experiment file
	row_found = False
	for file in exp_files:
		ndx = exp_files.index(file)
		for row in file:
			exp_bits = reader(row, column_indices[ndx])
			if exp_bits == bits:
				row_found = True; row_index = file.index(row); file_index = exp_files.index(file)
	
	# if the row is found, remove current lab file
	if row_found == True:
		if exists(sounddir + filename + '.lab'):
			move(sounddir + labname, sounddir + olddir + labname)
		lab_index = lab_indices[file_index]
		lab_text = exp_files[file_index][row_index][lab_index]
		
		# replace problematic characters
		lab_text = find_replace(lab_text, replist)
		lab_text = lab_text.encode('utf-8')
		
		print lab_text
		labfile = open(sounddir + labname, 'w')
		labfile.write(lab_text)
		labfile.close()