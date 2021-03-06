import scipy.io, os
import numpy as np
import cPickle
from PIL import Image
import shutil


def create_masks_for_model(model_folder):
 global images_counter
 global save_path
 
 file_name = model_folder 
 annot = load_annotations_from_file(file_name)
 for x in range(0, len(annot)):
   arr = np.zeros((480, 640))
   if (annot[x] <> 0):  
     arr[annot[x][1]:annot[x][3], annot[x][0]:annot[x][2]] = 1

   MM = {
      'PartMask' : arr
   }
           
   scipy.io.savemat(os.path.join(save_path,"{0}.mat".format(images_counter)), mdict = {'MM': MM}, do_compression = True)
   images_counter = images_counter + 1 
   if (x % 1000 == 0 and x>=1000):
     print images_counter

def load_annotations_from_file(file_name):
  f = file(file_name, 'rb')
  frame_rectangle_pairs = cPickle.load(f)
  f.close()
  return frame_rectangle_pairs

# [changeable] 
# choose where masks will be stored
save_path = os.path.abspath("/media/deeplearning/BCB24522B244E30E/experiment_DL/masks/training/")       

# [changeable]
# choose where the test_annotations.model is
model_folder =  os.path.abspath("/media/deeplearning/BCB24522B244E30E/experiment_DL/annotations/annotation_training.model") 


# [changeable]
# set to        last number + 1 of the mask that is in folder save_path       
# if the folder frames_path is empty leave it to 1
images_counter = 1


create_masks_for_model(model_folder)


