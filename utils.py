import math
import time
from xml.etree import ElementTree
from html import unescape

import math
import time

def float_to_srt_time_format(d: float) -> str:
    """
    Converts a floating-point number to a string in SRT time format.

    Args:
        d (float): The floating-point number to convert.

    Returns:
        str: The converted string in SRT time format.

    Example:
        >>> float_to_srt_time_format(123.456)
        '00:02:03,456'
    """
    fraction, whole = math.modf(d)
    time_fmt = time.strftime("%H:%M:%S,", time.gmtime(whole))
    ms = f"{fraction:.3f}".replace("0.", "")
    return time_fmt + ms

def xml_caption_to_srt(xml_captions: str) -> str:
    """
    Converts XML captions to SRT format.

    Args:
        xml_captions (str): The XML captions to be converted.

    Returns:
        str: The captions in SRT format.
    """
    segments = []
    root = ElementTree.fromstring(xml_captions)
    i=0
    for child in list(root.iter("body"))[0]:
        if child.tag == 'p':
            caption = ''
            if len(list(child))==0:
                caption = child.text
            for s in list(child):
                if s.tag == 's':
                    caption += ' ' + s.text
            caption = unescape(caption.replace("\n", " ").replace("  ", " "),)
            try:
                duration = float(child.attrib["d"])/10000.0
            except KeyError:
                duration = 0.0
            start = float(child.attrib["t"])/1000.0
            end = start + duration
            sequence_number = i + 1
            line = "{seq}\n{start} --> {end}\n{text}\n".format(
                seq=sequence_number,
                start=float_to_srt_time_format(start),
                end=float_to_srt_time_format(end),
                text=caption,
            )
            segments.append(line)
            i += 1
    return "\n".join(segments).strip()