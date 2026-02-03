#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.14"
# dependencies = [
#     "rich>=14.3.2",
# ]
# ///

import argparse
import glob
import shutil
import subprocess
import re
import statistics
import sys
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple
from rich import print

ENCODERS = {
    "jpegli": {
        "cmd": 'cjpegli --chroma_subsampling 420 -d 1.0 "{input}" "{output}"',
        "ext": ".jpg",
    },
    "libwebp": {
        "cmd": 'ffmpeg -y -i "{input}" -pix_fmt yuv420p -f rawvideo - | cwebp -s {width} {height} -m 6 -q 90 -o "{output}" -- -',
        "ext": ".webp",
    },
    "libwebp_sharpyuv": {
        "cmd": 'cwebp -m 6 -q 90 -sharp_yuv "{input}" -o "{output}"',
        "ext": ".webp",
    },
    "libwebp_default": {
        "cmd": 'cwebp -m 6 -q 90 "{input}" -o "{output}"',
        "ext": ".webp",
    },
    "svtav1": {
        "cmd": 'ffmpeg -y -i "{input}" -pix_fmt yuv420p10le -strict -2 "{temp_y4m}" && SvtAv1EncApp -i "{temp_y4m}" -b - --crf 20 --avif 1 --preset 0 --tune 3 | ffmpeg -y -i - -c:v copy "{output}"',
        "ext": ".avif",
    },
}

DECODERS = {
    "jpeg": {
        "imagemagick": {"type": "png", "cmd": 'magick "{encoded}" "{decoded}"'},
        "ffmpeg_basic": {
            "type": "png",
            "cmd": 'ffmpeg -y -i "{encoded}" -pix_fmt rgb24 -f image2 -update 1 -frames:v 1 "{decoded}"',
        },
        "djpegli": {"type": "png", "cmd": 'djpegli "{encoded}" "{decoded}"'},
        "ffmpeg_filtered": {
            "type": "png",
            "cmd": 'ffmpeg -y -i "{encoded}" -vf "scale=flags=lanczos+accurate_rnd+full_chroma_int:param0=5,format=rgb24" -f image2 -update 1 -frames:v 1 "{decoded}"',
        },
    },
    "webp": {
        "dwebp": {"type": "png", "cmd": 'dwebp "{encoded}" -o "{decoded}"'},
        "dwebp_nofancy": {
            "type": "png",
            "cmd": 'dwebp -nofancy "{encoded}" -o "{decoded}"',
        },
        "ffmpeg_basic": {
            "type": "png",
            "cmd": 'ffmpeg -y -i "{encoded}" -f image2 -update 1 -frames:v 1 "{decoded}"',
        },
        "ffmpeg_filtered": {
            "type": "png",
            "cmd": 'ffmpeg -y -i "{encoded}" -vf "scale=flags=lanczos+accurate_rnd+full_chroma_int:param0=5,format=rgb24" -f image2 -update 1 -frames:v 1 "{decoded}"',
        },
    },
    "avif": {
        "avifdec": {"type": "png", "cmd": 'avifdec -d 8 "{encoded}" "{decoded}"'},
        "ffmpeg_basic": {
            "type": "png",
            "cmd": 'ffmpeg -y -i "{encoded}" -f image2 -update 1 -frames:v 1 "{decoded}"',
        },
        "ffmpeg_filtered": {
            "type": "png",
            "cmd": 'ffmpeg -y -i "{encoded}" -vf "scale=flags=lanczos+accurate_rnd+full_chroma_int:param0=5,format=rgb24" -f image2 -update 1 -frames:v 1 "{decoded}"',
        },
    },
}

METRICS = {
    "fssimu2": {
        "cmd": 'fssimu2 "{ref}" "{decoded}"',
        "parser": lambda out: float(out.strip().split()[0]),
        "lower_is_better": False,
    },
    "butteraugli": {
        "cmd": 'butteraugli_main "{ref}" "{decoded}" --pnorm 3 --intensity_target 203',
        "parser": lambda out: float(out.strip().split()[0]),
        "lower_is_better": True,
    },
    "fcvvdp": {
        "cmd": 'fcvvdp "{ref}" "{decoded}"',
        "parser": lambda out: float(out.strip().split()[0]),
        "lower_is_better": False,
    },
}


def get_image_dimensions(path: Path) -> Tuple[int, int]:
    """
    Get image dimensions using ImageMagick
    """
    cmd = ["magick", "identify", "-format", "%wx%h", str(path)]
    try:
        result = subprocess.run(
            cmd, capture_output=True, text=True, check=True, timeout=10
        )
        w, h = result.stdout.strip().split("x")
        return int(w), int(h)
    except subprocess.TimeoutExpired:
        raise RuntimeError(f"Timeout getting dimensions for {path}")
    except Exception as e:
        raise RuntimeError(f"Failed to get dimensions for {path}: {e}")


def check_required_tools() -> None:
    """
    Verify all required external tools are available
    """
    tools: list[str] = [
        "magick",
        "cjpegli",
        "djpegli",
        "cwebp",
        "dwebp",
        "ffmpeg",
        "SvtAv1EncApp",
        "avifdec",
        "fssimu2",
        "butteraugli_main",
        "fcvvdp",
    ]

    missing = [tool for tool in tools if not shutil.which(tool)]
    if missing:
        print(
            f"Error: Required tools not found in PATH: {', '.join(missing)}",
            file=sys.stderr,
        )
        sys.exit(1)


def run_command(cmd: str) -> str:
    """
    Run a shell command & return the output.
    """
    result = subprocess.run(cmd, capture_output=True, text=True, shell=True)
    if result.returncode != 0:
        raise subprocess.CalledProcessError(
            result.returncode, cmd, result.stderr or result.stdout
        )
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()
    if stdout:
        return stdout
    if stderr:
        return stderr
    return ""


def get_butteraugli(src_pth: str, dst_pth: str) -> float:
    """
    Compute Butteraugli score with `butteraugli_main`.
    """
    butter_outp: str = run_command(
        f'butteraugli_main "{src_pth}" "{dst_pth}" --pnorm 3 --intensity_target 203',
    )
    butter_lines = butter_outp.strip().splitlines()
    return float(butter_lines[1].split(":")[1].strip())


def get_fcvvdp(src_pth: str, dst_pth: str) -> float:
    """
    Compute CVVDP JOD score using `fcvvdp`.
    """
    cmd = f'fcvvdp "{src_pth}" "{dst_pth}"'
    process = subprocess.Popen(
        cmd, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
    )
    stdout, stderr = process.communicate()
    if process.returncode != 0:
        raise subprocess.CalledProcessError(process.returncode, cmd, stderr)
    m = re.search(r"JOD:\s*([\d\.]+)", stderr)
    return float(m.group(1))


def encode_image(
    input_path: Path,
    output_path: Path,
    encoder: str,
    width: int,
    height: int,
) -> bool:
    """
    Encode an image using the specified encoder
    """
    template = ENCODERS[encoder]["cmd"]
    temp_y4m_path = None
    if "{temp_y4m}" in template:
        tf = tempfile.NamedTemporaryFile(suffix=".y4m", dir="/tmp", delete=False)
        temp_y4m_path = Path(tf.name)
        tf.close()

    cmd = template.format(
        input=str(input_path),
        output=str(output_path),
        width=width,
        height=height,
        temp_y4m=str(temp_y4m_path) if temp_y4m_path else "",
    )

    try:
        run_command(cmd)
        return True
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return False
    finally:
        if temp_y4m_path:
            try:
                if temp_y4m_path.exists():
                    temp_y4m_path.unlink()
            except Exception:
                pass


def process_image(
    input_path: Path,
    encoder: str,
    decoders: List[str],
    metrics: List[str],
    format_name: str,
    tmpdir: Path,
) -> Dict[str, Dict[str, float | None]]:
    """
    Process a single image through encoding and all decoder/metric combinations
    """
    results: Dict[str, Dict[str, float | None]] = {
        decoder: {metric: None for metric in metrics} for decoder in decoders
    }

    try:
        width, height = get_image_dimensions(input_path)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return results

    try:
        tf = tempfile.NamedTemporaryFile(
            suffix=ENCODERS[encoder]["ext"], dir=str(tmpdir), delete=False
        )
        encoded_path = Path(tf.name)
        tf.close()
    except Exception:
        encoded_path = tmpdir / f"{input_path.stem}{ENCODERS[encoder]['ext']}"

    if not encode_image(input_path, encoded_path, encoder, width, height):
        try:
            if encoded_path.exists():
                encoded_path.unlink()
        except Exception:
            pass
        return results

    for decoder_name in decoders:
        decoder = DECODERS[format_name][decoder_name]
        print(f"[bold]Decoder:\t{decoder_name}[/bold]")

        try:
            tf_dec = tempfile.NamedTemporaryFile(
                suffix=".png",
                prefix=f"{input_path.stem}_{decoder_name}_",
                dir=str(tmpdir),
                delete=False,
            )
            decoded_path = Path(tf_dec.name)
            tf_dec.close()
        except Exception:
            decoded_path = tmpdir / f"{input_path.stem}_{decoder_name}.png"

        cmd = str(decoder["cmd"]).format(
            encoded=str(encoded_path), decoded=str(decoded_path)
        )
        try:
            run_command(cmd)
        except Exception as e:
            print(f"Error: {e}", file=sys.stderr)
            try:
                if decoded_path.exists():
                    decoded_path.unlink()
            except Exception:
                pass
            continue

        for metric_name in metrics:
            try:
                if metric_name == "butteraugli":
                    score = get_butteraugli(str(input_path), str(decoded_path))
                    results[decoder_name][metric_name] = score
                    print(f"{metric_name}:\t{score:.6f}")
                    continue

                if metric_name == "fcvvdp":
                    score = get_fcvvdp(str(input_path), str(decoded_path))
                    results[decoder_name][metric_name] = score
                    print(f"{metric_name}:\t\t{score:.6f}")
                    continue

                template = METRICS.get(metric_name, {}).get("cmd")
                if not isinstance(template, str):
                    raise RuntimeError(f"No command template for metric {metric_name}")

                metric_cmd = template.format(
                    ref=str(input_path), decoded=str(decoded_path)
                )
                output = run_command(metric_cmd)

                parser = METRICS.get(metric_name, {}).get("parser")
                if not callable(parser):
                    raise RuntimeError(f"No parser available for metric {metric_name}")

                score = float(parser(output))
                results[decoder_name][metric_name] = score
                print(f"{metric_name}:\t{score:.6f}")
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)

        try:
            if decoded_path.exists():
                decoded_path.unlink()
        except Exception:
            pass

    try:
        if encoded_path.exists():
            encoded_path.unlink()
    except Exception:
        pass

    return results


def print_summary(
    scores: Dict[str, Dict[str, List[float]]], metrics: List[str], num_images: int
) -> None:
    """
    Print statistics & identify best decoders.
    """
    print("\nSummary")

    for metric in metrics:
        print(f"\n{metric}:")

        decoder_scores = {}
        for decoder in scores:
            scores_list = scores[decoder].get(metric, [])
            if scores_list:
                decoder_scores[decoder] = scores_list

        if not decoder_scores:
            print("  No data available")
            continue

        decoder_avgs = {
            dec: statistics.mean(lst) for dec, lst in decoder_scores.items()
        }

        lower_is_better = METRICS.get(metric, {}).get("lower_is_better", False)
        sorted_decoders = sorted(
            decoder_avgs.items(), key=lambda x: x[1], reverse=not lower_is_better
        )

        best_str: str = "[green] <-- best[/green]"

        if num_images > 1:
            header = f"[bold]{'Decoder':25s} {'avg':>12s} {'hmean':>12s} {'max':>12s} {'min':>12s} {'stddev':>12s}[/bold]"
            print(header)
            print("-" * 90)

            for i, (decoder, avg) in enumerate(sorted_decoders):
                lst = decoder_scores[decoder]
                avg_val = avg

                max_v = max(lst)
                min_v = min(lst)

                if len(lst) > 1:
                    try:
                        hmean = statistics.harmonic_mean(lst)
                        hmean_str = f"{hmean:12.6f}"
                    except Exception:
                        hmean_str = f"{'N/A':>12s}"

                    try:
                        stdev = statistics.stdev(lst)
                        stdev_str = f"{stdev:12.6f}"
                    except Exception:
                        stdev_str = f"{'N/A':>12s}"
                else:
                    hmean_str = f"{'N/A':>12s}"
                    stdev_str = f"{'N/A':>12s}"

                marker: str = best_str if i == 0 else ""
                print(
                    f"{decoder:25s} {avg_val:12.6f} {hmean_str} {max_v:12.6f} {min_v:12.6f} {stdev_str}{marker}"
                )
        else:
            for i, (decoder, avg) in enumerate(sorted_decoders):
                marker: str = best_str if i == 0 else ""
                print(f"  {decoder:25s} {avg:.6f}{marker}")

    header = f"\n{'Decoder':<25} "
    for metric in metrics:
        header += f"{metric:<15}"
    print(header)
    print("-" * 64)

    for decoder in sorted(scores.keys()):
        row = f"{decoder:<25} "
        for metric in metrics:
            scores_list = scores[decoder].get(metric, [])
            if scores_list:
                avg = statistics.mean(scores_list)
                row += f"{avg:<15.6f}"
            else:
                row += f"{'N/A':<15}"
        print(row)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Batch evaluate image encoding/decoding quality across multiple metrics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "encoder",
        choices=["jpegli", "libwebp", "libwebp_sharpyuv", "libwebp_default", "svtav1"],
        help="Encoder to use for compression",
    )
    parser.add_argument(
        "input_images", nargs="+", help="Input image files (supports glob patterns)"
    )
    parser.add_argument(
        "--decoders",
        nargs="*",
        help="Specific decoders to test (default: all for format)",
    )
    parser.add_argument(
        "--metrics",
        nargs="*",
        choices=list(METRICS.keys()),
        help="Specific metrics to use (default: all)",
    )
    args = parser.parse_args()

    check_required_tools()

    format_map = {
        "jpegli": "jpeg",
        "libwebp": "webp",
        "libwebp_sharpyuv": "webp",
        "libwebp_default": "webp",
        "svtav1": "avif",
    }
    format_name = format_map[args.encoder]

    available_decoders = list(DECODERS[format_name].keys())
    decoders_to_test = args.decoders or available_decoders

    for d in decoders_to_test:
        if d not in available_decoders:
            print(
                f"Error: Decoder '{d}' not available for {format_name} format",
                file=sys.stderr,
            )
            sys.exit(1)

    metric_names = args.metrics or list(METRICS.keys())

    scores: Dict[str, Dict[str, List[float]]] = {
        decoder: {metric: [] for metric in metric_names} for decoder in decoders_to_test
    }

    image_list = []
    for pattern in args.input_images:
        path = Path(pattern)
        if path.exists():
            image_list.append(path)
        else:
            matches = [Path(p) for p in glob.glob(pattern)]
            image_list.extend(matches)

    if not image_list:
        print("Error: No input images found", file=sys.stderr)
        sys.exit(1)

    image_list = sorted(set(image_list))

    tmpdir = Path("/tmp")

    for input_path in image_list:
        print(f"\nProcessing: {input_path.name} ({len(image_list)} images total)")

        image_results = process_image(
            input_path,
            args.encoder,
            decoders_to_test,
            metric_names,
            format_name,
            tmpdir,
        )

        for decoder in image_results:
            for metric in image_results[decoder]:
                val = image_results[decoder][metric]
                if val is not None:
                    scores[decoder][metric].append(val)

    print_summary(scores, metric_names, len(image_list))


if __name__ == "__main__":
    main()
