import os
from PIL import Image, ImageDraw, ImageFont, ImageChops, ImageOps, ImageFilter

def make_white_and_alpha(img_path):
    # Loads an image, converts it to RGBA, and handles color treatment.
    # If the image has dark pixels on a white/transparent background,
    # we invert it or map it to white text so it displays beautifully on our black background.
    try:
        img = Image.open(img_path).convert('RGBA')
        
        # Split channels
        r, g, b, a = img.split()
        
        # Calculate average brightness of RGB channels
        gray = img.convert('L')
        pixels = list(gray.getdata())
        avg_brightness = sum(pixels) / len(pixels)
        
        # If it's a dark logo on a light background, invert it
        if avg_brightness < 127:
            # Dark logo: we want it to be white
            # Create a solid white image and use the inverted original as the mask
            white_img = Image.new('RGBA', img.size, (255, 255, 255, 255))
            # If the original has transparency, we combine the transparency
            # otherwise we use brightness as alpha
            mask = gray.point(lambda x: 255 - x)
            # Combine original alpha if present
            mask = ImageChops.darker(mask, a)
            white_img.putalpha(mask)
            return white_img
        else:
            # Light logo or already white
            # Just force the non-transparent pixels to be white
            white_img = Image.new('RGBA', img.size, (255, 255, 255, 255))
            # Use original alpha or invert the black pixels if no alpha
            if img.mode == 'RGBA' and a.getextrema()[1] > 0:
                white_img.putalpha(a)
            else:
                mask = gray.point(lambda x: 255 - x)
                white_img.putalpha(mask)
            return white_img
    except Exception as e:
        print(f"Error processing logo {img_path}: {e}")
        return None

def create_gradient_mask(width, height, start_y, end_y):
    # Creates a vertical gradient mask that starts from fully transparent (0)
    # at start_y and becomes fully opaque black (255) at end_y.
    mask = Image.new('L', (width, height), 0)
    draw = ImageDraw.Draw(mask)
    for y in range(start_y, min(end_y, height)):
        alpha = int(255 * (y - start_y) / (end_y - start_y))
        draw.line([(0, y), (width, y)], fill=alpha)
    if end_y < height:
        draw.rectangle([(0, end_y), (width, height)], fill=255)
    return mask

def render_dates_table(draw, dates, start_x, start_y, row_height, font_regular, font_bold, width):
    # Renders the tour dates in a clean table format.
    # - Day: Bold, Left-aligned at 6% of width
    # - Month: Regular, Left-aligned at 12% of width
    # - Venue: Bold, Left-aligned at 20% of width
    # - City: Bold, Right-aligned to 78% of width
    # - Country: Regular, Right-aligned to 94% of width
    x_day = int(width * 0.06)
    x_month = int(width * 0.12)
    x_venue = int(width * 0.20)
    x_city_end = int(width * 0.78)
    x_country_end = int(width * 0.94)

    y = start_y
    for day, month, venue, city, country in dates:
        # Draw Day
        draw.text((x_day, y), day, fill=(255, 255, 255, 255), font=font_bold)
        
        # Draw Month
        draw.text((x_month, y), month, fill=(255, 255, 255, 255), font=font_regular)
        
        # Draw Venue
        draw.text((x_venue, y), venue, fill=(255, 255, 255, 255), font=font_bold)
        
        # Draw City (right-aligned to x_city_end)
        city_w = draw.textlength(city, font=font_bold) if hasattr(draw, 'textlength') else draw.textsize(city, font=font_bold)[0]
        draw.text((x_city_end - city_w, y), city, fill=(255, 255, 255, 255), font=font_bold)
        
        # Draw Country (right-aligned to x_country_end)
        country_w = draw.textlength(country, font=font_regular) if hasattr(draw, 'textlength') else draw.textsize(country, font=font_regular)[0]
        draw.text((x_country_end - country_w, y), country, fill=(255, 255, 255, 255), font=font_regular)
        
        y += row_height

def generate_social_images():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    artist_dir = os.path.dirname(script_dir)
    sources_dir = os.path.join(artist_dir, "Sources_and_Assets")
    
    bg_path = os.path.join(sources_dir, "gui boratto_edit_pb--11.JPEG")
    logo_path = os.path.join(sources_dir, "gui boratto logo.png")
    
    # 1. Load Background Image
    print("Loading background image...")
    bg_large = Image.open(bg_path).convert('RGBA')
    bg_w, bg_h = bg_large.size
    
    # 2. Tour Dates Data
    dates = [
        ("13", "JUN", "EPHIGENIA", "SÃO PAULO", "BRAZIL"),
        ("14", "JUN", "ALDEA ANNIVERSARY", "BUENOS AIRES", "ARGENTINA"),
        ("19", "JUN", "L'AVVENTURA", "BASEL", "SWITZERLAND"),
        ("21", "JUN", "AKASHA", "IBIZA", "SPAIN"),
        ("22", "JUN", "OPEN AIR LISBON X LUNA", "LISBON", "PORTUGAL"),
        ("25", "JUN", "MACARENA", "BARCELONA", "SPAIN"),
        ("28", "JUN", "RF & POV AT WAIKIKI BEACH CLUB", "COSTA DA CAPARICA", "PORTUGAL"),
        ("12", "JUL", "HIVE", "ZURICH", "SWITZERLAND"),
        ("18", "JUL", "PACHA", "MUNICH", "GERMANY"),
        ("19", "JUL", "VANITY AT XOYO", "LONDON", "U. KINGDOM"),
        ("24", "JUL", "VAGALUME", "TULUM", "MEXICO"),
        ("25", "JUL", "SALON AMADOR", "MEDELLIN", "COLOMBIA"),
        ("26", "JUL", "LOOLOO", "JUÁREZ", "MEXICO"),
        ("02", "AUG", "SILENCIO", "PARIS", "FRANCE"),
        ("09", "AUG", "LOVELAND FESTIVAL", "AMSTERDAM", "NETHERLANDS"),
        ("16", "AUG", "DOC SHOWCASE", "CAMPINAS", "BRAZIL"),
    ]
    
    # Fonts
    font_path_regular = "/System/Library/Fonts/Supplemental/Arial.ttf"
    font_path_bold = "/System/Library/Fonts/Supplemental/Arial Bold.ttf"
    
    # Load Logo
    print("Loading artist logo...")
    artist_logo = Image.open(logo_path).convert('RGBA')
    
    # Process Sponsor/Label Logos
    print("Processing bottom logos...")
    bottom_logo_files = ["DOC_AVATAR6.PNG", "metropole logo.png", "dukermusic_logo_white.PNG"]
    processed_logos = []
    for f in bottom_logo_files:
        path = os.path.join(sources_dir, f)
        if os.path.exists(path):
            p_logo = make_white_and_alpha(path)
            if p_logo:
                processed_logos.append(p_logo)
    
    # Add the small banner logo if it fits
    banner_logo_path = os.path.join(sources_dir, "cf99ade3-9b45-4736-b77b-c7c36707688f.JPG")
    if os.path.exists(banner_logo_path):
        p_logo = make_white_and_alpha(banner_logo_path)
        if p_logo:
            processed_logos.append(p_logo)

    # -------------------------------------------------------------
    # GENERATE INSTAGRAM POST (1080 x 1350)
    # -------------------------------------------------------------
    print("Generating Instagram Post (1080x1350)...")
    post_w, post_h = 1080, 1350
    
    # Crop the background image
    crop_w_post = 2174
    crop_h_post = 2718
    crop_x_post = int(1843 - crop_w_post/2) # 756
    crop_y_post = 2732
    
    crop_box_post = (crop_x_post, crop_y_post, crop_x_post + crop_w_post, crop_y_post + crop_h_post)
    post_bg = bg_large.crop(crop_box_post).resize((post_w, post_h), Image.Resampling.LANCZOS)
    
    # Apply vertical gradient to black
    gradient_post = create_gradient_mask(post_w, post_h, int(post_h * 0.25), int(post_h * 0.85))
    black_layer = Image.new('RGBA', (post_w, post_h), (0, 0, 0, 255))
    post_composite = Image.composite(black_layer, post_bg, gradient_post)
    
    # Draw interface
    draw_post = ImageDraw.Draw(post_composite)
    
    # Resize and place Artist Logo
    logo_w_post = 900
    logo_h_post = int(artist_logo.height * (logo_w_post / artist_logo.width))
    logo_resized_post = artist_logo.resize((logo_w_post, logo_h_post), Image.Resampling.LANCZOS)
    logo_x = (post_w - logo_w_post) // 2
    logo_y = 50
    post_composite.paste(logo_resized_post, (logo_x, logo_y), logo_resized_post)
    
    # Load fonts at appropriate size for Post
    font_title_post = ImageFont.truetype(font_path_bold, 22)
    font_reg_post = ImageFont.truetype(font_path_regular, 16)
    font_bold_post = ImageFont.truetype(font_path_bold, 16)
    
    # Draw "N E X T  D A T E S"
    title_text = "N E X T   D A T E S"
    draw_post.text((int(post_w * 0.06), 460), title_text, fill=(255, 255, 255, 255), font=font_title_post)
    
    # Render dates table
    render_dates_table(
        draw=draw_post,
        dates=dates,
        start_x=int(post_w * 0.06),
        start_y=510,
        row_height=42,
        font_regular=font_reg_post,
        font_bold=font_bold_post,
        width=post_w
    )
    
    # Render Bottom Logos
    logo_h_bottom = 30
    total_w_bottom = 0
    resized_bottom_logos = []
    
    for logo in processed_logos:
        lh = logo_h_bottom
        lw = int(logo.width * (lh / logo.height))
        l_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        resized_bottom_logos.append(l_resized)
        total_w_bottom += lw + 30 # 30px spacing
        
    total_w_bottom -= 30 # remove trailing spacing
    
    start_x_logos = (post_w - total_w_bottom) // 2
    y_logos = 1240
    current_x = start_x_logos
    
    for l_resized in resized_bottom_logos:
        post_composite.paste(l_resized, (current_x, y_logos), l_resized)
        current_x += l_resized.width + 30
        
    # Save Post images
    post_composite_rgb = post_composite.convert('RGB')
    post_output_dir = os.path.join(artist_dir, "Final_Deliverables", "Instagram_Posts_4_5")
    os.makedirs(post_output_dir, exist_ok=True)
    post_composite_rgb.save(os.path.join(post_output_dir, "post_tour_dates.jpg"), "JPEG", quality=95)
    post_composite.save(os.path.join(post_output_dir, "post_tour_dates.png"), "PNG")
    print("Instagram Post saved successfully!")

    # -------------------------------------------------------------
    # GENERATE INSTAGRAM STORY / REEL (1080 x 1920)
    # -------------------------------------------------------------
    print("Generating Instagram Story (1080x1920)...")
    story_w, story_h = 1080, 1920
    
    # Crop the background image
    crop_w_story = 1528
    crop_h_story = 2718
    crop_x_story = int(1843 - crop_w_story/2) # 1079
    crop_y_story = 2732
    
    crop_box_story = (crop_x_story, crop_y_story, crop_x_story + crop_w_story, crop_y_story + crop_h_story)
    story_bg = bg_large.crop(crop_box_story).resize((story_w, story_h), Image.Resampling.LANCZOS)
    
    # Apply vertical gradient to black
    gradient_story = create_gradient_mask(story_w, story_h, int(story_h * 0.28), int(story_h * 0.85))
    black_layer_story = Image.new('RGBA', (story_w, story_h), (0, 0, 0, 255))
    story_composite = Image.composite(black_layer_story, story_bg, gradient_story)
    
    # Draw interface
    draw_story = ImageDraw.Draw(story_composite)
    
    # Resize and place Artist Logo
    logo_w_story = 940
    logo_h_story = int(artist_logo.height * (logo_w_story / artist_logo.width))
    logo_resized_story = artist_logo.resize((logo_w_story, logo_h_story), Image.Resampling.LANCZOS)
    logo_x_story = (story_w - logo_w_story) // 2
    logo_y_story = 120
    story_composite.paste(logo_resized_story, (logo_x_story, logo_y_story), logo_resized_story)
    
    # Load fonts at appropriate size for Story
    font_title_story = ImageFont.truetype(font_path_bold, 28)
    font_reg_story = ImageFont.truetype(font_path_regular, 20)
    font_bold_story = ImageFont.truetype(font_path_bold, 20)
    
    # Draw "N E X T  D A T E S"
    draw_story.text((int(story_w * 0.06), 720), title_text, fill=(255, 255, 255, 255), font=font_title_story)
    
    # Render dates table
    render_dates_table(
        draw=draw_story,
        dates=dates,
        start_x=int(story_w * 0.06),
        start_y=790,
        row_height=58,
        font_regular=font_reg_story,
        font_bold=font_bold_story,
        width=story_w
    )
    
    # Render Bottom Logos
    logo_h_bottom_story = 36
    total_w_bottom_story = 0
    resized_bottom_logos_story = []
    
    for logo in processed_logos:
        lh = logo_h_bottom_story
        lw = int(logo.width * (lh / logo.height))
        l_resized = logo.resize((lw, lh), Image.Resampling.LANCZOS)
        resized_bottom_logos_story.append(l_resized)
        total_w_bottom_story += lw + 40 # 40px spacing
        
    total_w_bottom_story -= 40 # remove trailing spacing
    
    start_x_logos_story = (story_w - total_w_bottom_story) // 2
    y_logos_story = 1790
    current_x_story = start_x_logos_story
    
    for l_resized in resized_bottom_logos_story:
        story_composite.paste(l_resized, (current_x_story, y_logos_story), l_resized)
        current_x_story += l_resized.width + 40
        
    # Save Story images
    story_composite_rgb = story_composite.convert('RGB')
    story_output_dir = os.path.join(artist_dir, "Final_Deliverables", "Instagram_Stories_Reels_9_16")
    os.makedirs(story_output_dir, exist_ok=True)
    story_composite_rgb.save(os.path.join(story_output_dir, "story_tour_dates.jpg"), "JPEG", quality=95)
    story_composite.save(os.path.join(story_output_dir, "story_tour_dates.png"), "PNG")
    print("Instagram Story saved successfully!")

if __name__ == "__main__":
    generate_social_images()
