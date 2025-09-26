/* ==========================================================
   Purpose: Handles About page interactivity (pentagon + modals)
   Notes:
     - Accessible modals (focus trap, ESC, overlay click)
     - Profile modal: About, Fun Fact, Contributions, Contact
     - Send Message modal: word count + cancel
   ========================================================== */

(() => {
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function getCSRFToken() {
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }

  /* ------------------ Modal Management ------------------- */
  let activeModal = null;
  let lastFocusedEl = null;

  function getFocusable(container) {
    return $$(
      'a[href], button:not([disabled]), textarea, input, [tabindex]:not([tabindex="-1"])',
      container
    );
  }

  function trapFocus(e) {
    if (!activeModal || e.key !== "Tab") return;
    const focusables = getFocusable(activeModal);
    if (!focusables.length) return;
    const first = focusables[0];
    const last = focusables[focusables.length - 1];
    if (e.shiftKey && document.activeElement === first) {
      e.preventDefault();
      last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
      e.preventDefault();
      first.focus();
    }
  }

  function openModal(modalEl) {
    if (!modalEl) return;
    activeModal = modalEl;
    lastFocusedEl = document.activeElement;
    modalEl.classList.add("active");
    document.body.style.overflow = "hidden";
    const focusTarget = getFocusable(modalEl)[0] || modalEl;
    focusTarget.focus();
    document.addEventListener("keydown", onGlobalKeyDown);
    modalEl.addEventListener("mousedown", onOverlayClick);
    document.addEventListener("keydown", trapFocus);
  }

  function closeModal(modalEl) {
    if (!modalEl) return;
    modalEl.classList.remove("active");
    document.body.style.overflow = "";
    document.removeEventListener("keydown", onGlobalKeyDown);
    modalEl.removeEventListener("mousedown", onOverlayClick);
    document.removeEventListener("keydown", trapFocus);
    activeModal = null;
    if (lastFocusedEl) lastFocusedEl.focus();
  }

  function onGlobalKeyDown(e) {
    if (e.key === "Escape" && activeModal) closeModal(activeModal);
  }
  function onOverlayClick(e) {
    if (!activeModal) return;
    const content = activeModal.querySelector(".modal-content");
    if (!content.contains(e.target)) closeModal(activeModal);
  }

  // Global close buttons
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-close-modal]");
    if (btn) {
      const modalEl = btn.closest(".modal");
      if (modalEl) closeModal(modalEl);
    }
  });

  /* -------------------- Profiles Cache ------------------- */
  let profiles = {};
  const pentagonPositions = ["noel", "kyle", "steve", "riese", "amit"];
  const getPentagonClass = (i) => pentagonPositions[i] || "";

  /* ------------------ Render Pentagon ------------------- */
  async function loadTeam() {
    try {
      const res = await fetch("/api/team");
      const members = await res.json();
      const layout = $("#pentagon-layout");
      layout.innerHTML = "";
      members.forEach((m, i) => {
        profiles[m.id] = m;
        const card = document.createElement("article");
        card.className = `profile-pentagon ${getPentagonClass(i)}`;
        card.tabIndex = 0;
        card.setAttribute("role", "button");
        card.setAttribute(
          "aria-label",
          `Open profile: ${m.first_name} ${m.last_name}`
        );
        card.innerHTML = `
          <img src="${
            (window.STATIC_IMAGE_BASE || "") +
            (m.profile_image || "placeholder.png")
          }" 
               alt="${m.first_name} ${m.last_name}" class="profile-img">
          <div class="profile-name">${m.first_name} ${m.last_name}</div>
          <div class="profile-role">${m.role || ""}</div>
        `;
        card.addEventListener("click", () => showProfileModal(m.id));
        card.addEventListener("keydown", (e) => {
          if (e.key === "Enter" || e.key === " ") {
            e.preventDefault();
            showProfileModal(m.id);
          }
        });
        layout.appendChild(card);
      });
    } catch (err) {
      console.error("Failed to load team data", err);
      $("#pentagon-layout").textContent = "Unable to load team.";
    }
  }

  /* ---------------- Profile Modal ---------------- */
  function buildSection(title, bodyEl) {
    const sec = document.createElement("section");
    sec.className = "modal-section";
    const h3 = document.createElement("h3");
    h3.className = "section-title";
    h3.textContent = title;
    sec.append(h3, bodyEl);
    return sec;
  }

  function showProfileModal(id) {
    const p = profiles[id];
    if (!p) return;
    const container = $("#profile-modal-content");
    container.innerHTML = "";

    const closeBtn = document.createElement("button");
    closeBtn.className = "modal-close";
    closeBtn.setAttribute("data-close-modal", "");
    closeBtn.innerHTML = "&times;";
    container.appendChild(closeBtn);

    const header = document.createElement("div");
    header.className = "profile-modal-header";
    header.innerHTML = `
      <img src="${
        (window.STATIC_IMAGE_BASE || "") +
        (p.profile_image || "placeholder.png")
      }" 
           alt="${p.first_name} ${p.last_name}" class="modal-profile-img">
      <div class="modal-profile-meta">
        <h2 class="modal-profile-name" id="profileModalTitle">${p.first_name} ${
      p.last_name
    }</h2>
        <div class="modal-profile-role">${p.role || ""}</div>
      </div>`;

    const about = document.createElement("div");
    about.className = "modal-profile-bio";
    about.textContent = p.bio || "No bio provided.";
    const aboutSec = buildSection("About", about);
    aboutSec.id = "profileModalDesc";

    const factWrap = document.createElement("div");
    factWrap.textContent = p.fun_fact ? p.fun_fact : "No fun fact provided.";
    const factSec = buildSection("Fun Fact", factWrap);

    const contribWrap = document.createElement("ul");
    contribWrap.className = "contrib-list";
    if (Array.isArray(p.contributions) && p.contributions.length) {
      p.contributions.forEach((c) => {
        const li = document.createElement("li");
        li.className = "contrib-bullet";
        li.textContent = c;
        contribWrap.appendChild(li);
      });
    } else {
      contribWrap.appendChild(
        Object.assign(document.createElement("li"), {
          textContent: "No contributions yet.",
        })
      );
    }
    const contribSec = buildSection("Contributions", contribWrap);

    const contactWrap = document.createElement("div");
    contactWrap.className = "contact-links";
    if (p.linkedin_url) {
      const a = document.createElement("a");
      a.href = p.linkedin_url;
      a.textContent = "LinkedIn";
      a.className = "btn btn-link";
      a.target = "_blank";
      a.rel = "noopener";
      contactWrap.appendChild(a);
    }
    if (p.github_url) {
      const a = document.createElement("a");
      a.href = p.github_url;
      a.textContent = "GitHub";
      a.className = "btn btn-link";
      a.target = "_blank";
      a.rel = "noopener";
      contactWrap.appendChild(a);
    }
    if (p.email) {
      const a = document.createElement("a");
      a.href = `mailto:${p.email}`;
      a.textContent = "Email";
      a.className = "btn btn-link";
      contactWrap.appendChild(a);
    }
    const contactSec = buildSection("Contact", contactWrap);

    const actions = document.createElement("div");
    actions.className = "modal-actions";
    const msgBtn = document.createElement("button");
    msgBtn.className = "btn btn-primary btn-lg";
    msgBtn.textContent = "Send Message";
    msgBtn.addEventListener("click", () =>
      openMessageModal(`${p.first_name} ${p.last_name}`, p.id)
    );
    actions.appendChild(msgBtn);

    container.append(
      header,
      aboutSec,
      factSec,
      contribSec,
      contactSec,
      actions
    );
    openModal($("#profile-modal"));
  }

  /* ---------------- Message Modal ---------------- */
  const maxWords = 500;
  let wcEls = {};

  function openMessageModal(name, id) {
    $("#messageToName").textContent = `To: ${name}`;
    $("#messageMemberId").value = id;
    wcEls.form.reset();
    wcEls.status.textContent = "";
    $("#wordCount").textContent = "0";
    $("#wordLimitWarning").style.display = "none";
    wcEls.submitBtn.disabled = true;
    openModal($("#send-message-modal"));
  }

  function countWords(str) {
    return str.trim().split(/\s+/).filter(Boolean).length;
  }
  function updateWordCount() {
    const c = countWords(wcEls.textarea.value);
    wcEls.wordCount.textContent = c;
    const over = c > maxWords;
    $("#wordLimitWarning").style.display = over ? "inline" : "none";
    wcEls.submitBtn.disabled =
      over ||
      !wcEls.form.senderName.value.trim() ||
      !wcEls.form.senderEmail.value.trim() ||
      !wcEls.textarea.value.trim();
  }

  async function handleSend(e) {
    e.preventDefault();
    const c = countWords(wcEls.textarea.value);
    if (!c) {
      wcEls.status.textContent = "Please write a message.";
      return;
    }
    if (c > maxWords) {
      wcEls.status.textContent = "Too long.";
      return;
    }
    const payload = {
      senderName: wcEls.form.senderName.value,
      senderEmail: wcEls.form.senderEmail.value,
      message: wcEls.textarea.value,
      memberId: wcEls.form.memberId.value,
    };
    wcEls.status.textContent = "Sending…";
    try {
      const res = await fetch("/api/send-team-message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken(),
        },
        body: JSON.stringify(payload),
      });
      if (!res.ok) throw new Error();
      wcEls.status.textContent = "Sent ✅";
      setTimeout(() => closeModal($("#send-message-modal")), 1000);
    } catch {
      wcEls.status.textContent = "Failed to send.";
    }
  }

  document.addEventListener("DOMContentLoaded", () => {
    wcEls = {
      textarea: $("#messageTextarea"),
      wordCount: $("#wordCount"),
      warning: $("#wordLimitWarning"),
      submitBtn: $("#sendMessageBtnFinal"),
      status: $("#sendMessageStatus"),
      form: $("#sendMessageForm"),
    };
    wcEls.textarea.addEventListener("input", updateWordCount);
    wcEls.form.senderName.addEventListener("input", updateWordCount);
    wcEls.form.senderEmail.addEventListener("input", updateWordCount);
    wcEls.form.addEventListener("submit", handleSend);
    loadTeam();
  });

  window.openMessageModal = openMessageModal;
})();
