from PIL import Image, ImageDraw, ImageFont


def displayText(display, text):
    draw, image = getCanvas(display)

    # Draw Some Text
    font = ImageFont.truetype(
        "C:/Windows/Fonts/NotoMono-Regular.ttf", min(200//len(text), 40))
    font_width, font_height = font.getsize(text)
    draw.text((display.width//2 - font_width//2, display.height//2 - font_height//2),
              text, font=font, fill=255)
    display.image(image)


def drawProgressBar(display, percent):
    draw, image = getCanvas(display)
    y = 50
    height = 10
    fillHeight = height - 4
    x = 10
    width = display.width-2*x
    fillWidth = width * (percent/100) - 4
    draw.rectangle((x, y, x+width, y+height), fill=None, outline=1)
    draw.rectangle((x+2, y+2, x+2+fillWidth, y+2+fillHeight), fill=1)
    for x2 in range(x, width+x+1):
        for y2 in range(y, height+y+1):
            display.pixel(x2, y2, image.getpixel((x2, y2)))


def getCanvas(display):
    # Make sure to create image with mode '1' for 1-bit color.
    image = Image.new('1', (display.width, display.height))
    # Get drawing object to draw on image.
    draw: ImageDraw.ImageDraw = ImageDraw.Draw(image)
    return draw, image


class mockDisplay():
    imageData: Image.Image = None

    def __init__(self) -> None:
        self.width = 128
        self.height = 64

    def image(self, image):
        self.imageData = image

    def pixel(self, x, y, color):
        self.imageData.putpixel((x, y), color)

    def show(self):
        self.imageData.show()


if __name__ == "__main__":
    dsp = mockDisplay()
    displayText(dsp, "Jacky Cola")
    drawProgressBar(dsp, 20)
    dsp.show()
