
from controller import Robot


class Controller(Robot):
    timeStep = 64

    def __init__(self):
        super(Controller, self).__init__()

        self.pen = self.getDevice('pen')
        self.left_motor = self.getDevice('left wheel motor')
        self.right_motor = self.getDevice('right wheel motor')
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

    def move_forward(self, duration):
        self.left_motor.setVelocity(5.0)
        self.right_motor.setVelocity(5.0)
        self.step(duration)
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

    def rotate(self, duration):
        self.left_motor.setVelocity(-5.0)
        self.right_motor.setVelocity(5.0)
        self.step(duration)
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

    def run(self):
        while self.step(self.timeStep) != -1:
            self.pen.write(True)

            # go back and forth
            # self.move_forward(3000)  # Move forward for 1000 time steps
            # self.rotate(1000)  # Rotate for 1000 time steps = approx 360 degrees turn manually obtained

            #draw square
            self.move_forward(3000)  # Move forward for 1000 time steps
            self.rotate(530)  # Rotate for 530 time steps = 90 degrees turn manually obtained, not proportial to the 360 degree turn

            # #star
            # self.move_forward(3000)  # Move forward for 1000 time steps
            # self.rotate(850)  # Rotate for 850 time steps

controller = Controller()
controller.run()
