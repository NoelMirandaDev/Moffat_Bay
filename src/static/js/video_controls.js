// Purpose: Synchronized quote timing + audio control

document.addEventListener("DOMContentLoaded", () => {
  const container = document.querySelector(".video-hero");
  const video = container?.querySelector("video");
  if (!container || !video) return;

  // ---------- Mute / Unmute ----------
  const muteBtn = document.createElement("button");
  muteBtn.className = "mb-mute-btn";

  const syncBtn = () => {
    muteBtn.setAttribute("aria-label", video.muted ? "Unmute video" : "Mute video");
    muteBtn.textContent = video.muted ? "🔇" : "🔊";
  };
  syncBtn();

  muteBtn.addEventListener("click", () => {
    video.muted = !video.muted;
    syncBtn();
  });

  video.addEventListener("volumechange", syncBtn);
  container.appendChild(muteBtn);

  // ---------- Quotes (last quote removed, no quotation marks) ----------
  const QUOTES = [
    { text: "Adventure begins where the road ends.", start: 5,  duration: 12 },
    { text: "Let the sea set you free.",             start: 17, duration: 9  },
    { text: "Find peace where forest meets tide.",   start: 26, duration: 6  },
    { text: "Moments of stillness make the best memories.", start: 32, duration: 6 }
  ];

  // Overlay
  const overlay = document.createElement("div");
  overlay.className = "mb-quote";
  const overlayText = document.createElement("div");
  overlayText.className = "mb-quote__text";
  overlay.appendChild(overlayText);
  container.appendChild(overlay);

  // ---------- Quote Logic ----------
  let activeQuote = null;
  let duration = 46; // fallback until metadata loads

  video.addEventListener("loadedmetadata", () => {
    if (Number.isFinite(video.duration) && video.duration > 0) {
      duration = video.duration;
    }
  });

  video.addEventListener("timeupdate", () => {
    const t = video.currentTime;

    // No quotes during final 5s (last image)
    if (t >= duration - 5) {
      overlay.classList.remove("mb-quote--show", "flash", "last");
      return;
    }

    // Which quote is active now?
    const current = QUOTES.find(q => t >= q.start && t < q.start + q.duration);

    if (current && current !== activeQuote) {
      activeQuote = current;
      overlayText.textContent = current.text;

      // force-restart the flash animation so it’s visible every time
      overlay.classList.remove("flash");
      // reflow to restart animation reliably
      void overlay.offsetWidth;
      overlay.classList.add("mb-quote--show", "flash");

      // if you ever bring back a unique last-quote style, toggle `.last` here
      overlay.classList.remove("last");
    }

    if (!current && activeQuote) {
      overlay.classList.remove("mb-quote--show", "flash", "last");
      activeQuote = null;
    }
  });

  video.addEventListener("ended", () => {
    overlay.classList.remove("mb-quote--show", "flash", "last");
    activeQuote = null;
  });
});
