import os
import mmap
import shutil
import traceback

from reclaimer.util import *
from binilla.util import get_cwd

def inject_file_padding(file, *off_padsize_pairs, padchar=b'\xCA'):
    file.seek(0, 2)
    map_size = file.tell()
    dcbs = dstoff_cpysize_by_srcoff = dict(off_padsize_pairs)
    assert len(padchar) == 1

    off_diff = 0
    for srcoff in sorted(dcbs):
        assert dcbs[srcoff] >= 0
        off_diff += dcbs[srcoff]
        dcbs[srcoff] = [srcoff + off_diff, 0, off_diff]

    last_end = map_size
    map_size += off_diff
    for srcoff in sorted(dcbs)[::-1]:
        dcbs[srcoff][1] = last_end - srcoff
        last_end = srcoff

    close_mmap = False
    try:
        if not isinstance(file, mmap.mmap):
            file = mmap.mmap(file.fileno(), 0)
            close_mmap = True
    except Exception:
        pass

    try:
        if isinstance(file, mmap.mmap):
            file.resize(map_size)
        else:
            file.truncate(map_size)

        intra_file_move(file, dcbs)
    except Exception:
        if close_mmap:
            try: file.close()
            except Exception: pass
        raise

    return map_size


def intra_file_move(file, dstoff_cpysize_by_srcoff, padchar=b'\xCA'):
    is_mmap = isinstance(file, mmap.mmap)

    for srcoff in sorted(dstoff_cpysize_by_srcoff)[::-1]:
        # copy in chunks starting at the end of the copy section so
        # data doesnt get overwritten if  dstoff < srcoff + cpysize
        dstoff, cpysize, padsize = dstoff_cpysize_by_srcoff[srcoff][:]
        copied = padded = 0
        if not padsize or cpysize <= 0:
            continue

        if is_mmap:
            # mmap.move is much faster than our method below
            file.move(dstoff, srcoff, cpysize)
        else:
            while copied < cpysize:
                remainder = cpysize - copied
                chunksize = min(4*1024**2, remainder)  # copy of 4MB chunks

                file.seek(srcoff + remainder - chunksize)
                chunk = file.read(chunksize)
                file.seek(dstoff + remainder - chunksize)
                file.write(chunk)
                copied += chunksize

            del chunk

        file.seek(srcoff)
        if padsize >= 1024**2:
            # default to writing padding in 1MB chunks
            padding = padchar * 1024**2

        while padsize > 0:
            if padsize < 1024**2:
                padding = padchar * padsize
            file.write(padding)
            padsize -= len(padding)

    file.flush()


def sanitize_filename(name):
    # make sure to rename reserved windows filenames to a valid one
    if name in RESERVED_WINDOWS_FILENAME_MAP:
        return RESERVED_WINDOWS_FILENAME_MAP[name]
    final_name = ''
    for c in name:
        if c not in INVALID_PATH_CHARS:
            final_name += c
    if final_name == '':
        raise Exception('Bad %s char filename' % len(name))