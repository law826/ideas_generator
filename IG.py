#!/usr/bin/env python
# encoding: utf-8
"""
IdeasGenerator.py

Created by VL and LN on 2012-08-15.
Copyright (c) 2012 __MyCompanyName__. All rights reserved.

To do list:
[] build a way to focus on a particular term (for problem solving)
[] support for multiple users
[] implement smart correlations
[] set path for save files within gui
[] term management
[] make buttons tabable
[] delete item from list
[] set default behavior of text boxes and buttons
[] make window the default focus
"""
import os
import sys
import random as rand
from Tkinter import *
import tkMessageBox
import tkFileDialog 
import cPickle
import numpy as np
import igraph
import getpass
from pdb import *

# This will contain all the items and methods relevant to the items. 
class DataBase:
	def __init__(self, mainwindow):
		self.mainwindow = mainwindow
		self.load_user_settings()
		try:
			self.load_graph()
		except (cPickle.UnpicklingError):
			pass
		
	def load_user_settings(self):
		try: 
			self.user_settings = cPickle.load(open('user_settings.p', 'rb'))
			if os.getcwd() in self.user_settings:
				self.save_path = self.user_settings[os.getcwd()]
			else:
				tkMessageBox.showinfo("New User/Computer Detected. Please choose a save directory.")	
				self.SetPath()
		except (IOError, cPickle.UnpicklingError):
			self.user_settings = dict()
			tkMessageBox.showinfo("New User/Computer Detected", "Please choose a save directory.")
			self.SetPath()

	def load_graph(self):
		self.g = igraph.Graph.Read_Pickle(os.sep.join([self.save_path, "graph.p"]))
				
	def save_graph(self):
		try:
			self.g.write_pickle(os.sep.join([self.save_path, "graph.p"]))
		except:
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a valid save path (current path is %s)" %self.save_path)
		
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
		self.random_with_count_weight_fail_gate()
		return self.two_drawn[0]["name"], self.two_drawn[1]["name"], self.count_of_selected_edge, self.weight_of_selected_edge


		# Unconnected first.	
# 		try: 
# 			degree_fraction = [x/sum(self.g.vs.indegree()) for x in self.g.vs.indegree()]
# 		except ZeroDivisionError:
# 			degree_fraction = [1/self.g.vcount() for x in self.g.vs.indegree()]
# 			pass
# 		np.random.multinomial(2, *degree_fraction)

		#unconnected_total_probability = 0.5
		#self.vertex_sequence_of_unconnected = self.g.vs.select(_degree_eq=0)

	def random_with_count_weight_fail_gate(self):

		pass_fail_gate = 0
		while pass_fail_gate==0:
			self.two_drawn = rand.sample(self.g.vs, 2)
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

	def betweenness_max_vertex_search(self):

		non_zero_normed_edgeseq = self.g.es.select(weight_count_normed_gt=1)
		non_zero_edge_index_list = [edge.index for edge in non_zero_normed_edgeseq]
		non_zero_graph = self.g.subgraph_edges(non_zero_edge_index_list)
		betweenness = non_zero_graph.betweenness(weights='weight_count_normed')
		max_betweenness = max(betweenness)
		max_betweenness_vertex_list_pos = [i for i, j in enumerate(betweenness) if j == max_betweenness][0]
		max_vertex = non_zero_graph.vs[max_betweenness_vertex_list_pos]
		return max_vertex

	def update_edge(self, rating):
		self.g[self.two_drawn[0], self.two_drawn[1]] = rating
		try: 
			edge_count = self.g.es.select(_within=[self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"] # start here
			self.g.es.select(_within=[self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"] = edge_count + 1
		except (IndexError, KeyError, TypeError):
			self.g.es.select(_within=[self.two_drawn[0].index, self.two_drawn[1].index])[0]["count"] = 1
			edge_count=1
		self.g.es.select(_within=[self.two_drawn[0].index, self.two_drawn[1].index])[0]["weight_count_normed"] = rating/edge_count # Normalized weight count attribute.
		self.save_graph()

	def SetPath(self):
		self.save_path = tkFileDialog.askdirectory(parent = self.mainwindow.root, title = 'Please choose a save directory')
		self.user_settings[os.getcwd()] = self.save_path
		cPickle.dump(self.user_settings, open('user_settings.p', 'wb'))		

class MainWindow:
	def __init__(self):
		self.MakeUI()
			
	def MakeUI(self):
		
		self.root = Tk()
		self.root.title("Ideas Generator")
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
		self.entryWidget.focus_set()
		self.entryWidget.bind("<Return>", self.AddButtonPressed)
		self.textFrame.pack()
		
		# Buttons
		button_labels = [
			'Add Concept', 
			'Generate Pair', 
			'Manage Database', 
			'Debug Mode', 
			'Set Save Path', 
			]

		button_commands = [
			self.AddButtonPressed,
			self.GeneratePairButtonPressed,
			self.ManageDatabaseButtonPressed,
			self.DebugModeButtonPressed,self.SetPath,
			self.SetPath
			]

		for button_number, label in enumerate(button_labels):
			b = Button(self.root, text=label, default="normal", command=button_commands[button_number], takefocus=1).pack()
		
		self.root.lift()

		self.DB = DataBase(self) # Instantiated here at the end because of parent window issues for ask directory widget.
		self.root.mainloop()	
			
	def AddButtonPressed(self, event=0):
		if self.entryWidget.get().strip() == "":
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a text value")
		else:			
			self.DB.append_to_graph(self.entryWidget.get().strip())
			self.DB.save_graph()
			tkMessageBox.showinfo("Confirmation", "%s has been added." % self.entryWidget.get().strip())
			self.entryWidget.delete(0, END)	
		self.entryWidget.focus_set()
		
	def GeneratePairButtonPressed(self):
		RatingWindow(self)
					
	def ManageDatabaseButtonPressed(self):
		for member_count, member in enumerate(self.DB.g.vs["name"]):
			if member_count==0:
				self.database_string = self.DB.g.vs[member_count]["name"]
			else:
				self.database_string = self.database_string+"\r"+self.DB.g.vs[member_count]["name"]
		tkMessageBox.showinfo("Display List", self.database_string)
		
		# To make the list more functional:
		# listbox = Listbox(master)
		# listbox.pack()
	
	def DebugModeButtonPressed(self):
		#self.DB.g.write_svg("graph.svg", labels = "name", layout = self.DB.g.layout_kamada_kawai())
		set_trace()

	def SetPath(self):
		self.DB.save_path = tkFileDialog.askdirectory(title = 'Please choose a save directory')

class RatingWindow:
	def __init__(self, mainwindow):
		self.DB = mainwindow.DB
		self.mainwindow = mainwindow
		self.GeneratePair()
		self.MakeUI()
		
	def GeneratePair(self):
		self.Item1, self.Item2, self.count, self.weight = self.DB.draw_two()
		
	def MakeUI(self):
		
		self.root = Tk()
		self.root.title("Please give a rating")
     		
		# Create a text frame to hold the text Label and the Entry widget
		self.textFrame = Frame(self.root)	
						
		# Create a Label in textFrame
		self.pairLabel = Label(self.root, text="%s    %s" % (self.Item1, self.Item2)).pack()
		self.countweightLabel = Label(self.root, text='weight = ' + str(self.weight) + "   " + 'count = ' + str(self.count)).pack()
		
		# Buttons
		buttons = [1, 2, 3, 4, 5]
		for button in buttons:
			b = Button(self.root, text=str(button), default="active", command = lambda: self.RatingButtonClicked(button)).pack()

		# Binding of buttons (including in above seems to throw an error)
		for button in buttons:
			self.root.bind("<KeyRelease-%s>" % button, self.RatingButtonPressed)	

		self.root.lift()
		self.root.mainloop()

	def RatingButtonClicked(self, rating):
		self.DB.update_edge(rating)
		self.root.destroy()
		self.mainwindow.GeneratePairButtonPressed()		
		
	def RatingButtonPressed(self, event):
		self.DB.update_edge(float(event.char))
		self.root.destroy()
		self.mainwindow.GeneratePairButtonPressed()
		
def main():
	
	mainwindow = MainWindow()

if __name__ == '__main__':
    main()
		

		