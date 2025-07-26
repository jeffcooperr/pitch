# jotting down thoughts at work July 26
`extract_training_images.py` current version iterates through the 3 pitch type video folders and extracts a midpoint of each scene in each video.
these scenes are all added to the "not pitch" folder. the pitching scenes (which are easy to identify based on the thumbnail),
are manually dragged to the "pitch" folder. 
from here, we need to develop a model (research methods) to decipher between the two (ie, pitching scenes and all other scenes). the goal of this is to automatically extract 
the pitching scene from a given clip.

a revision (necessary?) for `extract_training_images.py` is likely to apply a crop/resizing for feeding the model. this apply should(?) be applied
before the midpoint images are saved to the "not pitch" folder. (why???)

jumping ahead to when model is done:

should be able to input a video file, and the return should be the pitching scene
raw video (multiple scenes) --> single (pitching) scene --> cropped ready to predict pitch

then obviously after this is probably the hardest part, actually predicting the pitch based off of movement, and potentially number of frames or something to get an idea of speed?

this project is meant to stand as a easy to operate, upload a video, get a result ordeal. a fully built model
