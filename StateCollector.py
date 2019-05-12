from EncodeState import EncodeState
import numpy as np
import getch
import sys
import os


"""
* collect training samples and store it in a table
"""
class PretrainingAgent(EncodeState):
    def __init__(self, environment, clustering_method,n_clusters, pretraining_steps, action_interval, sample_collect_interval, state_encoding_params):
        self.env = environment
        self.clustering_method = clustering_method
        self.n_clusters = n_clusters
        self.current_episode = 0
        self.existing_pretraining_states = np.load("./pretraining_states.npz")
        self.collected_pretraining_states = []
        self.steps = pretraining_steps
        self.frames = 0
        self.action_interval = action_interval
        self.s_c_i = sample_collect_interval
        self.s_e_p = state_encoding_params

    def action_choice(self):
        x = ord(getch.getch())
        return x

    def save_pretraining_states(self):
        self.show_states_status()
        print("Do you want to save the your collected pretraining states? (y/n)")
        while(True):
            comfirm_key_2 = getch.getch()
            if comfirm_key_2 == 'y':
                if len(self.collected_pretraining_states) == 0:
                    print("No collected pretraining states")
                    print("Proceed with the game")

                else:
                    if self.existing_pretraining_states["arr_0"].shape == (1,):
                        self.existing_pretraining_states = np.array(self.collected_pretraining_states)
                    else:
                        self.existing_pretraining_states = np.concatenate([self.existing_pretraining_states["arr_0"], np.array(self.collected_pretraining_states)], 0)
                    
                    np.savez_compressed("./pretraining_states.npz", self.existing_pretraining_states)
                    print("COLLECTED pretraining states are saved to EXISTING pretraing states")
                    self.collected_pretraining_states = []

                self.existing_pretraining_states =  np.load("./pretraining_states.npz")
                return self.existing_pretraining_states["arr_0"]
            
            elif comfirm_key_2 == 'n':
                return self.existing_pretraining_states["arr_0"]
            else:
                print("illegal key")
                continue

    def initialize_existing_pretraining_states(self):
        self.show_states_status()
        print("Do you want to initialize the EXISTING pretraining states? (y/n)")
        while(True):
            comfirm_key_2 = getch.getch()
            if comfirm_key_2 == 'y':
                np.savez_compressed("./pretraining_states.npz", [-1])
                print("OK Proceed with the game.")
                break
            elif comfirm_key_2 == 'n':
                print("OK Proceed with the game.")
                break
            else:
                print("illegal key")
                continue

    def initialize_collected_pretraining_states(self):
        self.show_states_status()
        print("Do you want to initialize the COLLECTED pretraining states? (y/n)")
        while(True):
            comfirm_key_2 = getch.getch()
            if comfirm_key_2 == 'y':
                self.collected_pretraining_states = []
                print("OK Proceed with the game.")
                break
            elif comfirm_key_2 == 'n':
                print("OK Proceed with the game.")
                break
            else:
                print("illegal key")
                continue



    def show_states_status(self):
        self.existing_pretraining_states = np.load("./pretraining_states.npz")
        existing_s = self.existing_pretraining_states["arr_0"].shape[0]
        collected_s = np.array(self.collected_pretraining_states).shape[0]
        print("===========================================================================================")
        if self.existing_pretraining_states["arr_0"].shape == (1,):
            existing_s -= 1
        
        print("Number of EXISTING pretraining states: {}".format(existing_s))
        print("Number of COLLECTED pretraining states: {}".format(collected_s))
        print("Total number of states: {}".format(existing_s+collected_s))
        print("Total number of states needed to at least do clustering (number of clusters): {}".format(self.n_clusters))
        print("Number of steps left: {}".format(self.steps))
        print("Sample Collection Interval: {}".format(self.s_c_i))
        print("===========================================================================================")

        # print(pretraining_states["arr_0"].shape)
        # print(np.array(self.collected_pretraining_states).shape) 

    def print_rule(self):
        print("===========================================================================================")
        print("Pretraining session! Let Mario explore as much as possibile!!")
        print("BASIC MOVES: Arrows. Space is jump forward (right+A+B)")
        print("Otherwise, 0 to {} to play, Press q to quit.".format(self.env.action_space.n-1))
        print("If sufficient number of states are collected, you can quit")
        print("Press p to see Pretraining states status")
        print("Press c to initialize Collected pretraining states")
        print("Press e to initialize Existing pretraining states")
        print("Press s to Save collected pretraining states")
        print("Press r to show this Rule again")
        print("===========================================================================================")
    
    # Returns pretraining states with encoding
    def get_pretraining_states(self):
        self.print_rule()
        self.initialize_existing_pretraining_states()
        
        done = True
        
        while self.steps > 0:
            if done:
                state = self.env.reset()
                
            # Control action from keyboard
            while (True):
                key = self.action_choice()
                if (key == 65): # arrow-up
                    action = 5  # jump
                elif (key == 66): # arrow-down
                    action = 10   # down
                elif (key == 67): # arrow-right
                    action = 3    # right+B
                elif (key == 68): # arrow-left
                    action = 8    # left+B
                elif (key == 32): # space
                    action = 4    # right+A+B
                else:
                    action = key - 48
                    
                if action in np.arange(self.env.action_space.n):
                    for frame in range(self.action_interval+3):
                        next_state, reward, done, info = self.env.step(action)
                        if reward == -15:
                            done = True
                        if done:
                                break

                    if self.steps % self.s_c_i == 0:
                        self.collected_pretraining_states.append(self.encode_state(self.clustering_method,
                                                                         next_state,
                                                                         self.s_e_p))
                    self.env.render()
                    self.steps -= 1
                    break
                # Press q to quit
                elif action == 113-48: # q
                    while(True):
                        print("Are you sure you want to stop pretraining? (y/n)")
                        comfirm_key = getch.getch()
                        if comfirm_key == 'y':
                            return self.save_pretraining_states()
                        elif comfirm_key == 'n':
                            break
                        else:
                            print("illegal key")
                            continue
                        
                elif action == 112-48: # p
                    self.show_states_status()
                    
                elif action == 99-48: # c
                    self.initialize_collected_pretraining_states()

                elif action == 101-48: # e
                    self.initialize_existing_pretraining_states()
                
                elif action == 114-48: # r
                    self.print_rule()

                elif action == 115-48: # s
                    self.save_pretraining_states()
                else:
                    continue

        print("End of pretraining session")
        return self.save_pretraining_states()    
        
