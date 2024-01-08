import pyroomacoustics as pra
import numpy as np
from scipy.io import wavfile
import matplotlib.pyplot as plt
from pyroomacoustics.doa import MUSIC
# from lib.doa import MUSIC


def plot_room(room: pra.ShoeBox) -> None:
    room_dim = room.get_bbox()[:, 1]

    fig = plt.figure(figsize=(8, 8))
    ax = fig.add_subplot(111, projection="3d")
    room.plot(ax=ax)

    # プロット範囲を部屋の大きさに合わせる
    ax.set_xlim([0, room_dim[0]])
    ax.set_ylim([0, room_dim[1]])
    ax.set_zlim([0, room_dim[2]])
    ax.set_box_aspect(room_dim)
    plt.show()


def main():
    side_length = 50
    fs = 16000
    nfft = 512

    room = pra.ShoeBox([side_length, side_length, side_length], fs=fs, max_order=0)

    signal = wavfile.read("data/arctic_a0001.wav")[1]
    room.add_source([1, 1, 1], signal=signal)

    mic_positions_2d = pra.circular_2D_array(
        center=(side_length / 2, side_length / 2), M=8, phi0=0, radius=0.1
    )
    new_axis = np.array([side_length / 2] * mic_positions_2d.shape[1])
    mic_positions_3d = np.concatenate(
        (mic_positions_2d[0], new_axis, mic_positions_2d[1])
    ).reshape(-1, mic_positions_2d.shape[1])
    room.add_microphone_array(mic_positions_3d)
    # plot_room(room)

    room.compute_rir()
    room.simulate()
    simulated_signal = room.mic_array.signals
    print(simulated_signal.shape)

    # フーリエ変換
    X = pra.transform.stft.analysis(
        room.mic_array.signals.T, nfft, nfft // 4, win=np.hanning(nfft)
    )
    X = np.swapaxes(X, 2, 0)

    doa = MUSIC(
        mic_positions_3d,
        fs,
        nfft,
    )
    doa.locate_sources(X, num_src=1)
    print(doa.grid.azimuth.shape)
    print(doa.grid.values.shape)
    doa.grid.plot()
    plt.show()


if __name__ == "__main__":
    main()
