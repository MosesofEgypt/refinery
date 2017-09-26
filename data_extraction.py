import arbytmap
import re
if not hasattr(arbytmap, "FORMAT_P8"):
    arbytmap.FORMAT_P8 = "P8-BUMP"

    """ADD THE P8 FORMAT TO THE BITMAP CONVERTER"""
    arbytmap.define_format(
        format_id=arbytmap.FORMAT_P8, raw_format=True, channel_count=4,
        depths=(8,8,8,8), offsets=(24,16,8,0),
        masks=(4278190080, 16711680, 65280, 255))

from arbytmap import Arbytmap, TYPE_2D, TYPE_3D, TYPE_CUBEMAP,\
     FORMAT_A8, FORMAT_Y8, FORMAT_AY8, FORMAT_A8Y8,\
     FORMAT_R5G6B5, FORMAT_A1R5G5B5, FORMAT_A4R4G4B4,\
     FORMAT_X8R8G8B8, FORMAT_A8R8G8B8,\
     FORMAT_DXT1, FORMAT_DXT3, FORMAT_DXT5, FORMAT_P8, FORMAT_U8V8,\
     FORMAT_R16G16B16F, FORMAT_A16R16G16B16F,\
     FORMAT_R32G32B32F, FORMAT_A32R32G32B32F
    
from os import makedirs
from os.path import dirname, exists, join
from struct import unpack, pack_into
from traceback import format_exc

from supyr_struct.buffer import BytearrayBuffer
from supyr_struct.defs.constants import *
from supyr_struct.defs.util import *
from supyr_struct.defs.audio.wav import wav_def
from supyr_struct.field_types import FieldType
from refinery.util import is_protected_tag, fourcc, is_reserved_tag
from refinery.util_h2 import *
from reclaimer.adpcm import decode_adpcm_samples
from reclaimer.hek.defs.objs.p8_palette import load_palette

#load the palette for p-8 bump maps
P8_PALETTE = load_palette()

#each sub-bitmap(cubemap face) must be a multiple of 128 bytes
CUBEMAP_PADDING = 128

BAD_PATH_CHAR_REMOVAL = re.compile(r'[<>:"|?*]{1, }')


def get_pad_size(size, mod): return (mod - (size % mod)) % mod


def save_sound_perms(permlist, filepath_base, sample_rate,
                     channels=1, overwrite=True, decode_adpcm=True):
    wav_file = wav_def.build()
    for i in range(len(permlist)):
        encoding, samples = permlist[i]
        filepath = filepath_base
        if not samples:
            continue

        if len(permlist) > 1: filepath += "__%s" % i

        if encoding in ("ogg", "wma"):
            filepath += ".%s" % encoding
        else:
            filepath += ".wav"

        filepath = BAD_PATH_CHAR_REMOVAL.sub("_", filepath)

        if exists(filepath) and not overwrite:
            continue

        if encoding in ("ogg", "wma"):
            try:
                folderpath = dirname(filepath)
                # If the path doesnt exist, create it
                if not exists(folderpath):
                    makedirs(folderpath)

                with open(filepath, "wb") as f:
                    f.write(samples)
            except Exception:
                print(format_exc())
        else:
            wav_file.filepath = filepath

            wav_fmt = wav_file.data.format
            wav_fmt.channels = channels
            wav_fmt.sample_rate = sample_rate
            wav_fmt.bits_per_sample = 16
            wav_fmt.byte_rate = ((wav_fmt.sample_rate *
                                  wav_fmt.bits_per_sample *
                                  wav_fmt.channels) // 8)

            samples_len = len(samples)
            if "adpcm" in encoding and decode_adpcm:
                samples = decode_adpcm_samples(samples, channels)

                wav_fmt.fmt.set_to('pcm')
                wav_fmt.block_align = 2 * wav_fmt.channels
                samples_len = len(samples) * 2  # UInt16 array, not bytes
            elif encoding == "none":
                wav_fmt.fmt.set_to('pcm')
                wav_fmt.block_align = 2 * wav_fmt.channels
            else:
                wav_fmt.fmt.set_to('ima_adpcm')
                wav_fmt.block_align = 36 * wav_fmt.channels

            wav_file.data.wav_data.audio_data = samples
            wav_file.data.wav_data.audio_data_size = samples_len
            wav_file.data.wav_header.filesize = 36 + samples_len

            wav_file.serialize(temp=False, backup=False)


def extract_h1_sounds(meta, tag_index_ref, **kw):
    halo_map = kw['halo_map']
    overwrite = kw.get('overwrite', True)
    decode_adpcm = kw.get('decode_adpcm', True)
    tagpath_base = join(kw['out_dir'], tag_index_ref.tag.tag_path)
    pitch_ranges = meta.pitch_ranges.STEPTREE
    same_pr_names = {}

    channels = meta.encoding.data + 1
    sample_rate = 22050 * (meta.sample_rate.data + 1)

    for i in range(len(pitch_ranges)):
        pr = pitch_ranges[i]
        perms = pr.permutations.STEPTREE
        pitchpath_base = tagpath_base
        if len(pitch_ranges) > 1:
            name = pr.name if pr.name else str(i)

            same_pr_ct = same_pr_names.get(name, 0)
            same_pr_names[name] = same_pr_ct + 1
            if same_pr_ct: name += "_%s" % same_pr_ct

            pitchpath_base = join(pitchpath_base, name)

        same_names_permlists = {}
        actual_perm_count = pr.actual_permutation_count
        unchecked_perms = set(range(len(pr.permutations.STEPTREE)))

        perm_indices = range(min(actual_perm_count, len(unchecked_perms)))
        if not perm_indices:
            perm_indices = unchecked_perms

        while perm_indices:
            # loop over all of the actual permutation indices and combine
            # the permutations they point to into a list with a shared name.
            # we do this so we can combine the permutations together into one.
            for j in perm_indices:
                perm = perms[j]
                compression = perm.compression.enum_name
                name = perm.name if perm.name else str(j)
                permlist = same_names_permlists.get(name, [])
                same_names_permlists[name] = permlist

                while j in unchecked_perms:
                    perm = perms[j]
                    if compression != perm.compression.enum_name:
                        # cant combine when compression is different
                        break

                    unchecked_perms.remove(j)
                    permlist.append(perm)

                    j = perm.next_permutation_index

            perm_indices = set(unchecked_perms)

        merged_permlists = {}
        for name, permlist in same_names_permlists.items():
            merged_permlists[name] = merged_permlist = []
            merged_data = b''
            for perm in permlist:
                compression = perm.compression.enum_name
                if compression == "ogg":
                    # cant combine this shit
                    merged_permlist.append((compression, perm.samples.data))
                    continue

                merged_data += perm.samples.data

            if merged_data:
                merged_permlist.append((compression, merged_data))


        for name, permlist in merged_permlists.items():
            save_sound_perms(permlist, join(pitchpath_base, name),
                             sample_rate, channels, overwrite, decode_adpcm)


def get_sound_name(string_ids, import_names, index):
    if index < 0 or index >= len(import_names):
        return ""
    return get_string_id_string(string_ids, import_names[index])


def extract_h2_sounds(meta, tag_index_ref, **kw):
    halo_map = kw['halo_map']
    overwrite = kw.get('overwrite', True)
    decode_adpcm = kw.get('decode_adpcm', True)
    tagpath_base = join(kw['out_dir'], tag_index_ref.tag.tag_path)
    string_ids = halo_map.map_header.strings.string_id_table

    ugh__meta = halo_map.ugh__meta
    if ugh__meta is None:
        return True

    import_names = ugh__meta.import_names.STEPTREE
    pitch_ranges = ugh__meta.pitch_ranges.STEPTREE
    permutations = ugh__meta.permutations.STEPTREE
    perm_chunks  = ugh__meta.perm_chunks.STEPTREE

    same_pr_names = {}

    channels    = {0: 1,     1: 2,     2: 6    }.get(meta.encoding.data)
    sample_rate = {0: 22050, 1: 44100, 2: 32000}.get(meta.sample_rate.data)
    compression = meta.compression.enum_name

    if meta.encoding.enum_name == "codec":
        print("    CANNOT YET EXTRACT THIS FORMAT.")
        '''
        The codec format seems to be encoded with wmaudio2.

        Bytes:
            0-31
                Two nearly identical GUIDs, with the second one specifying in
                its first 2 bytes that the audio data is encoded with wmaudio2.
            32-39
                Unknown, but always seems to be 01 00 00 00  00 00 00 00
            40-43
                Number of blocks of data(same value found in the header below)
            44-55
                Unknown, but I think it always seems to be the same.
            56-87
                wav_format header struct. sig is "ZYU\x00" instead of "fmt ",
                length is 28 instead of 20, and fmt is(always?) 0x0161,
                which is the format code for wmaudio2.
                channels, sample_rate, byte_rate, block_align, and
                bits_per_sample all seem to be set properly. the value
                for block_align is the same as bytes 40-43
            88-91
                Unknown. Might be something to specify the data length?

            Everything after this appears to be audio data.
        '''
        return

    pr_index = meta.pitch_range_index
    pr_count = min(meta.pitch_range_count, len(pitch_ranges) - pr_index)
    if pr_index < 0 or pr_count < 0:
        return True

    for i in range(pr_index, pr_index + pr_count):
        pr = pitch_ranges[i]
        pitchpath_base = tagpath_base
        if pr_count > 1:
            name = get_sound_name(string_ids, import_names, pr.import_name_index)
            if not name: name = str(i)

            same_pr_ct = same_pr_names.get(name, 0)
            same_pr_names[name] = same_pr_ct + 1
            if same_pr_ct: name += "_%s" % same_pr_ct

            pitchpath_base = join(pitchpath_base, name)

        perm_index = pr.first_permutation
        perm_count = min(pr.permutation_count, len(permutations) - perm_index)
        if perm_index < 0 or perm_count < 0:
            continue

        for j in range(perm_index, perm_index + perm_count):
            perm = permutations[j]
            name = get_sound_name(string_ids, import_names, perm.import_name_index)
            if not name: name = str(j)
            permpath_base = join(pitchpath_base, name)

            chunk_index = perm.first_chunk
            chunk_count = min(perm.chunk_count, len(perm_chunks) - chunk_index)
            if chunk_index < 0 or chunk_count < 0:
                continue

            merged_data = b''
            for k in range(chunk_index, chunk_index + chunk_count):
                ptr, map_name = split_raw_pointer(perm_chunks[k].pointer)
                size = perm_chunks[k].size
                this_map = halo_map
                if map_name != "local":
                    this_map = halo_map.maps.get(map_name)

                if this_map is None:
                    continue
                elif this_map.map_data is None:
                    continue

                this_map.map_data.seek(ptr)
                merged_data += this_map.map_data.read(size)

            save_sound_perms([(compression, merged_data)], permpath_base,
                             sample_rate, channels, overwrite, decode_adpcm)


def extract_bitmaps(meta, tag_index_ref, **kw):
    halo_map = kw['halo_map']
    filepath_base = join(kw['out_dir'], tag_index_ref.tag.tag_path)
    is_padded = "xbox" in halo_map.engine
    pix_data = meta.processed_pixel_data.STEPTREE

    if is_padded:
        # cant extract xbox bitmaps yet
        return True

    arby = Arbytmap()
    tex_infos = []
    bitm_i = 0
    multi_bitmap = len(meta.bitmaps.STEPTREE) > 1
    for bitmap in meta.bitmaps.STEPTREE:
        typ = bitmap.type.enum_name
        fmt = bitmap.format.enum_name
        bpp = 1
        w = bitmap.width
        h = bitmap.height
        d = bitmap.depth
        pix_off = bitmap.pixels_offset

        filepath = filepath_base
        if multi_bitmap:
            filepath += "__%s" % bitm_i
            bitm_i += 1

        tex_block = []
        tex_info = dict(
            width=w, height=h, depth=d, mipmap_count=bitmap.mipmaps,
            sub_bitmap_count=6 if typ == "cubemap" else 1, packed=True,
            swizzled=bitmap.flags.swizzled, filepath=filepath + ".dds"
            )
        tex_infos.append(tex_info)

        if fmt in ("a8", "y8", "ay8", "p8"):
            tex_info["format"] = {"a8":  FORMAT_A8,  "y8": FORMAT_Y8,
                                  "ay8": FORMAT_AY8, "p8": FORMAT_A8}[fmt]
        elif fmt == "p8-bump":
            tex_info.update(
                palette=P8_PALETTE.p8_palette_32bit_packed*(bitmap.mipmaps+1),
                palette_packed=True, indexing_size=8, format=FORMAT_P8)
        elif fmt in ("r5g6b5", "a1r5g5b5", "a4r4g4b4",
                     "a8y8", "v8u8", "g8b8"):
            bpp = 2
            tex_info["format"] = {
                "a8y8": FORMAT_A8Y8, "v8u8": FORMAT_U8V8, "g8b8": FORMAT_U8V8,
                "r5g6b5": FORMAT_R5G6B5, "a1r5g5b5": FORMAT_A1R5G5B5,
                "a4r4g4b4": FORMAT_A4R4G4B4}[fmt]
        elif fmt in ("x8r8g8b8", "a8r8g8b8"):
            bpp = 4
            tex_info["format"] = FORMAT_A8R8G8B8
        elif fmt == "rgbfp16":
            bpp = 6
            tex_info["format"] = FORMAT_R16G16B16F
        elif fmt == "rgbfp32":
            bpp = 12
            tex_info["format"] = FORMAT_A16R16G16B16F
        elif fmt == "argbfp32":
            bpp = 16
            tex_info["format"] = FORMAT_A32R32G32B32F
        else:
            tex_info["format"] = {
                "dxt1": FORMAT_DXT1, "dxt3": FORMAT_DXT3, "dxt5": FORMAT_DXT5
                }.get(fmt, FORMAT_A8)

        tex_info["texture_type"] = {
            "texture 2d": TYPE_2D, "texture 3d": TYPE_3D,
            "cubemap":TYPE_CUBEMAP}.get(typ, TYPE_2D)

        for i in range(bitmap.mipmaps + 1):
            if "dxt" in fmt:
                w_texel = w//4
                h_texel = h//4
                if w%4: w_texel += 1
                if h%4: h_texel += 1

                mip_size = w_texel * h_texel * 8  # 8 bytes per texel
                if fmt != "dxt1": mip_size *= 2
            else:
                mip_size = w * h * bpp

            if typ == "cubemap":
                if is_padded:
                    mip_size += get_pad_size(mip_size, CUBEMAP_PADDING)
                for i in range(6):
                    tex_block.append(pix_data[pix_off: pix_off + mip_size])
                    pix_off += mip_size
            else:
                mip_size *= d
                tex_block.append(pix_data[pix_off: pix_off + mip_size])
                pix_off += mip_size

            #if fmt == "p8": mip_size += 256*4
            if w > 1: w = w//2
            if h > 1: h = h//2
            if d > 1: d = d//2

        if not tex_block:
            # nothing to extract
            continue

        arby.load_new_texture(texture_block=tex_block, texture_info=tex_info)
        arby.save_to_file()

    return False


h1_data_extractors = {
    #'mode', 'mod2', 'coll', 'phys', 'antr', 'magy', 'sbsp',
    #'font', 'hmt ', 'str#', 'ustr', 'unic',
    "bitm": extract_bitmaps, "snd!": extract_h1_sounds,
    }

h2_data_extractors = {
    #'mode', 'coll', 'phmo', 'jmad',
    #'sbsp',

    #'hmt ', 'unic',
    "bitm": extract_bitmaps, "snd!": extract_h2_sounds,
    }
