from PIL import Image
import os
import sys

def print_logo():
    print(r"""
 ____  _          _ ____  _          _       _    
|  _ \(_)_  _____| / ___|| |__  _ __(_)_ __ | | __
| |_) | \ \/ / _ \ \___ \| '_ \| '__| | '_ \| |/ /
|  __/| |>  <  __/ |___) | | | | |  | | | | |   < 
|_|   |_/_/\_\___|_|____/|_| |_|_|  |_|_| |_|_|\_\
                                                  
    The Cool Image Converter and Compressor!
    """)

def pixel_shrink(input_path, output_path, target_size_kb=250, quality=95):
    print(f"PixelShrinking: {input_path}")
    try:
        with Image.open(input_path) as img:
            if img.mode != 'RGB':
                img = img.convert('RGB')
            
            img.save(output_path, 'JPEG', quality=quality)
            
            while os.path.getsize(output_path) > target_size_kb * 1024 and quality > 10:
                quality -= 5
                img.save(output_path, 'JPEG', quality=quality)
        
        print(f"PixelShrink complete! Saved to: {output_path}")
        print(f"Final size: {os.path.getsize(output_path) / 1024:.2f} KB")
    except FileNotFoundError:
        print(f"Error: The file '{input_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

print_logo()

if len(sys.argv) != 3:
    print("Usage: python pixel_shrink.py <input_file> <output_file>")
    sys.exit(1)

input_file = sys.argv[1]
output_file = sys.argv[2]

pixel_shrink(input_file, output_file)
print("PixelShrink operation completed successfully!")