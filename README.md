## Autonomous Pen Plotter Concept

This is a Webots simulation to show the concept of "Autonomous Pen Plotter", in which a robot draws the path of the uploaded svg file. You can run this simulatio from the demo or from webots desktop application.

### Demo on webots.cloud
https://webots.cloud/run?version=R2023b&url=https%3A%2F%2Fgithub.com%2Ffumipi%2Fautonomous_pen_plotter_concept%2Fblob%2Fmain%2Fworlds%2Fpenbot.wbt&type=demo
Note the webots.cloud does not support drawing by pen yet, I mimic the effect by making the robot's trail visible in green lines in the above demo.

### Run the simulation on Webots desktop app
Download the Webots desktop app from [their site](https://cyberbotics.com/) for free.  
If the simulation is run on desktop application, you can see the robot draw with pen in black ink.

### SVG file uploader app
You can change the svg image that the robot draws in the demo from the below app.
https://github.com/fumipi/svg_file_uploader

### note
I am just getting started, and planning to make the robot "autonomous" with sensors, but currently using the "supervisor" controller to move the robot as a first step. 
