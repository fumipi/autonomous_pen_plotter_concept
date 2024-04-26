from controller import Robot
import math

class Controller(Robot):
    timeStep = 64
    wheel_radius = 0.025
    wheel_distance = 0.09

    def __init__(self):
        super(Controller, self).__init__()
        self.pen = self.getDevice('pen')
        self.left_motor = self.getDevice('left wheel motor')
        self.right_motor = self.getDevice('right wheel motor')
        self.left_motor.setPosition(float('inf'))
        self.right_motor.setPosition(float('inf'))
        self.left_motor.setVelocity(0.0)
        self.right_motor.setVelocity(0.0)

        self.x = 0
        self.y = 0
        self.heading = -1.5708
        self.speed = 5.0
        self.step_size = self.speed / 1000 * self.timeStep * self.wheel_radius

    def goto(self, x, y):
        dx = x - self.x
        dy = y - self.y
        target_angle = math.atan2(dy, dx)
        dtheta = target_angle - self.heading

        # Normalize dtheta to the range of -pi to pi
        dtheta = math.atan2(math.sin(dtheta), math.cos(dtheta))

        # Calculate rotation duration

        # Looks good to draw a simple square only, but very arbitorary, not really working other degree turns.
        rotation_duration = abs(dtheta) / self.speed * 1700

        # Rotate to face the target position
        if dtheta > 0:
            self.left_motor.setVelocity(-self.speed)
            self.right_motor.setVelocity(self.speed)
        else:
            self.left_motor.setVelocity(self.speed)
            self.right_motor.setVelocity(-self.speed)

        self.step(int(rotation_duration))
        self.left_motor.setVelocity(0)
        self.right_motor.setVelocity(0)

        # Correctly update the heading after rotation
        self.heading = target_angle
        print(math.degrees(self.heading))
        self.heading = math.atan2(math.sin(self.heading), math.cos(self.heading))
        print(math.degrees(self.heading))

        # Move to the target position
        distance = math.sqrt(dx**2 + dy**2)
        self.move_forward(distance)

        # Update current position
        self.x = x
        self.y = y
        print(self.x, self.y, math.degrees(self.heading))

    def move_forward(self, distance):
        steps = int(distance / self.step_size)
        self.left_motor.setVelocity(self.speed)
        self.right_motor.setVelocity(self.speed)
        for _ in range(steps):
            self.step(self.timeStep)
        self.left_motor.setVelocity(0)
        self.right_motor.setVelocity(0)

    def run(self):
        
        # # Go straight and turn 360 degree and go back 行って、360度回転して、戻る 出来ていない
        # path=[(0,0),(0,-0.5),(0,0)]
        
        # #Draw square, looks good at 1700 on line 37 四角形を描く 上で1700にするとこれだけはちょうど良い
        path = [(0.3, 0.3), (0.3, -0.3),(-0.3, -0.3),(-0.3, 0.3),(0.3, 0.3)]

        # #Draw T-shirt, but small error accumulates and robot can't go back to (0,0) Tシャツを描く - しかし、これくらい複雑になると、誤差が積み重なって元の(0,0)点に戻れない
        # path = [(0,0),(0.3, 0.8), (0.6, 0.7), (1, 0.3), (0.6, 0.05),
        #   (0.5, 0.2), (0.5, -0.8), (-0.5, -0.8), (-0.5, 0.2),
        #   (-0.6, 0.5), (-1.0, 0.3), (-0.6, 0.7), (-0.3, 0.8),
        #   (0.0, 0.7), (0.3, 0.8),(0,0)]
        
        self.pen.write(False)
        self.goto(path[0][0], path[0][1])
        self.pen.write(True)
        for point in path[1:]:
            self.goto(point[0], point[1])
        self.pen.write(False)

controller = Controller()
controller.run()