from PIL import Image, ImageDraw, ImageFont
import os

if os.uname().machine == "x86_64":
    import mock.SSD1306_I2CMock as SSD1306_I2C
else:
    from adafruit_ssd1306 import SSD1306_I2C



class Display:
    image: Image.Image
    draw: ImageDraw.ImageDraw
    display: SSD1306_I2C

    def __init__(self, display) -> None:
        self.display = display

    def displayText(self, text):
        # Draw Some Text
        font = ImageFont.truetype(
            "DejaVuSansMono.ttf", min(200//len(text), 20))
        font_width, font_height = font.getsize(text)
        self.draw.text((self.display.width//2 - font_width//2, self.display.height//2 - font_height//2),
                       text, font=font, fill=255)

    def drawProgressBar(self, percent):
        y = 50
        height = 10
        fillHeight = height - 4
        x = 10
        width = self.display.width-2*x
        fillWidth = max(0, width * (percent/100) - 4)
        self.draw.rectangle((x, y, x+width, y+height), fill=None, outline=1)
        self.draw.rectangle((x+2, y+2, x+2+fillWidth, y+2+fillHeight), fill=1)
        # for x2 in range(x, width+x+1):
        #     for y2 in range(y, height+y+1):
        #         display.pixel(x2, y2, image.getpixel((x2, y2)))

    def setup(self):
        # Make sure to create image with mode '1' for 1-bit color.
        self.image = Image.new('1', (self.display.width, self.display.height))
        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

    def clear(self):
        self.setup()

    def show(self):
        max_tries = 3
        # multiple tries because of possible io error especially with jumper cables
        for i in range(0, max_tries):
            try:
                self.display.image(self.image)
                self.display.show()
                return
            except Exception as e:
                print(e)


class mockDisplay():
    def __init__(self) -> None:
        self.width = 128
        self.height = 64

    def image(self, img):
        pass

    def show(self):
        pass
