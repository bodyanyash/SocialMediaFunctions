import random
from PIL import Image, ImageDraw, ImageFont
import sys
import textwrap
import markovify


def add_random_shape(base, Color='random'):
    x1 = random.randrange(1280)
    x2 = x1 + random.randrange(1280 - x1)
    y1 = random.randrange(720)
    y2 = y1 + (x2 - x1)
    skewx = random.randrange(2)
    skewy = random.randrange(2)
    x1, x2, y1, y2 = skewx * x1, skewx * x2, skewy * y1, skewy * y2
    theta1 = random.randrange(360)
    theta2 = theta1 + random.randrange(360)
    width = int(random.randrange(10))
    radius = random.randrange(720)
    sides = int(random.randrange(9))
    shapes = ['triangle', 'pentagon', 'hexagon', 'octagon']
    shape = random.choice(shapes)
    if Color == 'random':
        fill = (random.randrange(255), random.randrange(255), random.randrange(255), random.randrange(255))
    else:
        fill = Color
    txt = Image.new('RGBA', base.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(txt)
    choice = random.choice([1, 2, 3, 4, 5, 6])
    if choice == 1:
        draw.chord((x1, y1, x2, y2), theta1, theta2, fill=fill, width=width)
    elif choice == 2:
        draw.ellipse((x1, y1, x2, y2), fill=fill, width=width)
    elif choice == 3:
        draw.line((x1, y1, x2, y2), fill=fill, width=width)
    elif choice == 4:
        draw.pieslice((x1, y1, x2, y2), theta1, theta2, fill=fill)

        # draw.polygon((x1, y1, radius), sides, fill=fill, rotation=theta1)
    elif choice == 5:
        draw.rectangle((x1, y1, x2, y2), fill=fill, width=width)
    elif choice == 6:
        draw.arc((x1, y1, x2, y2), theta1, theta2, fill=fill, width=width)

        # draw.shape(shape, fill=fill)

    return Image.alpha_composite(base, txt)


def add_logo(base, logo='logoWhite.png'):
    logo = Image.open(logo).convert("RGBA")
    w, h = logo.size
    w2, h2 = base.size
    if w / h >= w2 / h2:
        logo = logo.resize((w2, int(h * w2 / w)))
    else:
        logo = logo.resize((int(w * h2 / h), h2))

    base.paste(logo, (0, 0), logo)
    return base


def make_thumbnail(Text="Title", Color=(229, 62, 62, 255), Logo='logoWhite.png', OutFile='pil_text_font.png', Entity="Trawvid Sec"):
    img = img = Image.new('RGBA', (1280, 720), color=(0, 0, 0, 255))
    for n in range(random.randrange(30, 100)):
        print(n)
        img = add_random_shape(img, Color)

    img = add_logo(img, Logo)
    fact = 1
    flag = 0



    # Find the right size for the Title Text
    while flag == 0:
        print("Text", Text, " : ", int(len(Text) / fact))
        Title = textwrap.wrap(Text, width=int(len(Text) / fact), break_long_words=False)
        #print(len(Title), Title)
        size = 600 / (len(Title) + 1)
        fnt = ImageFont.truetype('Fonts/Roboto-BoldCondensedItalic.ttf', int(size))
        #print(fnt.getsize(Title[0])[0])
        for line in Title:
            if fnt.getsize(line)[0] > (1280 / 2) and int(len(Text) / (fact + 1)) != 0:
                fact += 1
                break
            elif line == Title[-1]:
                flag = 1

    d = ImageDraw.Draw(img)
    offset = 10
    for line in Title:
        d.text((600, offset), line, font=fnt, fill=(255, 255, 255, 255), stroke_width=10, stroke_fill='black')
        offset += fnt.getsize(line)[1]
    fnt = ImageFont.truetype('Fonts/VT323.ttf', 50)
    d.text((0, 0), Entity, font=fnt, fill=(255, 255, 255, 255), stroke_width=10, stroke_fill='black')

    img.show()
    img.save(OutFile)

    return OutFile




''''''
with open("../Jokes.txt", encoding='UTF-8') as f:
      text = f.read()

text_model = markovify.Text(text)
in_file = 'pil_text_font.png'
out_file = 'pil_text_font.png'
text = text_model.make_sentence()
print(text)
font = ImageFont.truetype('Fonts/AmaticSC.ttf', 100)
Text = None
while Text is None:
    Text = text_model.make_sentence()
make_thumbnail(Text, 'random')

