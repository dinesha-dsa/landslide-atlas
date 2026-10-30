const video = document.getElementById('research-tour-video');
const panel = document.getElementById('research-tour-panel');
const status = document.getElementById('tour-status');
const buttons = [...document.querySelectorAll('[data-tour-start]')];
if (video && panel) {
  let chapterMedia, chapterRequest = 0;
  // A small local Blob also supports seeking on preview servers without byte ranges.
  function loadChapterMedia() {
    if (!chapterMedia) chapterMedia = (async () => {
      const response = await fetch(video.querySelector('source').src);
      if (!response.ok) throw new Error('Video download failed');
      const url = URL.createObjectURL(await response.blob());
      await new Promise((resolve, reject) => {
        const cleanup = () => { video.removeEventListener('loadeddata', loaded); video.removeEventListener('error', failed); };
        const loaded = () => { cleanup(); resolve(); };
        const failed = () => { cleanup(); URL.revokeObjectURL(url); reject(new Error('Video could not be decoded')); };
        video.addEventListener('loadeddata', loaded);
        video.addEventListener('error', failed);
        video.src = url;
        video.load();
      });
    })().catch(error => { chapterMedia = null; throw error; });
    return chapterMedia;
  }
  for (const button of buttons) button.addEventListener('click', async () => {
    const start = Number(button.dataset.tourStart);
    const request = ++chapterRequest;
    status.textContent = 'Loading the selected chapter…';
    try {
      await loadChapterMedia();
      if (request !== chapterRequest || !panel.open) return;
      video.currentTime = start;
      await video.play();
      status.textContent = 'Playing the selected chapter. Use the video controls to pause or change captions, volume and speed.';
    } catch {
      status.textContent = 'Press Play in the video controls, or download the video to watch it locally.';
    }
  });
  video.addEventListener('timeupdate', () => {
    const active = buttons.findLast(button => video.currentTime >= Number(button.dataset.tourStart));
    for (const button of buttons) {
      if (button === active) button.setAttribute('aria-current', 'true');
      else button.removeAttribute('aria-current');
    }
  });
  panel.addEventListener('toggle', () => { if (!panel.open) video.pause(); });
  video.addEventListener('pause', () => { status.textContent = 'Paused. Press Play or choose a chapter to continue.'; });
  video.addEventListener('ended', () => { status.textContent = 'Walkthrough complete. Choose a chapter to revisit a topic.'; });
  video.addEventListener('error', () => {
    status.textContent = 'The video could not load. Use the download link or read the full transcript below.';
  });
}
