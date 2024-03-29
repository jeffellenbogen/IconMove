import time
from datetime import datetime


import random

from rgbmatrix import RGBMatrix, RGBMatrixOptions
from PIL import Image, ImageDraw, ImageFont

from usb_gamepad import gamepad_read_blocking,gamepad_read_nonblocking 

speed_delay = .5
###################################
# icon class 
#
#   Icons are the things that move around in the tank.  
#
#   On initialization, you specify an image file, which colors you want as 
#     transparent, and the desired size (in pixels) of that icon.
#
#   The move method updates the image's x and y position.
#  
#   The show method pastes the icon into an image.   
###################################
class Icon():

  ############################################
  # Init method 
  #   rtr, gtr, and btr are the transparency ranges for red, green, and blue 
  #      pixels in our image, represented as a tuple.  Any pixel in that range 
  #      (inclusive) will be marked as transparent. 
  # x_size is the horizonal size of the icon
  # y_size is the vertical size of the icon
  # timeout_seconds is the time an icons stays off screen before reseeding
  # total_columns and total_rows are the size of the whole matrix
  ###############################################
  def __init__(self, filename, rtr, gtr, btr, x_size, y_size, timeout_seconds, total_columns, total_rows):
  
    # top left corner of our image
    self.total_rows = total_rows
    self.total_columns = total_columns

    self.x = 50
    self.y = 50

    self.x_size = x_size
    self.y_size = y_size

    self.image = Image.open(filename)
    self.image = self.image.convert("RGBA")
    self.image = self.image.resize((x_size,y_size))

    self.filename = filename
    self.slowdown = 1
    self.movecount = 1
    self.direction = 1
    self.timeout = timeout_seconds
    self.onScreen = True

    # now that we have our image, we want to make a transparency mask.
    # start by looking at each pixel, and if it's in our transparency 
    # range, make the mask transparent (black).  Otherwise, make it 
    # fully opaque (white)
    self.mask = Image.new("L", (x_size,y_size))
    icon_data = self.image.getdata()
    mask_data = []
    for item in icon_data:
      # uncomment this line if you need to inspect pixels in your image
      # print item

      # is our pixel in range?  
      if ((item[0] >= rtr[0] and item[0] <= rtr[1]) and \
          (item[1] >= gtr[0] and item[1] <= gtr[1]) and \
          (item[2] >= btr[0] and item[2] <= btr[1])):
        mask_data.append(0)
      else:
        mask_data.append(255)
      self.mask.putdata(mask_data)

  ###############################################
  # setSlowdown method 
  ###############################################
  def setSlowdown(self,slowdown):
    self.slowdown = slowdown
  
  ###############################################
  # setDirection method 
  ###############################################
  def setDirection(self,direction):
    self.direction = direction
  
  ###############################################
  # show method 
  ###############################################
  def show(self,image):
    if self.direction == 1:
      image.paste(self.image,(self.x,self.y),self.mask)
    else:
      tempimage = self.image
      tempimageMask = self.mask
      tempimageFlip = tempimage.transpose(Image.FLIP_LEFT_RIGHT)
      tempimageFlipMask = tempimageMask.transpose(Image.FLIP_LEFT_RIGHT)
      image.paste(tempimageFlip,(self.x,self.y),tempimageFlipMask)

  ###############################################
  # startTimeout method 
  ###############################################
  def startTimeout(self):
    self.timeoutStart = time.time()
    print "timeout Started: "+str(self.filename) + " " +str(self.timeout) + "seconds"

  ###############################################
  # checkTimeout method 
  ###############################################
  def checkTimeout(self):
    currentTime = time.time()
    if currentTime - self.timeoutStart > self.timeout:
      self.onScreen = True

  ############################################
  # move 
  #   Checks to see if icon is onScreen and if onScreen == False, it runs checkTimeout to
  #      see if it is time to reseed yet.
  #   Updates our x and y position to the "next" spot.  
  #   If we go off the screen, we'll reset x, and pick a new
  #     random y.  
  ###############################################
  def move(self):
    global current_dir

    if current_dir == "up":
      self.y = self.y - 1
    if current_dir == "left":
      self.x = self.x - 1
    if current_dir == "right":
      self.x = self.x + 1
    if current_dir == "down":
      self.y = self.y + 1

    '''
    if self.onScreen == False:
      self.checkTimeout()
      ## this else block allows different icons to move at a slower rate based on the .slowdown value
    else:  
      if self.movecount < self.slowdown:
        self.movecount += 1
        return
      
      # if we're off the screen, reset direction and appropriate side, and pick a new y coordinate.
      if ((self.x < 0-self.x_size) or (self.x > self.total_columns)):
        self.onScreen = False
        self.startTimeout()
        directionChooser = random.randint(1,11)
        #direction is right
        if directionChooser % 2 == 0: 
          self.direction = 1
          self.x = 0 - self.x_size
        #direction is left  
        else:
          self.direction = -1
          self.x = self.total_columns
        if self.y_size >= self.total_rows:
          self.y = random.randint(0,self.total_rows)
        else:
          self.y = random.randint(0,self.total_rows - self.y_size)

      # move one pixel left or right depending on direction. 1 -> Right, -1 -> Left
      self.x = self.x + self.direction
      # increment movecount for slowing down movement if a value is set for .setSlowdown
      self.movecount = 1
      '''

###################################
#  Tank class
#
#  A tank has a background image and a list of icons that will be moving 
#  in that tank.
# 
###################################
class Tank():

  ############################################
  # Init method 
  ###############################################
  def __init__(self, panel_rows, panel_columns, num_horiz_panels, num_vert_panels):
 
    self.total_rows = panel_rows * num_vert_panels
    self.total_columns = panel_columns * num_horiz_panels

    options = RGBMatrixOptions()
    options.rows = matrix_rows 
    options.cols = matrix_columns 
    options.chain_length = num_horiz_panels
    options.parallel = num_vert_panels 
    options.hardware_mapping = 'regular' 
    #options.gpio_slowdown = 2

    self.matrix = RGBMatrix(options = options)
    self.background = None
    self.icons = []
    self.screen = Image.new("RGBA",(self.total_columns,self.total_rows))

  ############################################
  # set_background 
  ############################################
  def set_background(self, filename):
    self.background = Image.open(filename)
    self.background.convert("RGBA")
    self.background = self.background.resize((self.total_columns,self.total_rows))
   
  ############################################
  # add_icon 
  ###############################################
  def add_icon(self, icon):
    self.icons.append(icon)

  ############################################
  # show
  #   Displays the whole tank, and then moves any icon elements. 
  ###############################################
  def show(self):
    #restore background
    self.screen.paste(self.background,(0,0))
    
    # move and paste in our icons 
    for icon in self.icons:
      icon.move()
      icon.show(self.screen)

    self.screen = self.screen.convert("RGB")
    screen_draw = ImageDraw.Draw(self.screen)


    #write all changes to the screen
    self.matrix.SetImage(self.screen,0,0)

###################################
# Main code 
###################################
matrix_rows = 32
matrix_columns = 32
num_horiz = 5
num_vert = 3
current_dir = "up"

#create an instance of the Tank class and set it to a specific background image
forest_tank = Tank(matrix_rows, matrix_columns, num_horiz, num_vert)
forest_tank.set_background("images/forest_tank.png")

#create as many instances of the Icon class as needed
owl = Icon("images/bird1.png",(0,100),(150,255),(0,100),20,20,0,forest_tank.total_columns,forest_tank.total_rows)

#set the slowdown rate via the .setSlowdown method of the Icon class
#clownfish.setSlowdown(random.randint(0,2))

#add each of the icon instances to the tank, the order these are added determines their relationship
# in the tank from back to front. Last one added is closer to the front of the tank
forest_tank.add_icon(owl)

try:
  print("Press CTRL-C to stop")

  last_update_time = datetime.now()
  current_dir = "stop"

  while True:
    forest_tank.show()

    dir_pressed = False
    current_time = datetime.now()
    deltaT = current_time - last_update_time

    key = gamepad_read_nonblocking()

    if (key == "D-up"):
       print ("UP")
       current_dir = "up" 
       dir_pressed = True
    elif (key == "D-down"):
       print ("DOWN")
       current_dir = "down" 
       dir_pressed = True
    elif (key == "D-left"):
       print ("LEFT")
       current_dir = "left" 
       dir_pressed = True
    elif (key == "D-right"):
       print ("RIGHT")
       current_dir = "right" 
       dir_pressed = True
    else:
       current_dir = "stop"
       dir_pressed = False

    # Should probably use positive logic here to update the current direction, 
    # but instead, I'm using the continue construct.

    if ((deltaT.total_seconds() < speed_delay) & (dir_pressed == False)):
    #if (deltaT.total_seconds() < speed_delay) :  
      continue 
 
    last_update_time = current_time

    time.sleep(.02)
except KeyboardInterrupt:
  exit(0)



    
