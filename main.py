import cv2
import numpy as np


def generate_command_chain(image_path: str, output_path: str):
    """
        Generate a G-code command chain for a CNC gantry to draw an image with one continuous line.
        The image is processed into a 194x258 grid (50,052 pixels) with 11 discrete intervals (0-10) for squiggle intensity.
            - 0 = White (flat line)
              ...
            - 10 = Black (max squiggle)
        The Arduino Uno will read the 'S' parameter in each G1 command to determine how much to squiggle at that point.
        Since the resolution is 50k pixels, the finished image is surprisingly detailed for a single line drawing,
        being able to capture subtle shading, thin lines, and even some texture. See README.md for image examples and more details on the process.
    """

    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"Could not load image at {image_path}. Check your path.")

    # 194 x 258 = 50,052 pixels (~3:4 vertical aspect ratio)
    W, H = 194, 258
    img_resized = cv2.resize(img, (W, H), interpolation=cv2.INTER_AREA)

    # Quantize to 11 discrete intervals (0 to 10)
    # 0 = White (flat line), 10 = Black (max squiggle)
    quantized_img = np.floor(img_resized / 25.5).astype(np.uint8)

    # Invert the logic if needed: usually 0 in OpenCV is black.
    # If your pen needs max squiggle for black, we invert it so 0=White, 10=Black.
    quantized_img = 10 - quantized_img

    step_size = 0.1  # 0.1mm precision grid

    with open(output_path, 'w') as gcode:
        gcode.write("; 0.1mm Precision CNC Gantry - Command Chain\n")
        gcode.write("G21 ; Set units to millimeters\n")
        gcode.write("G90 ; Use absolute coordinates\n")
        gcode.write("G0 X0 Y0 ; Go to home\n\n")

        for y in range(H):
            phys_y = y * step_size

            # Snake logic: Even rows L->R, Odd rows R->L
            if y % 2 == 0:
                x_range = range(W)
            else:
                x_range = range(W - 1, -1, -1)

            for x in x_range:
                pixel_interval = quantized_img[y, x]
                phys_x = x * step_size

                # We send the X, Y, and the interval (0-10) as an 'S' parameter.
                # Arduino C++ parser reads this 'S' and executes the corresponding squiggle loop.
                gcode.write(f"G1 X{phys_x:.2f} Y{phys_y:.2f} S{pixel_interval}\n")

        gcode.write("\nG0 X0 Y0 ; Return home\n")
        gcode.write("M30 ; End of program\n")

    print(f"[*] Generated {W * H} chained commands.")
    print(f"[*] The Arduino Uno is officially the smart one in this relationship.")


if __name__ == "__main__":
    generate_command_chain("input.jpg", "output.gcode")