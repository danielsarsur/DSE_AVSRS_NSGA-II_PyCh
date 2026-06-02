import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('nbagg')

class LivePlot:
    def __init__(self, live = True):
        self.x_data, self.y_data = [], []
        self.figure = plt.figure()
        self.line, = plt.plot(self.x_data, self.y_data)
        self.live = live  # denotes if the step plot should be updated live

    def update(self, x_data, y_data):
        self.x_data.append(x_data)
        self.y_data.append(y_data)
        self.line.set_data(self.x_data, self.y_data)
        self.figure.gca().relim()
        self.figure.gca().autoscale_view()
        if self.live:
            self.figure.canvas.draw()
        return self.line,

    def show(self):
        plt.show()


class LiveStepPlot(LivePlot):
    def __init__(self, live = True):
        self.x_data, self.y_data = [], []
        self.figure = plt.figure()
        self.line, = plt.step(self.x_data, self.y_data)
        self.live = live  # denotes if the step plot should be updated live
