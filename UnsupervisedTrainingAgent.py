from EncodeState import EncodeState
import numpy as np
import getch
import sys

"""
* collect training samples and store it in a table
"""
class TrainingAgent(EncodeState):
    def __init__(self, environment, clustering_method, steps, action_interval, sample_collect_interval):
        super().__init__(resize_factor=None)
        self.env = environment
        self.clustering_method = clustering_method
        self.current_episode = 0
        self.training_states = []
        self.steps = steps
        self.frames = 0
        self.action_interval = action_interval
        self.sci = sample_collect_interval

    def action_choice(self):


        # TODO: fix for two characters e.g) 10, 11
        x = ord(getch.getch())

        return x-48


    # Returns training states with encoding
    def get_training_states(self):
        print("===========================================================================================")
        print("Pretraining session! Let Mario explore as much as possibile!!")
        print("Press 0 to {} to play, Press q to quit.".format(self.env.action_space.n-1))
        print("===========================================================================================")
        
        done = True
        for x in range(self.steps):
            if done:
                state = self.env.reset()
                
            # Control action from keyboard
            while (True):
                action = self.action_choice()
                if action in np.arange(self.env.action_space.n):
                    break
                # Press q to quit
                elif action == 113-48:
                    sys.exit()
            
            for frame in range(self.action_interval):
                next_state, reward, done, info = self.env.step(action)
                if reward == -15:
                    done = True


                if done:
                    break

            if x % self.sci == 0:
                self.training_states.append(self.encode_state(self.clustering_method, next_state))

            self.env.render()
            
        return np.array(self.training_states)
