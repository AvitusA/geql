import numpy as np
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec

class TrainingStats:
    def __init__(self, q_estimator, action_policy, comment=None, ma_width=20): 
        self.q_estimator_desc = q_estimator.summary()
        self.action_policy_desc = action_policy.summary()
        self.comment = '' if comment is None else '\n' + comment
        self.ma_width = ma_width
        self.n_episodes = 0
        self.episode_fitness = []
        self.episode_game_time = []
        self.episode_time = []
        self.episode_frame_count = []
        self.fig = plt.figure()
        self.fig.suptitle('$Q(s,a)$: ' + self.q_estimator_desc +
                          '\n$\pi(s,a)$:' + self.action_policy_desc +
                          self.comment, fontsize=8)
        spec = self.fig.add_gridspec(ncols = 1, nrows = 4)
        self.episode_fitness_graph = self.fig.add_subplot(spec[0:3,0])
        self.time_graph = self.episode_fitness_graph.twinx()        
        self.eps_graph = self.fig.add_subplot(spec[3,0], sharex = self.episode_fitness_graph)
        self.fps_graph = self.eps_graph.twinx()
        plt.ion()

    def moving_average(x, w):
        if len(x) == 0:
            return np.array([])
        convolved = np.convolve(x, np.ones(w), 'full')
        # Normalize the first elements separately (they are not over w samples)
        first_element_normalizers = np.array(range(1, w))
        convolved[0:w-1] = convolved[0:w-1] / first_element_normalizers
        # Normalize the rest of the elements
        convolved[w-1:len(x)] /= w
        return convolved[0:len(x)]
    
    def add_episode_stats(self, real_time_elapsed, game_time_elapsed, frames, fitness):
        self.episode_time.append(real_time_elapsed)
        self.episode_game_time.append(game_time_elapsed)
        self.episode_fitness.append(fitness)
        self.episode_frame_count.append(frames)
        self.n_episodes += 1
    
    def plot(self):
        n_episodes = len(self.episode_fitness)
        # Episode fitness
        self.episode_fitness_graph.clear()
        self.episode_fitness_graph.set_ylabel('fitness')
        self.episode_fitness_graph.tick_params(axis='y', colors='b')

        x = list(range(1, n_episodes + 1))
        self.episode_fitness_graph.plot(x, self.episode_fitness,
                                        color='cornflowerblue',
                                        marker='.',
                                        linestyle='')
        ma = TrainingStats.moving_average(self.episode_fitness, self.ma_width)
        self.episode_fitness_graph.plot(x, ma, 'b--')
        self.episode_fitness_graph.set_ylim(bottom=0)
        # Show x on the lowest subgraph instead
        self.episode_fitness_graph.grid(b=True, axis='x')
        self.episode_fitness_graph.tick_params(axis='x', bottom=False, top=False, colors='w')

        
        # Time
        self.time_graph.clear()
        self.time_graph.plot(x, self.episode_game_time,
                             color='salmon',
                             marker='.',
                             linestyle='')
        self.time_graph.set_ylim(bottom=0)
        self.time_graph.tick_params(axis='y', colors='r')
        self.time_graph.set_ylabel('episode time')



        # EPS
        self.eps_graph.clear()
        eps = (60*60) / np.array(self.episode_time)
        eps_ma = TrainingStats.moving_average(eps, self.ma_width)
        self.eps_graph.plot(x, eps,
                            color='cornflowerblue',
                            marker='.',
                            linestyle='')
        self.eps_graph.plot(x, eps_ma, 'b--')
        self.eps_graph.set_ylim(bottom=0)
        self.eps_graph.set_ylabel('EPH')
        self.eps_graph.tick_params(axis='y', colors='b')

        
        # FPS
        self.fps_graph.clear()
        fps = np.array(self.episode_frame_count) / np.array(self.episode_time)
        self.fps_graph.plot(x, fps, 'r')
        self.fps_graph.set_ylabel('FPS')
        self.fps_graph.set_ylim(bottom=0)
        self.fps_graph.tick_params(axis='y', colors='r')

        self.eps_graph.set_xlabel('episode')
        self.eps_graph.set_xlim(left=1, right=max(2,n_episodes))
        self.eps_graph.grid(b=True, axis='x')
    
        plt.pause(0.1)