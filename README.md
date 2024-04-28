## Autonomous Pen Plotter Concept
This is a Webots simulation showcasing the new concept of "Autonomous Pen Plotter." This robot draws paths from uploaded SVG files. Experience this simulation through a demo or the Webots desktop application.

### Demo on webots.cloud
[Simulation on Webots.cloud](https://webots.cloud/run?version=R2023b&url=https%3A%2F%2Fgithub.com%2Ffumipi%2Fautonomous_pen_plotter_concept%2Fblob%2Fmain%2Fworlds%2Fpenbot.wbt&type=demo)  
While actual pen drawing is not yet supported on webots.cloud, we simulate it by displaying the robot's trail in green lines.

### Run the simulation on Webots desktop app
Download the Webots desktop app from [Cybertronics site](https://cyberbotics.com/) for free.  
On the desktop version, watch the robot drawing paths in black ink.

### Video of simulation run on webots desktop app
View a video recording of the simulation running on the Webots desktop app here. This gives a closer look at the PEN feature, not yet available on webots.cloud.
https://github.com/fumipi/autonomous_pen_plotter_concept/assets/21126482/b362b177-f326-418f-9efe-393e62d9b924

### SVG file uploader app
Customize the robot's drawing using this [simple app](https://svgfileuploader-exgabjzrvp2vcszu7pyqbe.streamlit.app/)  I developed. The app accepts SVG images from Vectorizer.ai, supporting lines and bezier curves. Note: Arcs in SVG files are currently unsupported. Find the app's repository [here](https://github.com/fumipi/svg_file_uploader).

### note
This is an initial phase, with the robot currently operated via the "supervisor" controller. Future plans include enhancing its autonomy with sensors.
