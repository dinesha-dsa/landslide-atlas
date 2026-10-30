"""Create the English synthetic-voice slide video on Windows; no API keys.

Build dependencies: Pillow and imageio-ffmpeg. Requires Windows System.Speech
with Microsoft Zira Desktop. Outputs a captioned MP4, VTT and chapter metadata.
"""
from pathlib import Path
import hashlib
import json
import subprocess
import wave
from PIL import Image, ImageDraw, ImageFont
import imageio_ffmpeg

ROOT = Path(__file__).resolve().parents[1]
MEDIA = ROOT / 'docs/media'
WORK = ROOT / '.cache/research-tour'
WORK.mkdir(parents=True, exist_ok=True)
chapters = json.loads((MEDIA / 'research-tour.json').read_text(encoding='utf-8'))
subprocess.run(['powershell.exe', '-NoProfile', '-File', str(ROOT / 'scripts/generate_tour_voice.ps1'),
                '-ChapterPath', str(MEDIA / 'research-tour.json'), '-OutputPath', str(WORK)], check=True)

INK, MUTED, TEAL = '#173637', '#617577', '#16766a'
def font(size, bold=False):
    return ImageFont.truetype('C:/Windows/Fonts/segoeuib.ttf' if bold else 'C:/Windows/Fonts/segoeui.ttf', size)

def wrap(text, draw, face, width):
    lines, line = [], ''
    for word in text.split():
        candidate = (line + ' ' + word).strip()
        if draw.textlength(candidate, font=face) > width and line:
            lines.append(line); line = word
        else:
            line = candidate
    return lines + [line]

def slide(index, chapter):
    im = Image.new('RGB', (1280, 720), '#f3f5f0')
    d = ImageDraw.Draw(im)
    d.rectangle((0, 0, 1280, 72), fill='#102e31')
    d.text((48, 21), 'LANDSLIDE ATLAS  /  RESEARCHER WALKTHROUGH', font=font(23, True), fill='white')
    d.text((48, 107), chapter['tag'].upper(), font=font(20, True), fill=TEAL)
    y = 150
    for line in wrap(chapter['title'], d, font(44, True), 1170):
        d.text((48, y), line, font=font(44, True), fill=INK); y += 56
    if index == 6:
        example = Image.open(ROOT / 'research/landslide-segmentation/example_preview.png').convert('RGB')
        example.thumbnail((1168, 345))
        im.paste(example, ((1280-example.width)//2, 245))
        d.text((48, 608), 'Landslide4Sense sample 1 | CC BY 4.0 | DOI: 10.5281/zenodo.10463239', font=font(18), fill=MUTED)
    else:
        y = max(y+35, 280)
        for bullet in chapter['bullets']:
            d.rounded_rectangle((48, y+9, 60, y+21), radius=3, fill=TEAL)
            lines = wrap(bullet, d, font(29), 1085)
            for line in lines:
                d.text((80, y), line, font=font(29), fill=INK); y += 41
            y += 22
        d.text((48, 608), 'Source-linked observations. Research preview. Read the source ledger.', font=font(19), fill=MUTED)
    d.line((48, 654, 1232, 654), fill='#ccd9d1', width=2)
    d.text((48, 673), 'English synthetic narration | Captions and transcript available', font=font(17), fill=MUTED)
    d.text((1140, 672), f'{index+1:02d} / 08', font=font(20, True), fill=TEAL)
    path = WORK / f'slide-{index:02d}.png'
    im.save(path)
    return path

def timestamp(seconds):
    millis = round(seconds*1000)
    return f'{millis//3600000:02d}:{millis//60000%60:02d}:{millis//1000%60:02d}.{millis%1000:03d}'

captions, timings, concat = ['WEBVTT\n'], [], []
cursor, sentence_index = 0.0, 0
audio_path = WORK / 'narration.wav'
with wave.open(str(audio_path), 'wb') as output:
    output.setnchannels(1); output.setsampwidth(2); output.setframerate(24000)
    for index, chapter in enumerate(chapters):
        start = cursor
        for sentence in chapter['sentences']:
            with wave.open(str(WORK / f'voice-{sentence_index:02d}.wav'), 'rb') as clip:
                assert (clip.getnchannels(), clip.getsampwidth(), clip.getframerate()) == (1, 2, 24000)
                frames = clip.readframes(clip.getnframes())
                duration = clip.getnframes()/24000
            output.writeframes(frames)
            captions += [f'{timestamp(cursor)} --> {timestamp(cursor+duration)}\n{sentence}\n']
            output.writeframes(b'\x00\x00' * 8400)
            cursor += duration + .35
            sentence_index += 1
        output.writeframes(b'\x00\x00' * 18000)
        cursor += .75
        slide_path = slide(index, chapter)
        timings.append(dict(title=chapter['title'], start=round(start, 3), end=round(cursor, 3),
                            transcript=' '.join(chapter['sentences'])))
        concat += [f"file '{slide_path.name}'", f'duration {cursor-start:.6f}']
concat += [f"file 'slide-{len(chapters)-1:02d}.png'"]
(WORK/'slides.txt').write_text('\n'.join(concat), encoding='utf-8')
(MEDIA/'research-tour.en.vtt').write_text('\n'.join(captions), encoding='utf-8')
(MEDIA/'research-tour-chapters.json').write_text(json.dumps(timings, indent=2), encoding='utf-8')
video = MEDIA / 'research-tour.mp4'
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(), '-y', '-hide_banner', '-loglevel', 'error',
    '-f', 'concat', '-safe', '0', '-i', str(WORK/'slides.txt'), '-i', str(audio_path),
    '-c:v', 'libx264', '-preset', 'medium', '-tune', 'stillimage', '-r', '5', '-pix_fmt', 'yuv420p',
    '-crf', '23', '-c:a', 'aac', '-b:a', '64k', '-movflags', '+faststart', '-t', f'{cursor:.6f}', str(video)], check=True)
Image.open(WORK/'slide-00.png').save(MEDIA/'research-tour-poster.jpg', quality=85)
(MEDIA/'research-tour-provenance.json').write_text(json.dumps(dict(
    voice='Microsoft Zira Desktop (synthetic English)', format='1280x720 H.264/AAC, 5 fps',
    duration_seconds=round(cursor, 3), chapters=len(chapters), caption_cues=sentence_index,
    video_sha256=hashlib.sha256(video.read_bytes()).hexdigest(),
    description='Narrated explanatory slides; no live screen recording or model predictions.',
    dataset_figure='Landslide4Sense sample 1, DOI 10.5281/zenodo.10463239, CC BY 4.0; RGB stretch and supplied annotation/slope.'
), indent=2), encoding='utf-8')
print('Created', video, 'duration', round(cursor, 1), 'seconds;', video.stat().st_size, 'bytes', flush=True)
