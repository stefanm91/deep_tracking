import Tkinter as tk
import os
from PIL import ImageTk, Image
import dlib
from skimage import io
import glob
import numpy as np
import cPickle
import datetime
from sklearn.feature_extraction import image

class SampleApp(tk.Tk):
    '''Illustrate how to drag items on a Tkinter canvas'''

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)

	#set title you can do it in main as well
	self.title("Data annotation")
	
        # create a canvas
        self.canvas = tk.Canvas(width=860, height=640)
        self.canvas.pack(fill="both", expand=True)
	
	# maybe setup main folder here like $TOOLS
	
	#self.video_folder = os.path.abspath("/home/stefan/Documents/plexondata/2015_12_02_rat10/output1/")
        self.video_folder = os.path.abspath("/home/stefan/Documents/paw_tracking/frames")
        self.save_folder_patches = os.path.abspath("/home/stefan/Documents/paw_tracking/patches")
        self.save_folder_txt = os.path.abspath("/home/stefan/Documents/paw_tracking")
        
        # create an image
        
		
	# prevent image from garbage collection using self
	# create image counter
	self.img_num = 0
	
	# read all images
	self.images = [] 
	self.images_raw = []
        self._read_all_images()
	self.rectangle_frame_pairs = [0]*len(self.images_raw)
	
	#self.img = ImageTk.PhotoImage(Image.open(os.path.join(self.video_folder, "{0}.jpeg".format(self.img_num+1))))
        
        self.img_id = self.canvas.create_image(100, 100, image = self.images[self.img_num], anchor="nw") #, anchor = NW
	
	# this data is used to keep track of an 
        # item being dragged
        self._drag_data = {"x": 0, "y": 0, "item": None}
	
        # create a couple movable objects
        self.polygon_id = 0
        
        # rectangle size in x and y
        # rectangle_size = [100, 40]
        self.rectangle_size = [100, 50]
        
        self._create_token((100, 100), "red", self.rectangle_size)
        #self._create_token((200, 100), "black")
               

        # put image in label
	#panel = tk.Label(self.canvas, image = self.img)
	#panel.place(x=150,y=150)
	#panel.pack()
	
	
	
	#self.canvas.tag_lower(panel)
	#self.canvas.tag_lower(self.img)
	
        # add bindings for clicking, dragging and releasing over
        # any object with the "token" tag
        self.canvas.tag_bind("token", "<ButtonPress-1>", self.OnTokenButtonPress)
        self.canvas.tag_bind("token", "<ButtonRelease-1>", self.OnTokenButtonRelease)
        self.canvas.tag_bind("token", "<B1-Motion>", self.OnTokenMotion)
        
        # add bindings for arrow keys when changing the image to right
        self.canvas.bind("<Return>", self.returnKey)
        self.canvas.bind("<Right>", self.rightKey)
        self.canvas.bind("<Left>", self.leftKey)
        self.canvas.focus_set()
        
	#self.canvas.bind("<ButtonPress-1>", self.OnTokenButtonPress)
	#self.canvas.bind("<ButtonRelease-1>", self.OnTokenButtonRelease)
	#self.canvas.bind("<B1-Motion>", self.OnTokenMotion)
	
	# initialize tracker
	self.tracker = dlib.correlation_tracker()
	self.prev_tracker = self.tracker
	self.flag = 0
	
	'''create buttons section'''
	
	#add quit button
        button1 = tk.Button(self.canvas, text = "Quit", command = self.quit,
                                                            anchor = "w")
        button1.configure(width = 10)
        button1.pack()
        button1_window = self.canvas.create_window(10, 10, anchor="nw", window=button1)
	
	button2 = tk.Button(self.canvas, text = "Save annotations", command = self.save, anchor = "w")
	button2.configure(width = 15)
	button2.pack()
	button2_window = self.canvas.create_window(150, 10, anchor="nw", window=button2)
	
	#check if inbetwen save and load the space is same
	button3 = tk.Button(self.canvas, text = "Load annotations", command = self.load, anchor = "w")
	button3.configure(width = 15)
	button3.pack()
	button3_window = self.canvas.create_window(330, 10, anchor="nw", window=button3)
	
	button4 = tk.Button(self.canvas, text = "Extract patches", command = self.extract_patches, anchor = "w")
	button4.configure(width = 15)
	button4.pack()
	button4_window = self.canvas.create_window(530, 10, anchor="nw", window=button4)
	
	
	
	#img = self.images_raw[0]
	#self.patches = image.extract_patches_2d(img, (50,100))
	
    def _create_token(self, coord, color, rectangle_size):
        '''Create a token at the given coordinate in the given color'''
        (x,y) = coord
        #self.rect = self.canvas.create_rectangle(x-25, y-25, x+25, y+25, 
        #                        outline=color, tags="token")
	self.polygon_id = self.canvas.create_polygon(x-0,y-0,x+rectangle_size[0],y-0,x+rectangle_size[0],y+rectangle_size[1],x-0,y+rectangle_size[1], outline='red', fill='', tags="token")
	#self.canvas.tag_raise(self.polygon_id)
    
    def _read_all_images(self):
      for k, f in enumerate(sorted(glob.glob(os.path.join(self.video_folder, "*.jpg")))):
	img_raw = io.imread(f)
	#print len(img_raw)
	#print f
	self.images_raw.append(img_raw)
	self.images.append(ImageTk.PhotoImage(image = Image.fromarray(img_raw)))
      
    
    def _get_coord_rectangle(self):
      ''' Get coordinates of rectangle relative to image '''
      coords_rectangle = self.canvas.coords(self.polygon_id)
      coords_rectangle = [long(c) for c in coords_rectangle]
      coords_image = self.canvas.coords(self.img_id)
      coords_image = [long(c) for c in coords_image]
      coords_relative = [coords_rectangle[0]-coords_image[0],coords_rectangle[1]-coords_image[1],coords_rectangle[4]-coords_image[0],coords_rectangle[5]-coords_image[1]]
      
      return coords_relative      
    
    def _change_image(self):
      self.canvas.itemconfig(self.img_id, image = self.images[self.img_num])
    
    def _change_rectangle(self):
      rel_position = self.rectangle_frame_pairs[self.img_num]
      curr_position = self._get_coord_rectangle()
      #print (rel_position.left())
      self.canvas.move(self.polygon_id, -curr_position[0]+rel_position[0], -curr_position[1]+rel_position[1])
    
    
    # move the train = 0 out of this function
    def _sliding_window(self, window_size, image_num = 0, overlap = 0, train = 0):
      
      if train == 0:
	file = os.path.join(self.save_folder_txt, "train.txt")
      else:
	file = os.path.join(self.save_folder_txt, "val.txt")
      
      with open(file, "a") as myfile:
	# just for testing purposes
	# later for all images in separate folder
	#img = self.images_raw[0][:,:,0]
	img = self.images_raw[image_num]
	#img = np.arange(640*480).reshape((640,480))
	#patches = image.extract_patches_2d(img, window_size)
	
	# for each positive patch choose one negative by random
	# but make sure it does not overlap by more than 50%
	# maybe make two separate functions for positive and negative samples
	
	# left top right bottom
	#coord_relative = self._get_coord_rectangle()
	#print image_num

	coord_relative = self.rectangle_frame_pairs[image_num]
	#win = dlib.image_window()
	#print coord_relative
	#print img.shape
	#Image.fromarray(self.patches[540*(480-(50-1))+430]).save("test.jpg")
	#patch_nr = coord_relative[1]*(640-(window_size[1]-1))+coord_relative[0]
	coord_x = coord_relative[1]
	coord_y = coord_relative[0]
	p = 0
	counter = 0
	
	# make this more efficient without the whiles
	# just with matrices
	
	while p < (640/window_size[1])*(480/window_size[0]):
	  Image.fromarray(self.images_raw[image_num][coord_x:coord_x+50,coord_y:coord_y+100,:]).save("{0}/5_{1}_{2}.jpg".format(self.save_folder_patches,image_num,counter))
	  if p == 0:
	    myfile.write("patches/5_{0}_{1}.jpg 1 \n".format(image_num, counter))
	  else:
	    myfile.write("patches/5_{0}_{1}.jpg 0 \n".format(image_num, counter))
	    
	  coord_y = coord_y+window_size[1]
	  #proverka dali odi vo nov red, proveri na mal primer
	  if coord_y >= 640-window_size[1]:
	    coord_x = coord_x+window_size[0]
	    coord_y = 0
	  if coord_x >= 480-window_size[0]:
	    break
	  
	  #print coord_x, coord_y
	  p = p+1
	  counter = counter + 1
	p = 0
	coord_x = coord_relative[1]
	coord_y = coord_relative[0]
	while p < (640/window_size[1])*(480/window_size[0]):
	  coord_y = coord_y-window_size[1]
	  #proverka dali odi vo nov red, proveri na mal primer
	  #proveri dali pomalo i ednakvo
	  if coord_y < 0:
	    coord_x = coord_x-window_size[0]
	    coord_y = 640-window_size[1]
	  if coord_x < 0:
	    break      
	  
	  #Image.fromarray(patches[coord_x*(640-(window_size[1]-1))+coord_y]).save("test{0}.jpeg".format(p))
	  Image.fromarray(self.images_raw[image_num][coord_x:coord_x+50,coord_y:coord_y+100,:]).save("{0}/5_{1}_{2}.jpg".format(self.save_folder_patches,image_num,counter))
	  myfile.write("patches/5_{0}_{1}.jpg 0 \n".format(image_num, counter))
	  #print coord_x, coord_y
	  p = p+1
	  counter = counter + 1

	# or maybe instead of this, create non-overlapping windows, but that way it can miss
	# the positive sample
	  
	#Image.fromarray(self.patches[]).save("test.jpg")
	# stavi tuka prefiksi na slikite
      
      
      #print self.patches.shape
      #for p in range(0,len(patches)):
	#im = Image.fromarray(patches[p])
	#im.save("test{0}.jpg".format(p))
      print "patches successfully saved for image: ", image_num 
    def extract_patches(self):
      # check for 0 in rectangles
      # count all zeros so you know how to split train and test
      # shuffle data
      # or maybe put NaN and count nans
      
      counter = 0
      for rect in self.rectangle_frame_pairs:
	if rect is not 0:
	  counter = counter + 1


      # split into training and test and save in file
      stop_training = int(counter*0.75)
     
      # this can go in one while document
      c = 0
      c1 = 0
      while c < stop_training:
	if self.rectangle_frame_pairs[c1] <> 0:
	  self._sliding_window ((50,100), c1, 0, 0)
	  c = c + 1
	c1 = c1+1
      
      while c < counter:
	if self.rectangle_frame_pairs[c1] <> 0:
	  self._sliding_window ((50,100), c1, 0, 1)
	  c = c+1
	c1 = c1+1
      
      # check verbose
      print "patches were saved congrats to you!!!"
      
      
      
      #self._sliding_window((50,100),0,0)
      
    
    def save(self):
      # on each update replace the same file
      # on each session create new file so there won't be overwrites
      
      
      f = file("annotations.model", 'wb')
      cPickle.dump(self.rectangle_frame_pairs, f, protocol = cPickle.HIGHEST_PROTOCOL)
      f.close()
      
      print "save was called!"
    
    # make Browse button
    def load(self):
      f = file("annotations.model", 'rb')
      previous_frames = cPickle.load(f)
      
      # in case extra frames are added
      self.rectangle_frame_pairs[0:len(previous_frames)] = previous_frames  
      
      f.close()
      
      #write message like successfully loaded etc.
      print "load was called"
    
    def rightKey(self, event):
      self.img_num +=1
      if self.img_num >= len(self.images):
	self.img_num = 0
      else:
	# if rectangle exists redraw it
	if (self.rectangle_frame_pairs[self.img_num] is not 0):
	  self._change_rectangle() 
      self._change_image()
      #print self.img_num/float(20*3600)
      
    
    # same code in both right and left key, refactor
    
    def leftKey(self, event):
      self.img_num -=1 
      if self.img_num >= len(self.images): 
	self.img_num = 0
      else:
	# if rectangle exists redraw it
	if (self.rectangle_frame_pairs[self.img_num] is not 0):
	  self._change_rectangle() 
      self._change_image()
    
    def returnKey(self, event):
        #self._sliding_window((50,100),0)
        #print self.img_num/float(20*3600)
        #save rectangle position
        self.rectangle_frame_pairs[self.img_num] = self._get_coord_rectangle()
        
        #print image_id
        #print self._get_coord_rectangle()
        #print self.rectangle_frame_pairs
        
        
        # set the current position of the rectangle for tracking
	if (self.flag == 0):
	  
	  #print coords_rectangle
	  coords_relative = self._get_coord_rectangle()
	  
	  #proveri uste ednas koordhinatite
	  self.tracker.start_track(self.images_raw[self.img_num], dlib.rectangle(coords_relative[0],coords_relative[1],coords_relative[2],coords_relative[3]))
	  #self.tracker.start_track(self.images_raw[0], dlib.rectangle(170, 200, 240, 240))
	  self.flag = 1 
	  
	  self.img_num = self.img_num + 1
	  if self.img_num >= len(self.images):
	    self.img_num = 0
	    
	  self._change_image()
	  
        else:
	  
        #self.new_img = ImageTk.PhotoImage(Image.open(os.path.join(self.video_folder, "{0}.jpg".format(self.img_num))))
	#self.img = io.imread(os.path.join(self.video_folder, "{0}.jpg".format(self.img_num)))
	#self.im_from_array = Image.fromarray(self.img)
	#self.new_img = ImageTk.PhotoImage(image = self.im_from_array)
	#self.canvas.itemconfig(self.img_id, image = self.new_img)

	  # you can refactor this code
	  coords_relative = self._get_coord_rectangle()
	  
	  #update filter
	  #self.prev_tracker = tracker
	  self.tracker.update(self.images_raw[self.img_num], dlib.rectangle(coords_relative[0],coords_relative[1],coords_relative[2],coords_relative[3]))
	  
	  # update rectangle (overlay it)
	  rel_position = self.tracker.get_position()
	  curr_position = self._get_coord_rectangle()
	  #print (rel_position.left())
	  
	  # refactor this code as well
	  self.canvas.move(self.polygon_id, -curr_position[0]+rel_position.left(), -curr_position[1]+rel_position.top())
	  
	  self.img_num = self.img_num + 1
	  if self.img_num >= len(self.images):
	    self.img_num = 0
	    
	  self._change_image()

    
    def OnTokenButtonPress(self, event):
        '''Being drag of an object'''
        # record the item and its location
        self._drag_data["item"] = self.canvas.find_closest(event.x, event.y)[0]
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y
        
        # put item to front
        self.canvas.tag_raise(self._drag_data["item"])

    def OnTokenButtonRelease(self, event):
        '''End drag of an object'''
        # reset the drag information
        self._drag_data["item"] = None
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def OnTokenMotion(self, event):
        '''Handle dragging of an object'''
        # compute how much this object has moved
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        
        # move the object the appropriate amount
        self.canvas.move(self._drag_data["item"], delta_x, delta_y)
        
        # record the new position
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y

if __name__ == "__main__":
    app = SampleApp()
    app.mainloop()