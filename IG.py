#!/usr/bin/env python
# encoding: utf-8
"""
IdeasGenerator.py

Created by VL and LN on 2012-08-15.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.

To do list:
[] implement smart correlations
[] set path for save files within gui
[] term management
[] make buttons tabable
[] bind return key to add a concept
[] delete item from list
[] set default behavior of text boxes and buttons
[] make window the default focus
"""
import os
import sys
import random as rand
from Tkinter import *
import tkMessageBox
import cPickle
import numpy as np
import igraph
import getpass
from pdb import *


# This will contain all the items and methods relevant to the items. 
class DataBase:
	def __init__(self):
		try:
			with open('save.p'): cPickle.load
			self.save_path = cPickle.load(open('save.p', 'rb'))
			self.load_pickle()
		except IOError:
			pass
				
	def append_to_graph(self, item):
		try:
			self.g
		except AttributeError:
			self.g = igraph.Graph()
			self.g.add_vertices(1)
			self.g.es["weight"] = 1.0
			self.g["name"] = "Ideas Graph"
			self.g.vs[0]["name"] = item
		else:
			self.g.add_vertices(1)
			number_of_vertices = self.g.vcount()
			self.g.vs[number_of_vertices-1]["name"] = item

	def draw_two(self):
		# Unconnected first.	
# 		try: 
# 			degree_fraction = [x/sum(self.g.vs.indegree()) for x in self.g.vs.indegree()]
# 		except ZeroDivisionError:
# 			degree_fraction = [1/self.g.vcount() for x in self.g.vs.indegree()]
# 			pass
# 		np.random.multinomial(2, *degree_fraction)

		unconnected_total_probability = 0.5
		#self.vertex_sequence_of_unconnected = self.g.vs.select(_degree_eq=0)
		
		pass_fail_gate = 0
		while pass_fail_gate==0:
			self.two_drawn = rand.sample(self.g.vs, 2)
			print pass_fail_gate
			# Query edge characteristics for pass/fail.
			# Identify the edge of the chosen vertices.
			try:
				self.count_of_selected_edge = self.g.es.select(_within = [self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"]
				self.weight_of_selected_edge = self.g.es.select(_within = [self.two_drawn[0].index, self.two_drawn[1].index])[0]["weight"]		
			except (IndexError, KeyError):
				self.count_of_selected_edge = 0
				self.weight_of_selected_edge = 3
				
			self.count_fail_probability = 0.90-(0.90/(self.count_of_selected_edge+1))
			
			if self.weight_of_selected_edge >= 0:
				self.weight_fail_probability = -(0.18*self.weight_of_selected_edge) + 0.90
			else:
				self.weight_fail_probability = 0.90
							
			total_fail_probability = (self.count_fail_probability + self.weight_fail_probability)/2
			
			draw_number = rand.random()
			if draw_number >= total_fail_probability:
				pass_fail_gate = 1
			else:
				pass
		
		return self.two_drawn[0]["name"], self.two_drawn[1]["name"]
		

	def save_graph(self):
		self.g.write_pickle(os.sep.join([self.save_path, "graph.p"]))
	
	def load_pickle(self):
		self.username=getpass.getuser()
		self.g = igraph.Graph.Read_Pickle(os.sep.join([self.save_path, "graph.p"]))
		
	def update_rating_in_edgelist(self, rating):
		self.g[self.two_drawn[0], self.two_drawn[1]] = rating
		try: 
			self.g.es.select(_within = [self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"] # start here
			self.g.es.select(_within = [self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"] = self.g.es.select(_within = [self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"] + 1
		except (IndexError, KeyError, TypeError):
			self.g.es.select(_within = [self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"] = 1
		self.save_graph()

class MainWindow:
	def __init__(self):
		self.DB = DataBase()
		self.MakeUI()
			
	def MakeUI(self):
		
		self.root = Tk()
		self.root.title("Tkinter Entry Widget")
		self.root["padx"] = 40
		self.root["pady"] = 20       
			
		# Create a text frame to hold the text Label and the Entry widget
		self.textFrame = Frame(self.root)		
				
		# Create a Label in textFrame
		self.entryLabel = Label(self.textFrame)
		self.entryLabel["text"] = "Enter the concept:"
		self.entryLabel.pack(side=LEFT)
	
		# Create an Entry Widget in textFrame
		self.entryWidget = Entry(self.textFrame)
		self.entryWidget["width"] = 50
		self.entryWidget.pack(side=LEFT)
		self.textFrame.pack()
		
		
		# Buttons
		self.add_button = Button(self.root, text="Add Concept", default="active", command=self.AddButtonPressed, takefocus=1)
		self.add_button.pack()

		self.generate_pair_button = Button(self.root, text="Generate Pair", default="normal", command=self.GeneratePairButtonPressed, takefocus=1)
		self.generate_pair_button.pack()
		
		self.display_database_button = Button(self.root, text="Display Database", default="normal", command=self.ManageDatabase, takefocus=1)
		self.display_database_button.pack()
		
		self.debug_mode_button = Button(self.root, text="Debug Mode", default="normal", command=self.DebugMode, takefocus=1)
		self.debug_mode_button.pack()
		
		self.set_save_path_button = Button(self.root, text="Set Save Path", default="normal", command=self.SetPathButtonPressed, takefocus=1)
		self.set_save_path_button.pack()
		
		# Recent data base items.
		self.databaselabelFrame = Frame(self.root)
		
		# Create a Label in textFrame
		self.databaseLabel = Label(self.databaselabelFrame)
		self.databaseLabel["text"] = "Recently Entered Items"
		self.databaseLabel.pack(side=TOP)
		
		self.databaselabelFrame.pack()
	
		self.databasedisplayFrame = Frame(self.root)
		# Create an Database Widget in textFrame
		self.databaseDisplay = Label(self.databasedisplayFrame)
		self.database_string = "No items yet"
		self.databaseLabel["text"] = self.database_string
		self.databaseDisplay.pack(side=TOP)
		
		self.databasedisplayFrame.pack()
		self.root.lift()
		self.root.mainloop()	
		
	def AddButtonPressed(self):
		global entryWidget
		
		if self.entryWidget.get().strip() == "":
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a text value")
		else:			
			self.DB.append_to_graph(self.entryWidget.get().strip())
			self.DB.save_graph()
			tkMessageBox.showinfo("Confirmation", self.entryWidget.get().strip() + " has been added.")
			self.entryWidget.delete(0, END)	
			
	def GeneratePairButtonPressed(self):
		RatingWindow(self)
					
	def ManageDatabase(self):
		for member_count, member in enumerate(self.DB.g.vs["name"]):
			print member_count
			if member_count==0:
				self.database_string = self.DB.g.vs[member_count]["name"]
			else:
				self.database_string = self.database_string+"\r"+self.DB.g.vs[member_count]["name"]
		tkMessageBox.showinfo("Display List", self.database_string)
		
		# To make the list more functional:
		# listbox = Listbox(master)
		# listbox.pack()
	
	def DebugMode(self):
		self.DB.g.write_svg("graph.svg", labels = "name", layout = self.DB.g.layout_kamada_kawai())
		set_trace()
	
	def SetPathButtonPressed(self):
		self.path_root = Tk()
		
		# Create a text frame to hold the text Label and the Entry widget
		self.path_textFrame = Frame(self.path_root)		
				
		# Create a Label in textFrame
		self.path_entryLabel = Label(self.path_textFrame)
		self.path_entryLabel["text"] = "Enter the save path:"
		self.entryLabel.pack(side=LEFT)
	
		# Create an Entry Widget in textFrame
		self.path_entryWidget = Entry(self.path_textFrame)
		self.path_entryWidget["width"] = 50
		self.path_entryWidget.pack(side=LEFT)
		self.path_textFrame.pack()
		
		self.path_root.title("Please set the path for save files")
		
		self.path_add_button = Button(self.path_root, text="OK", default="active", command=self.SetPath, takefocus=1)
		self.path_add_button.pack()
		
		self.path_root.mainloop()
	
	def SetPath(self):
		
		if self.path_entryWidget.get().strip() == "":
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a save path")
		else:
			self.DB.save_path = self.path_entryWidget.get().strip()
		
		cPickle.dump(self.DB.save_path, open('save.p', 'wb'))
		
		self.path_root.destroy()

class RatingWindow:
	def __init__(self, mainwindow):
		self.DB = mainwindow.DB
		self.mainwindow = mainwindow
		self.GeneratePair()
		self.MakeUI()
		
	def GeneratePair(self):
		self.Item1, self.Item2 = self.DB.draw_two()
		
	def MakeUI(self):
		
		self.root = Tk()
		self.root.title("Please give a rating")
     		
		# Create a text frame to hold the text Label and the Entry widget
		self.textFrame = Frame(self.root)	
						
		# Create a Label in textFrame
		self.entryLabel = Label(self.root, text=self.Item1 + "   " + self.Item2)
		self.entryLabel.pack()
		
		# Buttons
		button1 = Button(self.root, text="1", default="active", command = lambda: self.RatingButtonPressed(1), takefocus=1).pack()
		button2 = Button(self.root, text="2", default="active", command = lambda: self.RatingButtonPressed(2), takefocus=1).pack()
		button3 = Button(self.root, text="3", default="active", command = lambda: self.RatingButtonPressed(3), takefocus=1).pack()
		button4 = Button(self.root, text="4", default="active", command = lambda: self.RatingButtonPressed(4), takefocus=1).pack()
		button5 = Button(self.root, text="5", default="active", command = lambda: self.RatingButtonPressed(5), takefocus=1).pack()
		
		self.root.lift()
		self.root.mainloop()	
		
	def RatingButtonPressed(self, rating):
		self.DB.update_rating_in_edgelist(rating)
		self.root.destroy()
		self.mainwindow.GeneratePairButtonPressed()
		
def main():
	
	mainwindow = MainWindow()

if __name__ == '__main__':
    main()
		

		