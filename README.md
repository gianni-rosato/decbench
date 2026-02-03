# decbench

Batch-evaluate image encoding + decoding quality across multiple decoders and objective metrics, with a focus on handling 4:2:0 chroma subsampling.

- Input: one or more image files (supports glob patterns)
- Action: encodes each image with the chosen encoder, decodes with one or more decoders, evaluates with one or more metrics
- Output: per-image metric values and a final summary table (avg/hmean/max/min/stddev, with the "best" decoder highlighted)

## Dependencies

- [uv](https://docs.astral.sh/uv/)
- avifdec
- butteraugli_main
- cjpegli/djpegli
- cwebp/dwebp
- [fcvvdp](https://github.com/halidecx/fcvvdp)
- ffmpeg
- [fssimu2](https://github.com/gianni-rosato/fssimu2)
- magick
- SvtAv1EncApp

Just `chmod a+x ./dec.py` followed by `./dec.py --help` to use. If one of these external tools is not in the `PATH`, the script will give you an error.

## Usage

```sh
% ./dec.py --help
usage: dec.py [-h] [--decoders [DECODERS ...]] [--metrics [{fssimu2,butteraugli,fcvvdp} ...]] {jpegli,libwebp,libwebp_sharpyuv,libwebp_default,svtav1} input_images [input_images ...]

Batch evaluate image encoding/decoding quality across multiple metrics

positional arguments:
  {jpegli,libwebp,libwebp_sharpyuv,libwebp_default,svtav1}
                        Encoder to use for compression
  input_images          Input image files (supports glob patterns)

options:
  -h, --help            show this help message and exit
  --decoders [DECODERS ...]
                        Specific decoders to test (default: all for format)
  --metrics [{fssimu2,butteraugli,fcvvdp} ...]
                        Specific metrics to use (default: all)
```

## Output

- Per-image lines showing decoder + metric scores as they're computed
- Final `Summary` section with per-decoder statistics (avg / harmonic mean / max / min / stddev) and a table of average metric values. The script marks the best decoder
- The script uses temporary files under `/tmp` (it attempts to clean them up)

## Credits

This project is under the [Apache 2.0 License](LICENSE). Sample numbers on the [gb82 image set](https://github.com/gianni-rosato/gb82-image-set) are provided in [this document](results.md).
