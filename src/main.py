from src.graphics import *
from src.particle import Particle
import random
from src.rtree import *
import time
from copy import deepcopy
import matplotlib.pyplot as plt

random.seed(0)


random_data = os.urandom(8)
seed = int.from_bytes(random_data, byteorder="big")
print(seed)

WIDTH = 500
HEIGHT = 500

def update_particles(particles):
    for i in range(len(particles)):
        particles[i].update(WIDTH, HEIGHT)


def update_tree(t, particles):
    for i in range(len(particles)):
        particles[i].update(WIDTH, HEIGHT)
        t.insert(particles[i])


def draw(t, win):
    for item in win.items[:]:
        item.undraw()
    t.draw(win)
    win.update()


def rtree_metrics(num_updates, num_particles):
    tree = RTree(Point(0, 0), Point(500, 500), max_per_level=4)
    particles = [Particle(random.random() * 500, random.random() * 500, 10, 10) for _ in range(num_particles)]
    start_time = time.time()
    update_freq = 30

    for i in range(num_updates):
        tree.clear()
        # update_tree(tree, particles)
        for j in range(num_particles):
            particles[j].update(WIDTH, HEIGHT)
            if i % update_freq == 0:
                tree.insert(particles[j])

        for j in range(num_particles):
            rect = particles[j].rect
            close_objects = tree.search(Rectangle(Point(rect.p1.x - 50, rect.p1.y - 50), Point(rect.p2.x + 50, rect.p2.y + 50)))

    # print(f"avg rtree update time: {(time.time() - start_time) / num_updates}")
    return (time.time() - start_time) / num_updates


def linear_search_metrics(num_updates, num_particles):
    particles = [Particle(random.random() * 500, random.random() * 500, 10, 10) for _ in range(num_particles)]
    start_time = time.time()

    for i in range(num_updates):
        update_particles(particles)
        for j in range(num_particles):
            rect = particles[0].rect
            close_objects = [particle for particle in particles if particle.rect.intersects(rect)]

    # print(f"avg linear update time: {(time.time() - start_time) / num_updates}")
    return (time.time() - start_time) / num_updates


def visualize_rtree():
    win = GraphWin(width=WIDTH, height=HEIGHT, autoflush=False)

    tree = RTree(Point(0, 0), Point(500, 500), max_per_level=10)
    num_particles = 50
    particles = [Particle(random.random() * 500, random.random() * 500, 10, 10) for _ in range(num_particles)]
    update_freq = 30

    num_updates = 10000
    for i in range(num_updates):
        if i % update_freq == 0:
            tree.clear()

        start_time = time.time()
        for j in range(num_particles):
            particles[j].update(WIDTH, HEIGHT)
            if i % update_freq == 0:
                tree.insert(particles[j])
        print(f"update time: {time.time() - start_time}")
        rect1 = particles[0].rect
        close_objects = tree.search(
            Rectangle(Point(rect1.p1.x - 50, rect1.p1.y - 50), Point(rect1.p2.x + 50, rect1.p2.y + 50)))
        draw(tree, win)
        # for item in win.items[:]:
        #     item.undraw()
        # for o in close_objects:
        #     o.rect.draw(win)
        # win.update()


num_iter = 10
points_in_plot = 100

rtree_results = []
linear_search_results = []

# Run the experiments
for i in range(1, points_in_plot + 1):
    print(i)
    rtree_result = rtree_metrics(num_iter, i * 5)
    linear_search_result = linear_search_metrics(num_iter, i * 5)
    rtree_results.append(rtree_result / num_iter)
    linear_search_results.append(linear_search_result / num_iter)

# Create a list of iterations for the x-axis
iterations = [i * 5 for i in range(1, points_in_plot + 1)]

# Create the plot
plt.plot(iterations, rtree_results, label='R-tree')
plt.plot(iterations, linear_search_results, label='Linear Search')

# Add labels and a legend
plt.xlabel('Number of Particles')
plt.ylabel('Average Time Per Iteration')
plt.legend()

# Show the plot
plt.show()

# Explanation: generates 50 points running 10 iterations of (i * 5) moving particles, finding AOI of each particle.
