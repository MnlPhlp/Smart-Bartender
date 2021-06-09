# Smart Bartender
This is a modified version of the [smart-bartender](https://youtu.be/2DopvpNF7J4) from Hacker Shack. It can be controlled via a webpage or an alexa skill.

For the building and electronics part watch the video or check the [hackster.io page](https://www.hackster.io/hackershack/smart-bartender-5c430e) of the original project.

## changes in the build
- switched the peristaltic pump for some cheaper and faster water pumps like [these](https://www.ebay.de/itm/131976810073?var=432870985005)
- using a [neopixel ring](https://www.adafruit.com/product/1463) for lighting
- using a [raspberry pi zero](https://www.raspberrypi.org/products/raspberry-pi-zero/) for control

## setup
To setup your pi you need to first install [circuitpython](https://learn.adafruit.com/circuitpython-on-raspberrypi-linux/installing-circuitpython-on-raspberry-pi). After that run:
```
curl https://raw.githubusercontent.com/MnlPhlp/Smart-Bartender/master/setup.sh | bash
```
This will clone the repository, create a venv and install necessary libraries. 
## start
To run the bartender `cd` into Smart-Bartender and start the program with:
```
sudo python bartender.py
```
> sudo is required for the neopixels to work