#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runs a rating experiment (Likert scale) - single stimulus assessment
(only distorted image is presented)

It runs through a design file in csv format, which should contain the filenames of the
images to be displayed.

From the command line pass the name of the design file as the first parameter
E.g.

python rating_experiment_single.py mydesignfile.csv

It saves the responses from the observer in a results file.


v2: it allows unlimited or limited presentation time. Change the global variable
    presentation_time


Seminar: Image quality and human visual perception, SoSe 2020, TU Berlin
@author: G. Aguilar, June 2020

"""

import csv
import datetime
import sys
import pyglet
from pyglet import window
from pyglet import clock
from pyglet.window import key
from pathlib import Path



## Excerpt from Bosse (2018) p. 11
#In single stimulus assessment methods, e.g. Single Stimulus (SS) [ITU-R Rec. BT.500-13, 2012]
# or Absolute Cateogry Rating (ACR) [ITU-T Rec. P.910, 2008], the quality of the 
# test condition is assessed by the participant without comparison to a reference 
# condition. In ACR, the opinion scores are given with respect to the absolute quality 
# and the rating scale carries semantic annotations as 
# 1-Bad, 2-Poor, 3-Fair, 4-Good and 5-Excellent.


instructions = """
Welcome!\n
Rating experiment - Single stimulus assessment\n
Sie werden im folgenden Experiment immer genau ein Bild sehen.
Sie wählen für jedes Bild eine Zahl zwischen 1-5, welche widerspiegelt, für wie stark bearbeitet Sie das Bild empfinden.\n
Wobei 1 für, garnicht bearbeitet steht und 5 für sehr stark!\n
Drücken Sie bevor Sie beginnen 'y', wenn Sie Instagram verwenden.\n Und 'n' wenn nicht.\n
Drücken Sie Enter zum bestätigen und starten.
Drücken Sie ESC um das Experiment zu beenden."""

instructions_ontrial = """ 1: unedited - ... - 5: heavily edited """


## stimulus presentation time variable
#presentation_time = 1 # presentation time in seconds, None for unlimited presentation
presentation_time = None


def read_design_csv(fname):
    """ Reads a CSV design file and returns it in a dictionary"""
    
    design = open(fname)
    header = design.readline().strip('\n').split(',')
    #print header
    data   = design.readlines()
    
    new_data = {}
    
    for k in header:
        new_data[k] = []
    for l in data:
        curr_line = l.strip().split(',')
        for j, k in enumerate(header):
            new_data[k].append(curr_line[j])
    return new_data


###############################################################################
class Experiment(window.Window):
    

    def __init__(self, *args, **kwargs):

        #Let all of the arguments pass through
        self.usage = ""
        self.win = window.Window.__init__(self, *args, **kwargs)
        
        self.debug = False
        
        
        clock.schedule_interval(self.update, 1.0/30) # update at FPS of Hz
        
        # Setting up text objects
        self.welcome_text = pyglet.text.Label(instructions,
                                  font_name='Arial', multiline=True,
                                  font_size=25, x=int(self.width/2.0), y=int(self.height/2.0),
                                  width=int(self.width*0.75), color=(0, 0, 0, 255),
                                  anchor_x='center', anchor_y='center')
        
        self.instructions_ontrial = pyglet.text.Label(instructions_ontrial,
                                  font_name='Arial', multiline=False,
                                  font_size=20, x=int(self.width/2.0), y=int(self.height*0.1),
                                  width=int(self.width*0.75), color=(0, 0, 0, 255),
                                  anchor_x='center', anchor_y='center')
    
                
        # Design file
        global designfile
        self.designfile = designfile
        
        # Results file - assigning filename
        s = designfile.split('.')
        s[-1] = '_results.csv'
        self.resultsfile = ''.join(s)



        # Results file - assigning filename
        self.resultsfile = 'single_results/single_result_1.csv'

        file = Path(self.resultsfile)
        index = 2

        # prevents result from being replaced by new results
        while file.is_file():
            self.resultsfile = 'single_results/single_result_' + str(index) + '.csv'
            file = Path(self.resultsfile)
            index += 1


        
        # opening the results file, writing the header
        self.rf = open(self.resultsfile, 'w')
        self.resultswriter = csv.writer(self.rf)  
        header = ['usage', 'image', 'filter', 'intensity', 'response', 'resptime']
        self.resultswriter.writerow(header)
    
        
        # experiment control 
        self.experimentphase = 0 # 0 for intro, 1 for running trials, 2 for good bye
        self.firstframe = True
        self.present_stim = True
        
        # calling some routines on start
        self.loaddesign()
        # forces a first draw of the screen
        self.dispatch_event('on_draw')

        self.test_position = 0.5
        
    def loaddesign(self):
        """ Loads the design file specifications"""
        self.design = read_design_csv(self.designfile)
        self.totaltrials = len(self.design['image'])
        
        if self.debug:
            print(self.design)
            print('total number of trials: %d ' % self.totaltrials)
            
        self.currenttrial = 0
    
    def update(self, dt):
        pass
    
    def on_draw(self):
        """ Executed when draws on the screen"""
        
        
        # clear the buffer
        pyglet.gl.glClearColor(1.0, 1.0, 1.0, 1.0)
        self.clear()
        
        # ticks the clock
        #dt = clock.tick() # ticking the clock
        #print(f"FPS is {clock.get_fps()}")
        
        
        if self.debug:
            print('-------- ondraw')
            print('self.present_stim %d' % self.present_stim)
        
        
        if self.experimentphase == 0:
            if self.debug:
                print('experiment phase 0: welcome')
            # draws instruction text
            self.welcome_text.draw()
            
        # go through the trials 
        elif self.experimentphase == 1:
            
            if self.debug:
                print('experiment phase 1: going through the trials')
            
            
            # load images only on the first frame
            if self.firstframe:
                print('trial: %d' % self.currenttrial)
            
                # load images
                self.load_images()
                
                # saves presentation time
                self.stimstarttime =  datetime.datetime.now()
            
           
            # draw images on the screen for a limited time
            if (presentation_time is None) or (self.present_stim):
                self.test_image.blit(int(self.width*self.test_position), int(self.height*0.5))
            
            
            # draw instruction text
            self.instructions_ontrial.draw()

            
            # timing
            self.firstframe = False
            
            # checking if stim time has passed
            if presentation_time is not None and self.present_stim:
                deltat = datetime.datetime.now() - self.stimstarttime
                
                if deltat.total_seconds() > presentation_time:
                    self.present_stim = False
            
        elif self.experimentphase == 2:
            if self.debug:
                print('experiment phase 2: goodbye')
            self.dispatch_event('on_close')  
            
        
        # flipping the buffers
        self.flip()
        #pyglet.gl.glFlush()
    
    def checkcontinue(self):
        """ Checks if we're at the end of the trials"""
        self.firstframe = True
        self.present_stim = True
        
        if self.currenttrial>=self.totaltrials:
             self.experimentphase = 2
             #self.dispatch_event('on_close')  
             
        
    def load_images(self):
        """ Loads images of current trial """
        # load files 
        if self.debug:
            print('loading files')
            
        self.test_image = pyglet.image.load("single_images_tiny/" + self.design['image'][self.currenttrial])
        
        # changes anchor to the center of the image
        self.test_image.anchor_x = self.test_image.width // 2
        self.test_image.anchor_y = self.test_image.height // 2
        


    def savetrial(self, resp, resptime):
        """ Save the response of the current trial to the results file """
        
        row = [self.usage, self.design['image'][self.currenttrial],
               self.design['filter'][self.currenttrial],
               self.design['intensity'][self.currenttrial],
               resp, resptime]
        self.resultswriter.writerow(row)
        print('Trial %d saved' % self.currenttrial)
        
        
    ## Event handlers
    def on_close(self):
        """ Executed when program finishes """
        
        self.rf.close() # closing results csv file
        self.close() # closing window
        
    def on_key_press(self, symbol, modifiers):
        """ Executed when a key is pressed"""
        
        if symbol == key.ESCAPE:
            self.dispatch_event('on_close')  

        if symbol == key.Y:
            self.usage = 'yes'

        if symbol == key.N:
            self.usage = 'no'

        elif (symbol == key.NUM_1 or symbol == key._1) and self.experimentphase==1:
            print("Press: 1")
            deltat = datetime.datetime.now() - self.stimstarttime
            self.savetrial(resp=1, resptime = deltat.total_seconds())
            self.currenttrial += 1
            self.checkcontinue()
            
        elif (symbol == key.NUM_2 or symbol == key._2) and self.experimentphase==1:
            print("Press: 2")
            deltat = datetime.datetime.now() - self.stimstarttime
            self.savetrial(resp=2, resptime = deltat.total_seconds())
            self.currenttrial += 1
            self.checkcontinue()
            
        elif (symbol == key.NUM_3 or symbol == key._3) and self.experimentphase==1:
            print("Press: 3")
            deltat = datetime.datetime.now() - self.stimstarttime
            self.savetrial(resp=3, resptime = deltat.total_seconds())
            self.currenttrial += 1
            self.checkcontinue()
            
        elif (symbol == key.NUM_4 or symbol == key._4) and self.experimentphase==1:
            print("Press: 4")
            deltat = datetime.datetime.now() - self.stimstarttime
            self.savetrial(resp=4, resptime = deltat.total_seconds())
            self.currenttrial += 1
            self.checkcontinue()
        
        elif (symbol == key.NUM_5 or symbol == key._5) and self.experimentphase==1:
            print("Press: 5")
            deltat = datetime.datetime.now() - self.stimstarttime
            self.savetrial(resp=5, resptime = deltat.total_seconds())
            self.currenttrial += 1
            self.checkcontinue()
                
        elif symbol == key.ENTER and self.experimentphase==0:
            if self.debug:
                print("ENTER")
            self.experimentphase += 1
        
        self.dispatch_event('on_draw') 
                 


#####################################################################
if __name__ == "__main__":
    
    if len(sys.argv) > 1:
        designfile = sys.argv[1]

    # it no argument passed, uses default design file    
    else:
        designfile = 'design_single_experiment_2.csv'

    
    # for fullscreen, use fullscreen=True and give your correct screen resolution in width= and height=
    win = Experiment(caption="Rating experiment - single stimulus assessment", 
                     vsync=False, height=800, width=1200, fullscreen=False)
    pyglet.app.run()

