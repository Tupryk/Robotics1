from modules.loader import load_sketch
from modules.solvers import line_solver, pen_picker
from modules.utils import sketch_plotter, line_length
import numpy as np
from robotic import ry


# TODO get WHITE_BOARD_Z from depth camera
LIFT_SPACE = np.array([.1, .0, .0])
DRAW_SPEED = 0.1

ry.params_add({'physx/motorKp': 10000., 'physx/motorKd': 1000.})
ry.params_print()

C = ry.Config()
C.addFile(ry.raiPath('../rai-robotModels/scenarios/pandaSingle.g'))

C.addFrame("pen") \
    .setPosition([-0.25, .1, .675]) \
    .setShape(ry.ST.ssBox, size=[.02, .15, .02, .005]) \
    .setColor([1., .5, 0]) \
    .setMass(.1) \
    .setContact(True)

sketch = load_sketch("data/output.json", max_dims=[0.3, 0.3], canvas_center=[0.25, 1.2])
C = sketch_plotter(sketch, C)

bot = ry.BotOp(C, False)
bot.home(C)

# Grasp pen
grasp = False
if grasp:
    path = pen_picker(C)

    bot.gripperOpen(ry._left)
    while not bot.gripperDone(ry._left):
        bot.sync(C, .1)

    bot.move(path, [2., 3.])
    while bot.getTimeToEnd() > 0:
        bot.sync(C, .1)

    bot.gripperClose(ry._left)
    while not bot.gripperDone(ry._left):
        bot.sync(C, .1)

    bot.home(C)

# Draw sketch
bot.sync(C, .1)
draw = True
if draw:
    last_point = np.array(sketch[0][0])
    for j, line in enumerate(sketch):
    
        line_start = np.array(line[0])
        line_end = np.array(line[-1])

        # Move hand to line starting position
        lift_path = [last_point, line_start + LIFT_SPACE, line_start]
        time_to_solve = line_length(lift_path)/DRAW_SPEED
        path = line_solver(lift_path, C, debug=False)

        bot.move(path, [time_to_solve])
        while bot.getTimeToEnd() > 0:
            bot.sync(C, .1)

        # Draw single line
        time_to_solve = line_length(line)/DRAW_SPEED
        path = line_solver(line, C, debug=False)

        bot.move(path, [time_to_solve])
        while bot.getTimeToEnd() > 0:
            bot.sync(C, .1)

        # Lift hand from whiteboard
        lift_path = [line_end, line_end + LIFT_SPACE]
        time_to_solve = line_length(lift_path)/DRAW_SPEED
        path = line_solver(lift_path, C, debug=False)

        bot.move(path, [time_to_solve])
        while bot.getTimeToEnd() > 0:
            bot.sync(C, .1)

        last_point = line_end + LIFT_SPACE