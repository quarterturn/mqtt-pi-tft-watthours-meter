#!/usr/bin/env python

import sys
import os, syslog
import pygame
import time
from time import sleep, strftime
from datetime import datetime
import string
import paho.mqtt.client as mqtt

# font colours
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)

# meter variables
watthours_per_day = 0
watthours_per_month = 0
cost_per_day = 0
cost_per_month = 0
previous_day = 0
previous_month = 0
# the following costs are in dollars
summer_cost_per_wh = 0.00010304
winter_cost_per_wh = 0.00009336
base_rate = 11.13
cost_of_reading = 0

# font colours
colorWhite = (255, 255, 255)
colorBlack = (0, 0, 0)

class pitft :
    screen = None;
    colorBlack = (0, 0, 0)
    
    def __init__(self):
        "Ininitializes a new pygame screen using the framebuffer"
        # Based on "Python GUI in Linux frame buffer"
        # http://www.karoltomala.com/blog/?p=679
        disp_no = os.getenv("DISPLAY")
        if disp_no:
            print "I'm running under X display = {0}".format(disp_no)

        os.putenv('SDL_FBDEV', '/dev/fb1')
        
        # Select frame buffer driver
        # Make sure that SDL_VIDEODRIVER is set
        driver = 'fbcon'
        if not os.getenv('SDL_VIDEODRIVER'):
            os.putenv('SDL_VIDEODRIVER', driver)
        try:
            pygame.init()
            pygame.display.init()
            pygame.mouse.set_visible(0)
            print("press ctrl-c now")
        except pygame.error:
            print 'Driver: {0} failed.'.format(driver)
            exit(0)
        
        size = (pygame.display.Info().current_w, pygame.display.Info().current_h)
        self.screen = pygame.display.set_mode(size, pygame.FULLSCREEN)
        # Clear the screen to start
        self.screen.fill((0, 0, 0))        
        # Initialise font support
        pygame.font.init()
        # Render the screen
        pygame.display.update()

    def __del__(self):
        "Destructor to make sure pygame shuts down, etc."

# Create an instance of the PyScope class
mytft = pitft()

pygame.mouse.set_visible(False)

# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')
# set up 3 sizes
font = pygame.font.Font(fontpath, 70)
fontSm = pygame.font.Font(fontpath, 30)
fontTime = pygame.font.Font(fontpath, 40)



def on_connect(mqttc, obj, flags, rc):
    print("connected to mqtt publisher")
    print("rc: " + str(rc))


def on_message(mqttc, obj, msg):
    print(msg.topic + " " + str(msg.qos) + " " + str(msg.payload))
    
    text_anchor_x = 0
    text_anchor_y = 0
    text_y_offset = 70

    global watthours_per_day 
    global watthours_per_month 
    global cost_per_day 
    global cost_per_month 
    global previous_day
    global previous_month
    global summer_cost_per_wh
    global winter_cost_per_wh
    global base_rate
    global cost_of_reading

    # update the display
    if msg.topic == "house_data/watthours":
        # blank the screen
        mytft.screen.fill(colorBlack)
        # check for month rollover
        if previous_month != datetime.now().strftime('%m'):
            # reset the day and month costs to the base rate
            cost_per_day = 0
            cost_per_month = base_rate   
            previous_month = datetime.now().strftime('%m')
        # check for day rollover
        if previous_day != datetime.now().strftime('%d'):
            # reset the day cost to zero
            cost_per_day = 0
            previous_day = datetime.now().strftime('%d')
        # summer rate
        if datetime.now().strftime('%m') in (7, 8, 9, 10):
            cost_of_reading = summer_cost_per_wh * float(msg.payload)
        # winter rate
        else:
            cost_of_reading = winter_cost_per_wh * float(msg.payload) 
        # add cost
        cost_per_day = cost_per_day + cost_of_reading
        cost_per_month = cost_per_month + cost_of_reading
      
        # strings
        day_string = "Today: $" + "%.2f" % cost_per_day
        #month_string = "This month: $" + "%.2f" % cost_per_month
        month_string = "%.2f" % cost_per_month
 
        # display text
        text_surface = font.render("Electricity Usage", True, colorWhite)
        mytft.screen.blit(text_surface, (text_anchor_x, text_anchor_y))
        text_anchor_y += text_y_offset
        text_surface = font.render(day_string, True, colorWhite)
        mytft.screen.blit(text_surface, (text_anchor_x, text_anchor_y)) 
        text_anchor_y += text_y_offset
        text_surface = font.render("This month:", True, colorWhite)
        mytft.screen.blit(text_surface, (text_anchor_x, text_anchor_y))
        text_anchor_y += text_y_offset
        text_surface = font.render("$" + month_string, True, colorWhite)
        mytft.screen.blit(text_surface, (text_anchor_x, text_anchor_y))


    # refresh the screen with all the changes
        pygame.display.update()

def on_publish(mqttc, obj, mid):
    print("mid: " + str(mid))
    pass


def on_subscribe(mqttc, obj, mid, granted_qos):
    print("Subscribed: " + str(mid) + " " + str(granted_qos))


def on_log(mqttc, obj, level, string):
    print(string)


# set up the fonts
# choose the font
fontpath = pygame.font.match_font('dejavusansmono')

# main code
client = mqtt.Client()
client.on_message = on_message
client.on_connect = on_connect

client.connect("192.168.0.21")

client.subscribe("house_data/watthours")

client.loop_forever()
