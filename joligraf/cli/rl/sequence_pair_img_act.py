from pathlib import Path

import click
import holoviews as hv
import numpy as np
from tqdm import tqdm
from pprint import pformat

hv.extension("bokeh")


@click.command()
@click.argument("data_sequence_folder", type=click.Path(exists=True))
@click.option("--limit", type=int, default=42)
@click.option("--start", type=int, default=0)
@click.option("--out", type=str, default=0)
def main(data_sequence_folder: str, limit: int, start: int, out: str):
    root = Path(data_sequence_folder)
    img_folder_path = root.joinpath("imgs/")
    npz_filepath = root.joinpath("rendered.npz")

    data = np.load(npz_filepath)
    datasource = {key: data[key] for key in data.files}

    images_filepaths = list(img_folder_path.glob("*.png"))
    images_filepaths.sort()

    limit = min(start + limit, len(images_filepaths) - 1)

    with_slides = {}
    for idx, filepath in enumerate(tqdm(images_filepaths[start:limit])):
        dataframe = dict([(key, str(value[start + idx])) for key, value in datasource.items()])

        image = hv.RGB.load_image(str(filepath))
        image.opts(title=f"Frame #{idx+1}")
        table = hv.Div(pformat(dataframe).replace("\n", "</br>"))
        fig = image + table
        with_slides[idx + 1] = fig

    data.close()
    hmap = hv.HoloMap(with_slides, "frame")
    hmap = hmap.collate()

    path_info = hv.Div(f"Sequence from {str(img_folder_path.parent)}")

    layout = hv.Layout([path_info] + [hmap])

    hv.save(layout, "holomap.html")


if __name__ == "__main__":
    main()
