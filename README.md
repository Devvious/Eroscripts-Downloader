# EroScripts Downloader

Paste a [discuss.eroscripts.com](https://discuss.eroscripts.com) topic link and get the script and a matching video saved into one folder, ready to play.

The program reads the topic and its replies, finds the script attachments and every video link, checks which links still work, and lets you pick the video. Everything lands in your library like this:

```
Library/
  Scene Name/
    Scene Name.funscript
    Scene Name.roll.funscript   (extra axes, if any)
    Scene Name.mp4
    EroScripts - Topic Title.url  (shortcut back to the topic)
```

Players like ScriptPlayer, MultiFunPlayer and HereSphere pick up the script automatically because the names match.

## Features

- Checks every video link in the topic and hides the dead ones
- Downloads from Pixeldrain (files, lists and folders), Mega (files and folders), Google Drive (files and folders), Dropbox, MediaFire, Gofile, KrakenFiles, BuzzHeavier, Catbox, e621, PMVHaven, direct file links, and any site yt-dlp supports (PornHub, xHamster, Iwara, SpankBang, ...)
- A built-in download window for sites that want an "I am human" check or only play the video (VikingFile and similar)
- Topics with several scripts: each video shows which script it goes with, and you can change it with a right-click
- Several versions of one script (for example with and without vibration): pick the main one, which gets the folder name together with the video. The others keep their own names, and the folder gets " (+Variation)" at the end. Set your favourite version once in **Extras...** (for example "Handy 2 Pro Overclocked") and it's picked automatically
- Topic titles that start with a tag like `[Studio]` keep it in the folder name
- Shows how long each script runs, and warns when a video's length doesn't match
- "Show post text" shows what each post says about its script or video, handy when a reply links an uncut or re-encoded version
- Resumes interrupted downloads, queues several topics at once, and can watch the clipboard for topic links
- Unpacks zipped scripts and videos
- Already have the video? Point to it and it gets moved or copied into the folder

## Requirements

- Python 3.8 or newer ([python.org](https://www.python.org/downloads/) - tick "Add Python to PATH" when installing on Windows)
- An EroScripts account (script attachments are for members)

Optional extras, which the program can install for you from its **Extras...** button:

| Package | What it adds |
|---|---|
| `yt-dlp` | Downloads from tube sites |
| `pycryptodome` | Downloads from Mega |
| `pywebview` | The download window for captcha / player-only sites |
| `certifi` | Up-to-date security certificates (fixes "certificate expired" on some hosts) |

Or install them yourself:

```
pip install -r requirements.txt
```

[FFmpeg](https://ffmpeg.org/download.html) on your PATH lets yt-dlp grab the best quality from tube sites.

## Usage

Download `eroscripts_downloader.py` and double-click it, or run:

```
python eroscripts_downloader.py
```

Tip: rename it to `eroscripts_downloader.pyw` to hide the console window on Windows.

1. Press **Account...** and log in to EroScripts
2. Pick your library folder
3. Paste a topic link and press **Add**
4. Pick a video and press **Download scripts + selected video**

### Console version

```
python eroscripts_downloader.py --cli
python eroscripts_downloader.py URL [URL ...] --dest "D:\Library"
python eroscripts_downloader.py URL --dest "D:\Library" --auto
python eroscripts_downloader.py --login USERNAME
```

`--auto` takes the ticked scripts and the best online video without asking. Run with `--help` for all options.

## Your data

The program saves its settings (including your EroScripts login session) and download history next to itself, in `eroscripts_downloader_settings.json` and `eroscripts_downloader_history.jsonl`. Your password is never saved. Don't share those files.

## Works with Funscript Organizer

The library layout is the same one Funscript Organizer uses, and the downloader borrows its library folder setting if you have it.

## Disclaimer

This tool only downloads what topic posters have linked. Respect the scripters' and video creators' terms, and support them where you can.

## License

MIT - see [LICENSE](LICENSE).
