from PIL import Image
import numpy as np

"""
* encode state for training + predicting(States are optimized for different learning methods)
"""
class EncodeState:        
    def encode_state(self, clustering_method, state, state_encoding_params):
        if (clustering_method == "kmeans"):
            img = Image.fromarray(state)
            img = img.crop((0,40,256,240))
            img = img.convert(mode='L')
            
            new_width = int(state_encoding_params.default_shape[0]/state_encoding_params.resize_factor)
            new_height = int(state_encoding_params.default_shape[1]/state_encoding_params.resize_factor)
            resized_img = img.resize((new_width, new_height), resample=Image.BICUBIC)
            imgtoArray = np.asarray(resized_img).reshape(-1)
            return imgtoArray

