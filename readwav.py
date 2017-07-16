
import struct


def big_end(b):
    return b.decode("ascii")


def lit_end(b):
    length = len(b)
    if length == 2:
        return struct.unpack_from("<h", b)[0]
    elif length == 4:
        return struct.unpack_from("<i", b)[0]
    elif length == 8:
        return struct.unpack_from("<q", b)[0]
    else:
        raise NotImplemented


def read_data(fp, size, unit=2048):
    data = []
    for _ in range(0, size, unit):
        data.append(fp.read(unit))
    return data


class WaveFile(object):
    pass


wave_data = WaveFile()
with open("sample.wav", 'rb') as fp:
    wave_data.chunkid = big_end(fp.read(4))
    wave_data.chunksize = lit_end(fp.read(4))
    wave_data.wave_format = big_end(fp.read(4))

    wave_data.subchunk_1_id = big_end(fp.read(4))
    wave_data.subchunk_1_size = lit_end(fp.read(4))
    wave_data.audio_format = lit_end(fp.read(2))
    wave_data.num_channels = lit_end(fp.read(2))
    wave_data.sample_rate = lit_end(fp.read(4))
    wave_data.byterate = lit_end(fp.read(4))
    wave_data.block_align = lit_end(fp.read(2))
    wave_data.bits_per_sample = lit_end(fp.read(2))

    wave_data.subchunk_2_id = big_end(fp.read(4))
    wave_data.subchunk_2_size = lit_end(fp.read(4))

    infosize = int(wave_data.subchunk_2_size)
    wave_data.info = big_end(fp.read(infosize))
    wave_data.info_rest = fp.read(9)

    data_size = int(wave_data.chunksize - 36)
    channels = int(wave_data.num_channels)
    wave_data.data = read_data(fp, data_size, unit=2048)

with open("data.txt", 'wb') as fp:
    for data in wave_data.data:
        fp.write(data)
