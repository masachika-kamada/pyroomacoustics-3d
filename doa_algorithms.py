import argparse

import matplotlib.pyplot as plt
import numpy as np
import pyroomacoustics as pra
from display_grid_sphere import plot_grid_sphere
from tabulate import tabulate

methods = ["MUSIC", "FRIDA", "WAVES", "TOPS", "CSSM", "SRP", "NormMUSIC"]


def main(args):
    # we use a white noise signal for the source
    nfft = 256
    fs = 16000
    x = np.random.randn((nfft // 2 + 1) * nfft)

    # create anechoic room
    # room = pra.AnechoicRoom(fs=fs)
    l = 15
    l_half = l / 2
    room = pra.ShoeBox([l, l, l], fs=fs, absorption=1.0, max_order=0)

    # ソースの極座標系パラメータ
    radius = 5  # 半径
    # 方位角
    azimuth_true = -np.pi / 3
    # 天頂角
    colatitude_true = np.pi / 4

    # XYZ座標の計算
    source_x = radius * np.sin(colatitude_true) * np.cos(azimuth_true) + l_half
    source_y = radius * np.sin(colatitude_true) * np.sin(azimuth_true) + l_half
    source_z = radius * np.cos(colatitude_true) + l_half
    room.add_source([source_x, source_y, source_z], signal=x)

    # place the microphone array
    mic_locs = np.array(
        [
            [0.1 + l_half, l_half, l_half],
            [-0.1 + l_half, l_half, l_half],
            [l_half, 0.1 + l_half, l_half],
            [l_half, -0.1 + l_half, l_half],
            [l_half, l_half, 0.1 + l_half],
            [l_half, l_half, -0.1 + l_half],
        ]
    ).T
    room.add_microphone_array(mic_locs)

    # run the simulation
    room.simulate()

    room.plot()
    plt.show()

    # create frequency-domain input for DOA algorithms
    X = pra.transform.stft.analysis(
        room.mic_array.signals.T, nfft, nfft // 2, win=np.hanning(nfft)
    )
    X = np.swapaxes(X, 2, 0)

    # perform DOA estimation
    doa = pra.doa.algorithms[args.method](mic_locs, fs, nfft, dim=3)
    doa.locate_sources(X)

    # 表示
    data = [
        ["Azimuth", np.rad2deg(azimuth_true), np.rad2deg(doa.azimuth_recon[0])],
        ["Colatitude", np.rad2deg(colatitude_true), np.rad2deg(doa.colatitude_recon[0])],
    ]
    headers = ["Parameter", "Real Source (degrees)", "Estimated Source (degrees)"]
    print(tabulate(data, headers, tablefmt="grid"))

    plot_grid_sphere(doa.grid.cartesian, doa.grid.values)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Estimates the DoA of a sound source.")
    parser.add_argument(
        "--method",
        "-m",
        choices=methods,
        default=methods[0],
        help="DOA method to use",
    )
    args = parser.parse_args()

    main(args)
