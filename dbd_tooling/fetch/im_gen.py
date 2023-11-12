from pathlib import Path
from PIL import Image
import tempfile

_backgrounds = [
    "assets/perk_bg_uncommon.png",
    "assets/perk_bg_rare.png",
    "assets/perk_bg_very_rare.png",
]

_levels = [
    "assets/perk_level_1.png",
    "assets/perk_level_2.png",
    "assets/perk_level_3.png",
]


def generate_frames(input_img_path, folder_path):
    Path(folder_path).mkdir(parents=True, exist_ok=True)

    frames = []

    with Image.open(input_img_path) as input_img:
        for i in range(0, 3):
            frame_path = f"{folder_path}/frame_{i}.png"
            with Image.open(_backgrounds[i]) as bg_img:
                output_img = _combine_imgs(input_img, bg_img)
                output_img.save(frame_path)
            frames.append(frame_path)

    return frames


def generate_gif(frame_paths, output_path):
    temp_files = [
        tempfile.NamedTemporaryFile(mode="wb", suffix=".png", delete=True)
        for _ in range(0, 3)
    ]
    _add_levels(frame_paths, temp_files)

    images = []

    for file in temp_files:
        images.append(Image.open(file.name))

    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        optimize=True,
        duration=1000,
        loop=True,
    )

    for image in images:
        image.close()
    for file in temp_files:
        file.close()


def _add_levels(frame_paths, output_frames):
    for i, frame in enumerate(frame_paths):
        with Image.open(_levels[i]) as lvl_img, Image.open(frame) as bg_img:
            output_img = _combine_imgs(lvl_img, bg_img)
            output_img.save(output_frames[i])


def _combine_imgs(foreground, background):
    if foreground.size != background.size:
        print("error: images can't have different sizes.")
        raise RuntimeError("Images can't have different sizes.")

    foreground = foreground.convert("RGBA")

    background = Image.alpha_composite(
        Image.new("RGBA", background.size), background.convert("RGBA")
    )

    x = 0
    y = 0

    background.paste(foreground, (x, y), foreground)
    return background


# TODO: Maybe worth writing tests for instead of these manual test cases.
# FOR TESTING PURPOSES
# with Image.open(
#     "data/perks/killers/a_nurses_calling/Anursescalling.png"
# ) as input_img, Image.open(_backgrounds[0]) as bg_img:
#     input_img.save("test1.png")
#     bg_img.save("test2.png")

#     output_img = _combine_imgs(input_img, bg_img)
#     output_img.save("test_output.png")


# generate_frames(
#     "data/perks/killers/a_nurses_calling/Anursescalling.png",
#     "data/perks/killers/a_nurses_calling",
# )

# generate_gif(
#     [
#         "data/perks/killers/a_nurses_calling/frame_0.png",
#         "data/perks/killers/a_nurses_calling/frame_1.png",
#         "data/perks/killers/a_nurses_calling/frame_2.png",
#     ],
#     "im.gif",
# )
