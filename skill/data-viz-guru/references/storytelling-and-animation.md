# Storytelling and animation

## The story shape

A data story is a short argument with a beginning, a turn and an end. For a client it should fit one screen or thirty seconds.

1. **Setup** (the question or the starting point): "£100 invested in January 2014."
2. **Tension** (what happened): the fall, the divergence, the surprise.
3. **Resolution** (what it means for the client): the takeaway, in the title's words, and a next step if appropriate.

Choose **one** message per visual. If you have three messages, make three visuals. A sequence of charts, each building on the last, is a better story than one crowded chart.

### Techniques that work

- **Reveal**: build the chart over time so the reader meets the data in the order it happened.
- **Focus**: grey everything but the one series the sentence is about; bring others in on later beats.
- **Compare then explain**: show the two options first, then add the annotation that says why they differ.
- **Zoom**: from the whole decade to the six weeks that matter.
- **Personalise**: put the reader in the chart ("your £10,000"). Use only with real client numbers and care.

### Things that damage trust

- A title that says more than the chart shows.
- Picking a start date to get a dramatic ending. State why the period was chosen.
- Cropping the y-axis so that small moves look large.
- Animating a forecast so it looks like history.
- Leaving out the bad stretch.

## Animation

**When to animate**: the order of events carries the message (a growth path, a crash and recovery, a lead changing hands). **When not to**: a snapshot comparison, anything with many series, or anything the audience needs to study; use a still.

### Pacing

| Beat | Duration | Why |
|---|---|---|
| Lead-in on the empty frame | 0.5–1 s | Let the title be read before motion starts |
| Draw the lines | 6–10 s for ten years | Fast enough to hold attention, slow enough to follow |
| Pause at each annotation | ~1 s | The reader needs time to read the callout |
| Hold the finished chart | 2–3 s (GIF: loops after this) | The conclusion is the takeaway; do not cut it off |

Ease in and out (the toolkit does); keep the axes fixed so nothing rescales mid-animation; no more than 3 annotation beats; text on screen for at least 2 seconds per ~7 words.

### Formats

- **MP4 (H.264)**: the default for video, decks and LinkedIn. Small and sharp. Use `yuv420p`, `+faststart` (the toolkit does).
- **GIF**: for email, chat and places that will not play video. Keep to ≤ 960 px wide, ≤ ~12 fps, ≤ 10 s; expect 10× the size of the MP4. Check the file size before sending; Outlook and many email clients choke over a few MB.
- **Silent by default**: most social video is watched muted, so the title and annotations must carry the message without audio. Add captions or on-screen text for any narration.
- **Accessibility**: a GIF or video needs a text equivalent (the alt text or a short transcript stating the finding and the key numbers), and nothing should flash faster than three times a second.

### Making a video story

1. Write the script first, one sentence per beat; the sentences are the title, annotations and (if any) voice-over.
2. Build the final frame as a static chart and lint it; the animation ends on that exact frame.
3. `animate.reveal(fig, seconds=…, hold=…)` then `animate.save_animation(anim, "story.mp4")`.
4. For a longer piece, make one reveal per beat and join them with `ffmpeg` (concat), with a title card and a closing card that carries the disclosure text for the full duration of the last frame.
5. Voice-over: about 150 words per minute; the number the narrator says should be on screen at that moment.
6. Vertical (9:16) for Reels/Shorts: use `video_vertical`, shorten the title, keep the plot out of the bottom 20% where platform controls sit.

### Compliance for moving pictures

A video or GIF is a financial promotion in its own right. The past-performance statement and source must be on screen for the **whole** of the final frame (the toolkit places them in the footer from frame one), and a clear "not advice / capital at risk" statement belongs on the closing card. See `disclosure-and-compliance.md`.
