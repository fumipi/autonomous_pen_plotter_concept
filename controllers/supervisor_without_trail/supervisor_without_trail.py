from controller import Supervisor
import math
from svgpathtools import parse_path
from math import ceil
import numpy as np
import requests
import xml.etree.ElementTree as ET

class Controller(Supervisor):
    timeStep = 64
    step_size = 0.01

    def __init__(self):
        super(Controller, self).__init__()
        self.robot = self.getFromDef('MyBot')
        self.trans_field = self.robot.getField('translation')
        self.rotation_field = self.robot.getField('rotation')
        self.pen = self.getDevice('pen')
        self.pen.write(True)
        self.current_position = [0, 0]
        self.current_rotation = 0
        self.pen_is_down = True

    def forward(self, distance):
        dx = distance * math.cos(self.current_rotation)
        dy = distance * math.sin(self.current_rotation)
        new_position = [self.current_position[0] + dx, self.current_position[1] + dy]
        self.move_to(new_position)

    def backward(self, distance):
        self.forward(-distance)

    def left(self, angle):
        self.current_rotation += math.radians(angle)

    def right(self, angle):
        self.left(-angle)

    def goto(self, x, y):
        new_position = [x, y]
        self.move_to(new_position)

    def move_to(self, position):
        steps = int(math.dist(self.current_position, position) / self.step_size)
        for i in range(steps):
            x = self.current_position[0] + (position[0] - self.current_position[0]) * i / steps
            y = self.current_position[1] + (position[1] - self.current_position[1]) * i / steps
            self.trans_field.setSFVec3f([x, y, 0])
            self.step(self.timeStep)
        self.current_position = position

    def penup(self):
        self.pen.write(False)
        self.pen_is_down = False

    def pendown(self):
        self.pen.write(True)
        self.pen_is_down = True

    def move(self, x, y):
        self.penup()
        self.goto(x, y)
        self.pendown()

    def line(self, x, y):
        self.goto(x, y)

    def draw_polygon(self, poly):
        self.penup()
        self.goto(poly[0][0], poly[0][1])
        self.pendown()
        for p in poly[1:]:
            self.goto(p[0], p[1])

    def draw_multipolygon(self, mpoly):
        for poly in mpoly:
            self.draw_polygon(poly)

    def run(self):
        # Try to download the SVG file from the GitHub raw URL
        url = 'https://raw.githubusercontent.com/fumipi/svg_files/main/uploaded.svg'
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
            svg_content = ET.fromstring(response.content)
        except (requests.RequestException, ET.ParseError):
            # If the request fails or the SVG content is invalid, use the local SVG file
            svg_file = "../../inputs/svg_icon.svg"
            with open(svg_file, 'r') as file:
                svg_content = ET.parse(file).getroot()

        # Extract paths from the SVG
        paths = []
        attrs = []
        for path_element in svg_content.findall('.//{http://www.w3.org/2000/svg}path'):
            path_data = path_element.get('d')
            if path_data:
                path = parse_path(path_data)
                paths.append(path)
                attrs.append(path_element.attrib)

        svg_attr = svg_content.attrib
        
        viewbox = svg_attr.get('viewBox', '0 0 100 100')
        viewbox_values = viewbox.split()
        svg_size = float(viewbox_values[2]), float(viewbox_values[3])
        
        # Get the paper size (to be obtained from sensors in the future)
        root_node = self.getRoot()
        paper_node = root_node.getField('children').getMFNode(-1)
        paper_size = paper_node.getField('children').getMFNode(0).getField('geometry').getSFNode().getField('size').getSFVec2f()
        
        # Scale the SVG to fit the paper size
        scale_x = paper_size[0] / svg_size[0]
        scale_y = paper_size[1] / svg_size[1]
        scale_factor = min(scale_x, scale_y)
        
        # Convert SVG coordinates to Webot coordinates
        offset_x = -svg_size[0] * scale_factor / 2
        offset_y = svg_size[1] * scale_factor / 2  
        
        seg_res = 5  
        polys = []
        for path, attr in zip(paths, attrs):
            if 'stroke' in attr and attr['stroke'] != 'none':
                poly = []
                for subpaths in path.continuous_subpaths():
                    points = []
                    for seg in subpaths:
                        interp_num = ceil(seg.length() / seg_res)
                        points.append(seg.point(np.arange(interp_num) / interp_num))
                    points = np.concatenate(points)
                    points = np.append(points, points[0])
                    poly.append(points)
                polys.append([[(p.real * scale_factor + offset_x, -p.imag * scale_factor + offset_y) for p in pl] for pl in poly])  # Flipped y-coordinate
        
        for poly in polys[1:]:  # Skip the frame line
            self.draw_multipolygon(poly)

controller = Controller()
controller.run()