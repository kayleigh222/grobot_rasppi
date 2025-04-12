import qrcode
from PIL import Image, ImageDraw, ImageFont
import os

# Output folder
output_folder = "qr_codes_numbered"
os.makedirs(output_folder, exist_ok=True)

# Try loading a clean sans-serif font
try:
    font = ImageFont.truetype("arial.ttf", 24)
except:
    font = ImageFont.load_default()

for i in range(1, 9):
    data = f"Plant {i}"  # Still encode full data
    number_label = str(i)  # Just the number to display

    # Generate QR code
    qr = qrcode.QRCode(box_size=10, border=4)
    qr.add_data(data)
    qr.make(fit=True)
    qr_img = qr.make_image(fill_color="black", back_color="white").convert("RGB")

    # Draw number in top-right corner
    draw = ImageDraw.Draw(qr_img)
    text_bbox = draw.textbbox((0, 0), number_label, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]

    padding = 5
    x = qr_img.width - text_width - padding
    y = padding

    draw.text((x, y), number_label, fill="black", font=font)

    # Save the labeled QR image
    filename = os.path.join(output_folder, f"plant_{i}.png")
    qr_img.save(filename)
    print(f"Saved: {filename}")



# import qrcode
# import os

# # Output folder (change if you want)
# output_folder = "qr_codes"
# os.makedirs(output_folder, exist_ok=True)

# # Generate QR codes for Plant 1 to Plant 8
# for i in range(1, 9):
#     data = f"Plant {i}"
#     img = qrcode.make(data)
    
#     filename = os.path.join(output_folder, f"plant_{i}.png")
#     img.save(filename)
#     print(f"Saved QR code for '{data}' at: {filename}")