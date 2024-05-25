import requests
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
import qrcode
import logging
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Function to fetch contestant data
def fetch_contestant_data(contestant_slug):
    url = f'https://khalti.com/api/v2/vcontestant/{contestant_slug}/'
    response = requests.get(url)
    return response.json()

# Example slug (this will be passed by the frontend)
contestant_slug = "305DD8X"

# Start the timer
start_time = time.time()

# Fetch the data from the API
data = fetch_contestant_data(contestant_slug)

# Extract the necessary data
name = data['name']
image_url = data['image']
cta_link = data['cta_link']
title = data['contest']['name']

# Fetch and compress the contestant's image
image_response = requests.get(image_url)
contestant_image = Image.open(BytesIO(image_response.content))

# Compress the image to 50% quality
buffer = BytesIO()
contestant_image.save(buffer, format="JPEG", quality=50)
buffer.seek(0)
contestant_image = Image.open(buffer)

# Define the coordinates and size for the circular image
left, top = 397, 308
circle_diameter = 285
size = (circle_diameter, circle_diameter)

# Create a circular mask
mask = Image.new('L', size, 0)
draw = ImageDraw.Draw(mask)
draw.ellipse((0, 0, circle_diameter, circle_diameter), fill=255)

# Resize and crop the contestant's image to fit within the circle
contestant_image = contestant_image.resize(size, Image.LANCZOS)
circle_contestant_image = Image.new('RGBA', size)
circle_contestant_image.paste(contestant_image, (0, 0), mask=mask)

# Open the vote.png image
vote_image = Image.open('vote.png').convert('RGBA')

# Paste the circular image onto the vote image
vote_image.paste(circle_contestant_image, (left, top), mask=circle_contestant_image)

# Load the Poppins font
font_path = "Poppins-SemiBold.ttf"  # Update this path if necessary
font_size = 50
font = ImageFont.truetype(font_path, font_size)

# Draw the name at the specified coordinates
draw = ImageDraw.Draw(vote_image)
text_position = (549, 653)
draw.text(text_position, name, fill='white', font=font, anchor="mm")

# Draw the title at the specified coordinates
title_font_size = 30
title_font_path = "Poppins-Regular.ttf"
title_font = ImageFont.truetype(title_font_path, title_font_size)
title_position = (537, 714)
draw.text(title_position, title, fill='white', font=title_font, anchor="mm")

# Generate the QR code
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_L,
    box_size=10,
    border=4,
)
qr.add_data(cta_link)
qr.make(fit=True)
qr_img = qr.make_image(fill='black', back_color='white').convert('RGBA')

# Resize the QR code to fit the specified coordinates
qr_size = (799 - 266, 1376 - 850)
qr_img = qr_img.resize(qr_size, Image.LANCZOS)

# Paste the QR code onto the vote image
vote_image.paste(qr_img, (266, 850), mask=qr_img)

# Show the output image (comment this line if not necessary)
vote_image.show()

# Save the output image
vote_image.save('final_vote_image.png')

# End the timer and log the time taken
end_time = time.time()
time_taken = end_time - start_time
logger.info(f"Time taken to generate the image: {time_taken:.2f} seconds")