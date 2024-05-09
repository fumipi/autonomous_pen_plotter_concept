from controller import Supervisor
import math
from svgpathtools import parse_path
from math import ceil
import numpy as np
import requests
import xml.etree.ElementTree as ET

#As webots.cloud does not support PEN device, added trail to the penbot controller in this version to mimic pen drawing

class Controller(Supervisor):
    timeStep = 64
    step_size = 0.005

    def __init__(self):
        super(Controller, self).__init__()
        self.robot = self.getFromDef('MyBot')
        self.trans_field = self.robot.getField('translation')
        self.rotation_field = self.robot.getField('rotation')
        self.pen = self.getDevice('pen')
        self.pen.write(True)
        self.current_position = [0, 0, 0.001]
        self.current_rotation = 0
        self.pen_is_down = True
        self.trail_node = None
        self.create_trail_shape()
        self.last_pen_down_index = 0

    def create_trail_shape(self):
        self.trail_node = self.getFromDef("TRAIL")
        if self.trail_node:
            self.trail_node.remove()

        trail_string = """
            DEF TRAIL Shape {
                appearance Appearance {
                    material Material {
                        diffuseColor 0 1 0
                        emissiveColor 0 1 0
                    }
                }
                geometry IndexedLineSet {
                    coord Coordinate {
                        point [
                            0 0 0.0015
                            0 0 0.0015
                        ]
                    }
                    coordIndex [
                        0 1
                    ]
                }
            }
            """

        root_node = self.getRoot()
        root_children_field = root_node.getField("children")
        root_children_field.importMFNodeFromString(-2, trail_string)
        self.trail_node = self.getFromDef("TRAIL")

    def update_trail(self):
        if self.trail_node and self.pen_is_down:
            target_translation = self.trans_field.getSFVec3f()
            trail_line_set_node = self.trail_node.getField("geometry").getSFNode()
            coordinates_node = trail_line_set_node.getField("coord").getSFNode()
            point_field = coordinates_node.getField("point")
            coord_index_field = trail_line_set_node.getField("coordIndex")


            if self.pen_is_down:
                index = point_field.getCount()
                point_field.insertMFVec3f(index, [target_translation[0], target_translation[1], 0.001])

                if index > 0:
                    coord_index_field.insertMFInt32(-1, index - 1)
                    coord_index_field.insertMFInt32(-1, index)

                self.last_pen_down_index = index
            else:
                # Remove points and indices from the last pen down position
                point_field.removeMFVec3fRange(self.last_pen_down_index, point_field.getCount() - self.last_pen_down_index)
                coord_index_field.removeMFInt32Range(coord_index_field.getCount() - 2, 2)

    def goto(self, x, y):
        new_position = [x, y, 0.001]
        self.move_to(new_position)
        self.current_position = new_position
        self.update_trail()

    def move_to(self, position):
        steps = int(math.dist(self.current_position[:2], position[:2]) / self.step_size)
        
        dx = position[0] - self.current_position[0]
        dy = position[1] - self.current_position[1]
        target_rotation = math.atan2(dy, dx)
        
        current_rotation = self.rotation_field.getSFRotation()[3]
        rotation_diff = target_rotation - current_rotation
        if rotation_diff > math.pi:
            rotation_diff -= 2 * math.pi
        elif rotation_diff < -math.pi:
            rotation_diff += 2 * math.pi
        
        start_rotation_step = int(steps * 0.8)  # Start rotating at 80% of the total steps
        
        for i in range(steps):
            t = i / steps
            
            # Interpolate position using linear interpolation
            x = self.current_position[0] + (position[0] - self.current_position[0]) * t
            y = self.current_position[1] + (position[1] - self.current_position[1]) * t
            self.trans_field.setSFVec3f([x, y, position[2]])
            
            if i >= start_rotation_step:
                current_rotation = self.rotation_field.getSFRotation()[3]
                rotation_error = target_rotation - current_rotation
                if rotation_error > math.pi:
                    rotation_error -= 2 * math.pi
                elif rotation_error < -math.pi:
                    rotation_error += 2 * math.pi
                
                # Rotate the robot towards the target rotation using a proportional controller
                rotation_speed = rotation_error * 0.1  # Adjust the proportional gain as needed
                new_rotation = current_rotation + rotation_speed
                
                # Normalize the rotation to stay within the range of 0 to 2π radians
                new_rotation = new_rotation % (2 * math.pi)
                
                self.rotation_field.setSFRotation([0, 0, 1, new_rotation])
            
            self.step(self.timeStep)
            self.update_trail()
        
        self.current_position = position
        self.current_rotation = target_rotation

    def penup(self):
        self.pen.write(False)
        self.pen_is_down = False
        self.update_trail()

    def pendown(self):
        self.pen.write(True)
        self.pen_is_down = True

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
        # url = 'https://raw.githubusercontent.com/fumipi/svg_files/main/uploaded.svg'
        # try:
        #     response = requests.get(url)
        #     response.raise_for_status()  # Raise an exception for 4xx or 5xx status codes
        #     svg_content = ET.fromstring(response.content)
        # except (requests.RequestException, ET.ParseError):
        #     # If the request fails or the SVG content is invalid, use the local SVG file
        svg_file = "../../inputs/camber_p1_simplified.svg"
        # svg_file = "../../inputs/sewing-pattern.svg"
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
        paper_node = None
        for i in range(root_node.getField('children').getCount()):
            node = root_node.getField('children').getMFNode(i)
            if node.getTypeName() == 'Solid' and node.getField('name').getSFString() == 'paper':
                paper_node = node
                break
        if paper_node:
            paper_size = paper_node.getField('children').getMFNode(0).getField('geometry').getSFNode().getField('size').getSFVec2f()
        else:
            # If paper node is not found, use a default paper size
            paper_size = [2, 2]  # Default paper size if not found in the world
        
        # Scale the SVG to fit the paper size
        scale_x = paper_size[0] / svg_size[0]
        scale_y = paper_size[1] / svg_size[1]
        scale_factor = min(scale_x, scale_y)
        
        # Convert SVG coordinates to Webot coordinates
        offset_x = -svg_size[0] * scale_factor / 2
        offset_y = svg_size[1] * scale_factor / 2  
        
        seg_res = 15  #5 works with sewing_pattern.svg , 15 works with camber_p2_simplified.svg
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
            self.update_trail()

controller = Controller()
controller.run() 