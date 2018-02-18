# Usage instructions:
### Training a profile:
1. Create a folder for your training images. This folder should not contain anything except for the category folders and the images in them.
2. Inside of your main images folder, create a folder for each category. Put all of your training images in its category's folder. For example, if you are training a profile to distinguish between different flowers, it would look something like this: ![example image dir](https://www.tensorflow.org/images/folder_structure.png)
(Don't have a file called LICESNSE, just ignore that)
* [how to pick good training images](https://www.tensorflow.org/tutorials/image_retraining#creating_a_set_of_training_images)
3. Create a profile for this classifier in Taxon if you haven't already
4. Train your profile, and select flower_photos (or whatever yours is) as the image directory. Make sure that you don't accidentally select a category folder or something when you do this. Before you press the train button, make sure the path shown on the screen is to the correct folder.
5. Wait for the training to finish, and you're ready to label!
### How to use a trained profile:
1. After you have trained a profile, press "use a profile"
2. Select the profile you trained and select the image you want to label
3. After a short time, it will tell you what category it thinks the image is and how confident it is.
### Things you shouldn't do:
* do not store any files in or manipulate the program's directory in any way
# for developers:
### dependencies (for non-frozen python):
* [tensorflow](https://www.tensorflow.org/install/) version 1.5.0
* [appJar](http://appjar.info/Install/) version 0.90.0
* I have only found this to work on python 3.5.2 64 bit with tensorflow 1.5.0 installed
