import getch
import sys
import signal

import gym
from nes_py.wrappers import BinarySpaceToDiscreteSpaceEnv
import gym_super_mario_bros as gym_smb
from gym_super_mario_bros.actions import *
import MarioRLAgent
import TrainingStats

import impl.EpsilonGreedyActionPolicy as EGAP
import impl.TabularQEstimator as TabQ
import impl.GBoostedQEstimator as GBQ


from UnsupervisedTrainingAgent import TrainingAgent
from UnsupervisedLearning import Cluster

class MarioRLUI(MarioRLAgent.IMarioRLAgentListener):
    def __init__(self,
               environment,
               q_estimator,
               action_policy,
               action_set,
               learning_policy = MarioRLAgent.LearningPolicy.SARSA,
               action_interval = 6):
        self.q_estimator = q_estimator
        self.rl_agent = MarioRLAgent.MarioRLAgent(
            environment,
            self.q_estimator,
            action_policy,
            action_set,
            learning_policy,
            action_interval,
            self)
        self.rl_agent.render_option = MarioRLAgent.RenderOption.ActionFrames
        self.paused = False
        self.verbose = False
        self.should_quit = False
        self.training_stats = TrainingStats.TrainingStats(q_estimator.summary(),
                                                          action_policy.summary(),
                                                          learning_policy.describe(),
                                                          ma_width=100)
        self.training_stats.plot()
        signal.signal(signal.SIGINT, self.make_signal_handler())

    def make_signal_handler(self):
        def handler(signum, frame):
            if self.paused:
                if self.confirm_quit():
                    self.should_quit = True
            else:
                print('Ctrl-C caught! Pausing...')
                self.paused = True
        return handler
        
    def episode_finished(self,
                         episode_number,
                         wall_time_elapsed,
                         game_time_elapsed,
                         n_frames,
                         fitness):
        self.training_stats.add_episode_stats(wall_time_elapsed,
                                              game_time_elapsed,
                                              n_frames,
                                              fitness)
        self.training_stats.plot()
        
    def main_loop(self):
        while not self.should_quit:
            print('\nMarioRL: [(v)erbose: {}] [(r)endering: {}]'.
                  format(
                      self.verbose,
                      str(self.rl_agent.render_option)
                  ))
            print('Commands: (t)rain (s)tep (q)uit')
            try:
                char = getch.getch()
            except OverflowError:
                continue
                
            if char == 'v':
                self.toggle_verbose()
            elif char == 'r':
                self.toggle_rendering()
            elif char == 't':
                print('Training... (Ctrl-C to pause and return to menu)')
                self.train()
            elif char == 's':
                self.step()
                print(self.rl_agent.action_policy.cluster.show_action_count())
            elif char == 'q':
                if self.confirm_quit():
                    self.should_quit = True
                    break

    def toggle_verbose(self):
        self.verbose = not self.verbose
        self.rl_agent.verbose = self.verbose
        self.q_estimator.verbose = self.verbose

    def toggle_rendering(self):
        if self.rl_agent.render_option == MarioRLAgent.RenderOption.NoRender:
            self.rl_agent.render_option = MarioRLAgent.RenderOption.ActionFrames
        elif self.rl_agent.render_option == MarioRLAgent.RenderOption.ActionFrames:
            self.rl_agent.render_option = MarioRLAgent.RenderOption.All
        elif self.rl_agent.render_option == MarioRLAgent.RenderOption.All:
            self.rl_agent.render_option = MarioRLAgent.RenderOption.NoRender
        else:
            raise RuntimeError('Unknown render option')

    def train(self):
        self.paused = False
        while not self.paused:
            self.rl_agent.step()

    def step(self):
        self.rl_agent.step()

    def confirm_quit(self):
        try:
            print('Are you sure you would like to quit (Y)?')
            char = getch.getch()
            return char == 'y' or char == 'Y'
        except OverflowError:
            return False

    def unsupervised_learning(self):
         TA = TrainingAgent(environment=self.rl_agent.env, clustering_method="kmeans", steps=300, action_interval=self.rl_agent.action_interval, sample_collect_interval=20)
         C = Cluster(action_space_size=self.rl_agent.env.action_space.n, clustering_method="kmeans", n_clusters=15)
         C.cluster(TA.get_training_states())
         return C
         

            
if __name__ == '__main__':
    # Set up the model
    env = gym_smb.make('SuperMarioBros-v0')
    action_set = COMPLEX_MOVEMENT
    env = BinarySpaceToDiscreteSpaceEnv(env, action_set)
    action_list = list(range(env.action_space.n))
   
    action_policy = EGAP.EpsilonGreedyActionPolicy(actions=action_list, epsilon=0.1, cluster=None)
    greedy_policy = EGAP.EpsilonGreedyActionPolicy(actions=action_list, epsilon=0, cluster=None)
    learning_policy = MarioRLAgent.LearningPolicy.SARSA

    # q_estimator = TabQ.TabularQEstimator(discount=0.5,
    #                                      steps=10,
    #                                      learning_rate=0.1,
    #                                      learning_policy=learning_policy,
    #                                      q_action_policy=None)
    q_estimator = GBQ.GBoostedQEstimator(discount=0.5,
                                         steps=10000,
                                         learning_rate=0.2,
                                         learning_policy=learning_policy,
                                         q_action_policy=greedy_policy)

    app = MarioRLUI(env,
                    q_estimator,
                    action_policy,
                    action_set,
                    learning_policy)
    cluster = app.unsupervised_learning()
        
    action_policy = EGAP.EpsilonGreedyActionPolicy(actions=action_list, epsilon=0.1, cluster=cluster)
    greedy_policy = EGAP.EpsilonGreedyActionPolicy(actions=action_list, epsilon=0, cluster=cluster)
    learning_policy = MarioRLAgent.LearningPolicy.SARSA

    
    app = MarioRLUI(env,
                    q_estimator,
                    action_policy,
                    action_set,
                    learning_policy)
    app.unsupervised()
    app.main_loop()
    env.close()
