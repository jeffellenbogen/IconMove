# player starts going up 
  current_dir = "up"

  print "use gamepad to move worm" 
 
  last_update_time = datetime.now()
  

  while True:

    dir_pressed = False
    current_time = datetime.now()
    deltaT = current_time - last_update_time

    key = gamepad_read_nonblocking()
    if (key == "D-up") & (current_dir != "down"):
       current_dir = "up" 
       dir_pressed = True
    if (key == "D-down") & (current_dir != "up"):
       current_dir = "down" 
       dir_pressed = True
    if (key == "D-left") & (current_dir != "right"):
       current_dir = "left" 
       dir_pressed = True
    if (key == "D-right") & (current_dir != "left"):
       current_dir = "right" 
       dir_pressed = True

    # Should probably use positive logic here to update the current direction, 
    # but instead, I'm using the continue construct.
    if ((deltaT.total_seconds() < speed_delay) & (dir_pressed == False)):
      continue 
 
    last_update_time = current_time
    
    if current_dir == "up":

    if current_dir == "left":

    if current_dir == "right":

    if current_dir == "down":