#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Runs a rating experiment (Likert scale) - double stimulus assessment
(reference and distorted image)

It runs through a design file in csv format, which should contain the filenames of the
images to be displayed. reference and test.

From the command line pass the name of the design file as the first parameter
E.g.

python rating_experiment_double.py mydesignfile.csv

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
from pyglet.gl import glBindTexture, glEnable
from pyglet.window import key
from pathlib import Path

## Excerpt from Bosse (2018) p. 11
## In double stimulus assessment, such as Degradation Category Rating (DCR) 
# [ITU-T Rec. P.910, 2008] (also known as Double Stimulus Impairment Scale (DSIS) 
## [ITU-R Rec. BT.500-13, 2012]) or Double Stimulus Continuous Quality Scale 
## (DSCQS) [ITU-R Rec. BT.500-13, 2012], the participant is presented with a test
## condition (e.g. a distorted version of reference video or image) in relation 
## to its reference condition. Reference and test conditions can be presented 
## consecutively or side by side, the latter referred to as Simultaneous 
## Presentation (SP).
## (...) Observers report their judgment in terms of impairment of the test 
## condition with respect to the reference condition on a categorical scale 
## that is semantically annotated as 1-Very annoying, 2-Annoying, 3-Slightly 
## annoying, 4-Perceptible but not annoying and 5-Imperceptible. 
## In the DSCQS case the presentation order (or left/right hand sided position 
## on screen for SP) of reference and test condition is randomized (...)


instructions = """
Wilkommen!\n
Im folgenden Experiment werden immer zwei Bilder nebeneinander angezeigt.
Wähle in jedem Durchlauf das Bild, das Du als optisch ansprechender empfindest. Nutze hierfür die rechte und linke Pfeiltaste. \n
Bevor du beginnst, gib bitte an, ob du Instagram verwendest.
Drücken Sie die Taste 'y' wenn du Instagram verwendest. Drücke 'n' wenn du kein Instagram verwendest. \n
Drücken Sie ENTER um zu bestätigen und zu starten.
Drücken Sie ESC um zu beenden. """

instructions_ontrial = """ Linke Pfeiltaste     :     Rechte Pfeiltaste """

## stimulus presentation time variable
# presentation_time = 1 # presentation time in seconds, None for unlimited presentation
presentation_time = None


def read_design_csv(fname):
    """ Reads a CSV design file and returns it in a dictionary"""

    design = open(fname)
    header = design.readline().strip('\n').split(',')
    # print header
    data = design.readlines()

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

        # TODO: ask when starting
        self.usage = ""

        # Let all of the arguments pass through
        self.win = window.Window.__init__(self, *args, **kwargs)

        self.debug = False

        clock.schedule_interval(self.update, 1.0 / 30)  # update at FPS of Hz

        # Setting up text objects
        self.welcome_text = pyglet.text.Label(instructions,
                                              font_name='Arial', multiline=True,
                                              font_size=25, x=int(self.width / 2.0), y=int(self.height / 2.0),
                                              width=int(self.width * 0.75), color=(0, 0, 0, 255),
                                              anchor_x='center', anchor_y='center')

        self.instructions_ontrial = pyglet.text.Label(instructions_ontrial,
                                                      font_name='Arial', multiline=False,
                                                      font_size=20, x=int(self.width / 2.0), y=int(self.height * 0.1),
                                                      width=int(self.width * 0.75), color=(0, 0, 0, 255),
                                                      anchor_x='center', anchor_y='center')

        self.reference_text = pyglet.text.Label("Image A",
                                                font_name='Arial', multiline=False,
                                                font_size=20, x=int(self.width / 2.0), y=int(self.height * 0.9),
                                                width=int(self.width * 0.75), color=(0, 0, 0, 255),
                                                anchor_x='center', anchor_y='center')

        self.test_text = pyglet.text.Label("Image B",
                                           font_name='Arial', multiline=False,
                                           font_size=20, x=int(self.width / 2.0), y=int(self.height * 0.9),
                                           width=int(self.width * 0.75), color=(0, 0, 0, 255),
                                           anchor_x='center', anchor_y='center')

        # Design file
        global designfile
        self.designfile = designfile

        # Results file - assigning filename
        self.resultsfile = 'pair_results/pair_result_1.csv'

        file = Path(self.resultsfile)
        index = 2

        # prevents result from being replaced by new results
        while file.is_file():
            self.resultsfile = 'pair_results/pair_result_' + str(index) + '.csv'
            file = Path(self.resultsfile)
            index += 1


        # opening the results file, writing the header
        self.rf = open(self.resultsfile, 'w')
        self.resultswriter = csv.writer(self.rf)
        header = ['usage', 'image_a', 'image_b', 'f_a_og', 'f_b_og', 'f_a', 'f_b', 'i_a', 'i_b',
                  'chosen_f_og', 'chosen_f', 'chosen_i', 'left_right', 'resptime']
        self.resultswriter.writerow(header)

        # experiment control 
        self.experimentphase = 0  # 0 for intro, 1 for running trials, 2 for good bye
        self.firstframe = True
        self.present_stim = True

        # calling some routines on start
        self.loaddesign()
        # forces a first draw of the screen
        self.dispatch_event('on_draw')

    def loaddesign(self):
        """ Loads the design file specifications"""
        self.design = read_design_csv(self.designfile)
        self.totaltrials = len(self.design['image_a'])

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
        # dt = clock.tick() # ticking the clock
        # print(f"FPS is {clock.get_fps()}")

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
                self.stimstarttime = datetime.datetime.now()

            # draw images on the screen for a limited time
            if (presentation_time is None) or (self.present_stim):

                self.ref_image.blit(int(self.width * self.ref_position), int(self.height * 0.5))
                self.test_image.blit(int(self.width * self.test_position), int(self.height * 0.5))


                # draw label texts
                self.reference_text.x = int(self.width * self.ref_position)
                self.reference_text.draw()

                self.test_text.x = int(self.width * self.test_position)
                self.test_text.draw()

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
        # pyglet.gl.glFlush()

    def checkcontinue(self):
        """ Checks if we're at the end of the trials"""
        self.firstframe = True
        self.present_stim = True

        if self.currenttrial >= self.totaltrials:
            self.experimentphase = 2
            # self.dispatch_event('on_close')

    def load_images(self):
        """ Loads images of current trial """
        # load files 
        if self.debug:
            print('loading files')

        self.ref_image = pyglet.image.load("images_tiny/" + self.design['image_a'][self.currenttrial])
        self.test_image = pyglet.image.load("images_tiny/" + self.design['image_b'][self.currenttrial])

        # changes anchor to the center of the image
        self.ref_image.anchor_x = self.ref_image.width // 2
        self.ref_image.anchor_y = self.ref_image.height // 2

        self.test_image.anchor_x = self.test_image.width // 2
        self.test_image.anchor_y = self.test_image.height // 2

        self.ref_position = 0.25
        self.test_position = 0.75


    def savetrial(self, resp, resptime):
        """ Save the response of the current trial to the results file """

        left_right = 'left' if resp == 0 else 'right'
# 'usage', 'image_a', 'image_b', 'f_a_og', 'f_b_og', 'f_a', 'f_b', 'i_a', 'i_b', 'chosen_f_og', 'chosen_f', 'chosen_i', 'left_right', 'resptime'
        coresp_filter_a = self.design['f_a_og'][self.currenttrial]
        coresp_filter_b = self.design['f_b_og'][self.currenttrial]

        if coresp_filter_a == 'OG':
            coresp_filter_a = coresp_filter_b

        if coresp_filter_b == 'OG':
            coresp_filter_b = coresp_filter_a

        if left_right == 'left':
            selected_filter = self.design['f_a_og'][self.currenttrial]
            selected_intensity = self.design['i_a'][self.currenttrial]
            coresp_selected_filter = coresp_filter_a
        else:
            selected_filter = self.design['f_b_og'][self.currenttrial]
            selected_intensity = self.design['i_b'][self.currenttrial]
            coresp_selected_filter = coresp_filter_b


        row = [self.usage,
               self.design['image_a'][self.currenttrial],
               self.design['image_b'][self.currenttrial],
               self.design['f_a_og'][self.currenttrial],
               self.design['f_b_og'][self.currenttrial],
               coresp_filter_a,
               coresp_filter_b,
               self.design['i_a'][self.currenttrial],
               self.design['i_b'][self.currenttrial],
               selected_filter,
               coresp_selected_filter,
               selected_intensity,
               left_right,
               resptime]
        self.resultswriter.writerow(row)
        print('Trial %d saved' % self.currenttrial)

    ## Event handlers
    def on_close(self):
        """ Executed when program finishes """

        self.rf.close()  # closing results csv file
        self.close()  # closing window

    def on_key_press(self, symbol, modifiers):
        """ Executed when a key is pressed"""

        if symbol == key.ESCAPE:
            self.dispatch_event('on_close')

        if symbol == key.Y:
            self.usage = 'yes'

        if symbol == key.N:
            self.usage = 'no'

        elif (symbol == key.NUM_1 or symbol == key.LEFT) and self.experimentphase == 1:
            print("Press: Left arrow")
            deltat = datetime.datetime.now() - self.stimstarttime
            self.savetrial(resp=0, resptime=deltat.total_seconds())
            self.currenttrial += 1
            self.checkcontinue()

        elif (symbol == key.NUM_1 or symbol == key.RIGHT) and self.experimentphase == 1:
            print("Press: Right arrow")
            deltat = datetime.datetime.now() - self.stimstarttime
            self.savetrial(resp=1, resptime=deltat.total_seconds())
            self.currenttrial += 1
            self.checkcontinue()


        elif symbol == key.ENTER and self.experimentphase == 0:
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
        designfile = 'design_pair_experiment_1.csv'

    # for fullscreen, use fullscreen=True and give your correct screen resolution in width= and height=
    win = Experiment(caption="Rating experiment - double stimulus assessment",
                     vsync=False, height=1000, width=1400, fullscreen=False)
    pyglet.app.run()
