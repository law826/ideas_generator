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
from __future__ import division
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
		return self.two_drawn[0]["name"], self.two_drawn[1]["name"], self.count_of_selected_edge, self.weight_of_selected_edge, self.total_fail_probability


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
				

			#self.count_fail_probability = 0.90-(0.90/(self.count_of_selected_edge+1))
			self.weight_fail_probability = -(0.18*(self.weight_of_selected_edge-1)) + 0.90
							
			self.total_fail_probability = self.weight_fail_probability
			
			draw_number = rand.random()
			if draw_number >= self.total_fail_probability:
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

	def update_comment(self, comment):
		self.g.es.select(_within=[self.two_drawn[0].index, self.two_drawn[1].index])[0]["comment"] = comment

	def retrieve_comment(self):
		try:
			self.comment = self.g.es.select(_within=[self.two_drawn[0].index, self.two_drawn[1].index])[0]["comment"]
		except (IndexError, KeyError, TypeError):
			self.comment = "Insert comments here"

		return self.comment

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

		self.LabelEntryUI()
		self.ButtonsUI()

		self.DB = DataBase(self) # Instantiated here at the end because of parent window issues for ask directory widget.

		self.GraphStatisticsUI()

		self.root.lift()
		self.root.mainloop()

	def LabelEntryUI(self):
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

	def ButtonsUI(self):
		button_labels = [
			'Add Concept', 
			'Generate Pair', 
			'Database Manager', 
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
			b = Button(self.root, text=label, default="normal", command=button_commands[button_number]).pack()

	def GraphStatisticsUI(self):
		self.SetGraphStatistics()
		self.nodeFrame = Frame(self.root)
		self.edgeFrame = Frame(self.root)
		self.percentageFrame = Frame(self.root)

		self.node_count_label = Label(self.nodeFrame, text="Nodes = ").pack(side = LEFT)
		self.node_count_label_number = Label(self.nodeFrame, textvariable=self.node_count).pack(side = LEFT)
		self.edge_count_label = Label(self.edgeFrame, text="Edges = ").pack(side = LEFT)
		self.edge_count_label_number = Label(self.edgeFrame, textvariable=self.edge_count).pack(side = LEFT)
		self.percentage_count_label = Label(self.percentageFrame, text="Percentage of explored edges = ").pack(side = LEFT)
		self.percentage_count_label_number = Label(self.percentageFrame, textvariable=self.percentage).pack(side = LEFT)



		self.nodeFrame.pack()
		self.edgeFrame.pack()
		self.percentageFrame.pack()
			
	def AddButtonPressed(self, event=0):
		if self.entryWidget.get().strip() == "":
			tkMessageBox.showerror("Tkinter Entry Widget", "Enter a text value")
		else:			
			self.DB.append_to_graph(self.entryWidget.get().strip())
			self.DB.save_graph()
			tkMessageBox.showinfo("Confirmation", "%s has been added." % self.entryWidget.get().strip())
			self.entryWidget.delete(0, END)	
		self.SetGraphStatistics()
		self.entryWidget.focus_set()
		
	def GeneratePairButtonPressed(self):
		RatingWindow(self)
					
	def ManageDatabaseButtonPressed(self):
		ManageDatabaseWindow(self.DB)
	
	def DebugModeButtonPressed(self):
		#self.DB.g.write_svg("graph.svg", labels = "name", layout = self.DB.g.layout_kamada_kawai())
		set_trace()

	def SetGraphStatistics(self):
		try: 
			self.node_count
		except AttributeError:
			self.node_count = StringVar()
			self.edge_count = StringVar()
			self.percentage = StringVar()
		self.node_count.set(len(self.DB.g.vs))
		self.edge_count.set(len(self.DB.g.es))

		self.percentage_of_edges = len(self.DB.g.es)/sum(range(len(self.DB.g.vs)))
		self.percentage.set(str('%.2f') % self.percentage_of_edges)

	def SetPath(self):
		self.DB.save_path = tkFileDialog.askdirectory(title = 'Please choose a save directory')


class ManageDatabaseWindow:
	def __init__(self, database):
		self.DB = database
		self.root = Tk()
		self.root.title("Database Manager")
		self.MakeListBox()
		mainloop()

	def MakeListBox(self):	
		self.listbox = Listbox(self.root)
		self.listbox.pack()
		self.b = Button(self.root, text = "Delete", command = self.DeleteItem)
		self.b.pack()
		for concept in self.DB.g.vs["name"]:
			self.listbox.insert(END, concept)


	def DeleteItem(self):
		selected_index = self.listbox.curselection()
		selected_concept = self.listbox.get(selected_index)

		result = tkMessageBox.askquestion("Delete", "Are you sure you want to delete %s?" %selected_concept, icon='warning')
		if result == 'yes':
			vertex_index = self.DB.g.vs.find(name=selected_concept).index
			self.DB.g.delete_vertices(vertex_index)
			self.listbox.pack_forget()
			self.b.pack_forget()
			self.MakeListBox()
			self.DB.save_graph()
			tkMessageBox.showinfo("Term deleted", "%s has been deleted." %selected_concept)
		else:
			pass

class RatingWindow:
	def __init__(self, mainwindow):
		self.DB = mainwindow.DB
		self.mainwindow = mainwindow
		self.GeneratePair()
		self.MakeUI()
		
	def GeneratePair(self):
		self.Item1, self.Item2, self.count, self.weight, self.total_fail_probability = self.DB.draw_two()
		
	def MakeUI(self):
		
		# Initializing UI.
		self.root = Tk()
		self.root.title("Please give a rating")
     						
		# Create a Label in textFrame
		self.pairLabel = Label(self.root, text="%s    %s" % (self.Item1, self.Item2), font=("Helvetica", 24, "bold")).pack()
		self.countweightLabel = Label(self.root, text='weight = %s count = %s\r fail probability = %s' %(str(self.weight), str(self.count), str(self.total_fail_probability))).pack()
		
		# Create a button frame to hold the buttons horizontally.
		self.buttonFrame = Frame(self.root)
		self.buttonFrame.pack()

		# Buttons
		buttons = [1, 2, 3, 4, 5]
		for button in buttons:
			b = Button(self.buttonFrame, text=str(button), command = lambda: self.RatingButtonClicked(button)).pack(side = LEFT)

		# Binding of buttons (including in above seems to throw an error)
		for button in buttons:
			self.buttonFrame.bind("<KeyRelease-%s>" % button, self.RatingButtonPressed)	

		# Add comments to the edge.
		self.comments_box = Text(self.root, width=40, height = 10, takefocus=1, wrap = WORD)

		self.comments = self.DB.retrieve_comment()

		self.comments_box.bind("<Button-1>", self.ClearDefaultComments)

		try: 
			self.comments_box.insert('1.0', self.comments)
		except TclError:
			pass
		self.comments_box.pack()

		self.root.bind("<KeyRelease-c>", self.ClearDefaultComments)
		self.root.bind("<Escape>", self.RatingsFocusSet)

		# Last elements of UI.
		self.root.lift()
		self.buttonFrame.focus_set()		
		self.root.mainloop()

	def SaveComments(self):
		self.comments = self.comments_box.get('1.0', 'end') 
		self.DB.update_comment(self.comments)

	def RatingsFocusSet(self, event):
		self.buttonFrame.focus_set()

	def ClearDefaultComments(self, event):
		if self.comments_box.get('1.0', 'end')  == u'Insert comments here\n':
			self.comments_box.delete(1.0, END)
		self.comments_box.focus_set()

	def RatingButtonClicked(self, rating):
		self.DB.update_edge(rating)
		self.SaveComments()
		self.mainwindow.SetGraphStatistics()
		self.root.destroy()
		self.mainwindow.GeneratePairButtonPressed()
	
	def RatingButtonPressed(self, event):
		rating = float(event.char)
		self.RatingButtonClicked(rating)


		
def main():
	
	mainwindow = MainWindow()

if __name__ == '__main__':
    main()
		

		