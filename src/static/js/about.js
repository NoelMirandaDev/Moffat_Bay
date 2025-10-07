/* ==========================================================
   File: about.js
   Purpose: Team layout (Noel left + 2x2 grid right) + two-page
            narrative bios, with 500-word message limit.
   Safe with site login modal (scoped listeners).
   ========================================================== */
(() => {
  const $  = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

  function getCSRFToken(){
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }

  /* ---------------- Narrative text (front-end only) ---------------- */
  // DB ids typically: 1=Noel, 2=Kyle, 3=Steve, 4=Riese, 5=Amit
  const STORY_OVERRIDES = {
    1: `Noel didn’t set out to collect degrees—he followed curiosity. Sociology taught him how people work; Criminal Justice showed him how systems hold up (or don’t). Software became the bridge between the two: code that serves people. On this project he gravitates to the hard, invisible parts—security, sessions, data flow—so the visible parts feel simple. When he’s not shipping features, you’ll probably find him plotting the next trail with his fiancé, trading screen light for dappled greens.`,
    2: `Kyle grew up where the internet felt like a magic rope—one that reached beyond miles of quiet fields. That rope turned into a lifelong fascination with how things look, feel, and work. He collects little details the way others collect vinyl: button states, motion curves, color balance. If a moment on the site feels smooth or just “right,” there’s a good chance Kyle sanded the edges until your hand wouldn’t catch.`,
    3: `Steve’s story starts with data—then keeps going. From analyst programmer to senior DBA, she’s been the person who makes sure the heart beats steady while everyone else is dancing. At Moffat Bay she carries that same calm precision into the app’s backbone and the little touches users notice: pages that load cleanly, flows that explain themselves, and an About page that feels like people, not profiles.`,
    4: `Riese likes untangling knots. Throw a twisty bug or a half-baked idea on the table, and they’ll quietly start reshaping it until it’s clean, clear, and useful. That patience shows up across the project: registration flows that don’t fight users, pages that do what they promise, and details that click into place without calling attention to themselves.`,
    5: `Amit changed lanes on purpose: from logistics to the logic of the browser. He brings a practical eye to the front end—layouts that read well, patterns you understand at a glance, and choices that travel nicely from phone to desktop. Out on the road he’ll take the long way for the view; in the code, he prefers the simple route that gets every traveler where they meant to go.`
  };

  const CONTRIB_NARRATIVE = {
    1: `Noel set the rails. He stood up the project, wired the database, and made security a habit—not a hope. Logins feel instant because the plumbing is tight; reservations feel safe because the rules are consistent. He broke big tasks into small wins, kept the board honest, and made sure reviews felt like progress, not roadblocks.`,
    2: `Kyle gave the site its voice. He built a living style guide, the modern login modal that keeps you on the page, and a layer of shared scripts that make little interactions feel alive. He tested designs with real flows and trimmed the parts that didn’t earn their keep.`,
    3: `Steve drew the map and built the road. The ERD, the TDD, the attraction experiences, the functional tests—then the deployment to PythonAnywhere so real people could kick the tires. She listened hard to feedback, then tightened every seam that needed it. This About page layout? That’s her hand, too.`,
    4: `Riese turned ideas into working doors. Registration that holds up, a reservation summary you can trust, and test runs that catch frayed edges before they fray users. Quiet momentum, durable results.`,
    5: `Amit partnered across registration and reservation, keeping the interface clear and the path steady. He shaped the feel of the site—what goes where, what reads first, and how to move forward without thinking too hard.`
  };

  /* ---------------- Modal infra (SCOPED; login modal untouched) ---- */
  let activeModal=null, lastFocus=null;
  const MODAL_SCOPE = "#profile-modal, #send-message-modal";

  function focusables(c){
    return $$('a[href],button:not([disabled]),textarea,input,[tabindex]:not([tabindex="-1"])', c);
  }
  function trap(e){
    if(!activeModal || e.key !== "Tab") return;
    const f = focusables(activeModal); if(!f.length) return;
    const a=f[0], z=f[f.length-1];
    if(e.shiftKey && document.activeElement===a){ e.preventDefault(); z.focus(); }
    else if(!e.shiftKey && document.activeElement===z){ e.preventDefault(); a.focus(); }
  }
  function onEsc(e){ if(e.key==="Escape" && activeModal) closeModal(activeModal); }
  function onOverlay(e){
    if(!activeModal) return;
    const box = activeModal.querySelector(".modal-content");
    if (!box.contains(e.target)) closeModal(activeModal);
  }

  function openModal(m){
    activeModal = m;
    lastFocus = document.activeElement;
    m.classList.add("active");
    document.body.style.overflow = "hidden";
    (focusables(m)[0] || m).focus();
    document.addEventListener("keydown", onEsc);
    document.addEventListener("keydown", trap);
    m.addEventListener("mousedown", onOverlay);
  }
  function closeModal(m){
    m.classList.remove("active");
    document.body.style.overflow = "";
    document.removeEventListener("keydown", onEsc);
    document.removeEventListener("keydown", trap);
    m.removeEventListener("mousedown", onOverlay);
    activeModal = null;
    if (lastFocus) lastFocus.focus();
  }

  // Close buttons — ONLY for About-page modals
  document.addEventListener("click", (e) => {
    const btn = e.target.closest("[data-close-modal]");
    if (!btn) return;
    const modalEl = btn.closest(MODAL_SCOPE);
    if (modalEl) closeModal(modalEl);
  });

  /* ---------------- Data cache ---------------- */
  let profiles = {};

  /* ---------------- Render (Noel left + 2×2 grid right) ----------------- */
  async function loadTeam(){
    try{
      const res = await fetch("/api/team");
      if (!res.ok) throw new Error("Bad response");
      const members = await res.json();

      const layout = $("#team-layout");
      if(!layout) return;
      layout.innerHTML = "";

      // LEFT: Noel
      const left = document.createElement("div");
      left.className = "team-left";

      const noel = members.find(m => m.first_name === "Noel");
      if (noel){
        profiles[noel.id] = noel;
        const lead = document.createElement("figure");
        lead.className = "team-lead";
        lead.innerHTML = `
          <img src="${(window.STATIC_IMAGE_BASE||"") + (noel.profile_image||"placeholder.png")}"
               alt="${noel.first_name} ${noel.last_name}" class="avatar-large">
          <figcaption>
            <div class="name">${noel.first_name} ${noel.last_name}</div>
            <a class="bio-link" href="#" data-member-id="${noel.id}">Read Bio →</a>
          </figcaption>`;

        // Whole figure opens bio (link still works)
        lead.addEventListener("click", (e)=>{
          if (e.target.closest(".bio-link")) return;
          e.preventDefault();
          showProfileModal(noel.id);
        });

        left.appendChild(lead);
      }

      // RIGHT: 2×2 grid (Kyle, Riese, Amit, Steve)
      const right = document.createElement("div");
      right.className = "team-right";
      const grid  = document.createElement("div");
      grid.className = "right-grid";
      right.appendChild(grid);

      ["Kyle","Riese","Amit","Steve"].forEach(name=>{
        const m = members.find(mm => mm.first_name === name);
        if (!m) return;
        profiles[m.id] = m;

        const card = document.createElement("figure");
        card.className = "member";
        card.innerHTML = `
          <img src="${(window.STATIC_IMAGE_BASE||"") + (m.profile_image||"placeholder.png")}"
               alt="${m.first_name} ${m.last_name}" class="avatar">
          <figcaption class="member-info">
            <div class="name">${m.first_name} ${m.last_name}</div>
            <a class="bio-link" href="#" data-member-id="${m.id}">Read Bio →</a>
          </figcaption>`;

        // Whole card opens the bio (link still works)
        card.addEventListener("click", (e)=>{
          if (e.target.closest(".bio-link")) return;
          e.preventDefault();
          showProfileModal(m.id);
        });

        grid.appendChild(card);
      });

      // Append the two columns (no divider)
      layout.append(left, right);

      // Delegated handler for “Read Bio →”
      layout.addEventListener("click", (e)=>{
        const link = e.target.closest(".bio-link[data-member-id]");
        if (!link) return;
        e.preventDefault();
        const id = Number(link.getAttribute("data-member-id"));
        if (id) showProfileModal(id);
      });

    }catch(err){
      console.error("Failed to load team", err);
      const l = $("#team-layout"); if (l) l.textContent = "Unable to load team.";
    }
  }

  /* ---------------- Tabs helpers for the two-page modal ------------------ */
  function buildTabs(){
    const bar = document.createElement("div");
    bar.className = "tabbar";
    bar.innerHTML = `
      <button type="button" class="tab is-active" data-tab="story">Story</button>
      <button type="button" class="tab" data-tab="contrib">Contributions</button>
    `;
    return bar;
  }
  function switchTab(container, tabName){
    const tabs = $$(".tab", container);
    tabs.forEach(t => t.classList.toggle("is-active", t.dataset.tab === tabName));
    const panels = $$(".tab-panel", container);
    panels.forEach(p => p.hidden = (p.dataset.panel !== tabName));
  }
  function section(title, bodyEl){
    const s = document.createElement("section");
    s.className = "modal-section";
    const h = document.createElement("h3");
    h.className = "section-title";
    h.textContent = title;
    s.append(h, bodyEl);
    return s;
  }

  /* ---------------- Profile modal (two pages: Story / Contributions) ----- */
  function showProfileModal(id){
    const p = profiles[id]; if (!p) return;
    const box = $("#profile-modal-content"); if (!box) return;
    box.innerHTML = "";

    // Close button
    const closeBtn = document.createElement("button");
    closeBtn.className = "modal-close";
    closeBtn.setAttribute("data-close-modal","");
    closeBtn.innerHTML = "&times;";
    box.appendChild(closeBtn);

    // Header
    const header = document.createElement("div");
    header.className = "profile-modal-header";
    header.innerHTML = `
      <img src="${(window.STATIC_IMAGE_BASE||"") + (p.profile_image||"placeholder.png")}"
           alt="${p.first_name} ${p.last_name}" class="modal-profile-img">
      <div class="modal-profile-meta">
        <h2 class="modal-profile-name" id="profileModalTitle">${p.first_name} ${p.last_name}</h2>
        <div class="modal-profile-role">${p.role || ""}</div>
      </div>`;
    box.appendChild(header);

    // Tabs
    const tabs = buildTabs();
    box.appendChild(tabs);

    // Page 1: Story
    const storyPanel = document.createElement("div");
    storyPanel.className = "tab-panel";
    storyPanel.dataset.panel = "story";

    const storyText = STORY_OVERRIDES[id] || p.bio || "No story available.";
    const storyEl = document.createElement("div");
    storyEl.className = "modal-profile-bio";
    storyEl.textContent = storyText;

    const fun = document.createElement("div");
    fun.textContent = p.fun_fact ? p.fun_fact : "";
    const funSec = p.fun_fact ? section("A little extra", fun) : document.createDocumentFragment();

    storyPanel.append(section("Story", storyEl), funSec);

    // Page 2: Contributions + Contact + Message
    const contribPanel = document.createElement("div");
    contribPanel.className = "tab-panel";
    contribPanel.dataset.panel = "contrib";

    let contribStory = CONTRIB_NARRATIVE[id];
    if(!contribStory){
      if (Array.isArray(p.contributions) && p.contributions.length){
        contribStory = `Here’s how ${p.first_name} contributed:\n` + p.contributions.map(c => `• ${c}`).join("\n");
      } else {
        contribStory = "No recorded contributions yet.";
      }
    }
    const cn = document.createElement("div");
    cn.className = "modal-profile-bio";
    cn.textContent = contribStory;

    const contact = document.createElement("div");
    contact.className = "contact-links";
    if (p.linkedin_url){
      const a = document.createElement("a");
      a.href = p.linkedin_url; a.textContent = "LinkedIn";
      a.className = "btn btn-link"; a.target="_blank"; a.rel="noopener";
      contact.appendChild(a);
    }
    if (p.github_url){
      const a = document.createElement("a");
      a.href = p.github_url; a.textContent = "GitHub";
      a.className = "btn btn-link"; a.target="_blank"; a.rel="noopener";
      contact.appendChild(a);
    }
    if (p.email){
      const a = document.createElement("a");
      a.href = `mailto:${p.email}`; a.textContent = "Email";
      a.className = "btn btn-link";
      contact.appendChild(a);
    }

    const actions = document.createElement("div");
    actions.className = "modal-actions";
    const msg = document.createElement("button");
    msg.className = "btn btn-primary btn-lg";
    msg.textContent = "Send Message";
    msg.addEventListener("click", () => openMessageModal(`${p.first_name} ${p.last_name}`, p.id));
    actions.appendChild(msg);

    contribPanel.append(section("Contributions", cn), section("Contact", contact), actions);

    // Mount both pages, default to Story
    box.append(storyPanel, contribPanel);
    switchTab(box, "story");

    tabs.addEventListener("click", (e)=>{
      const btn = e.target.closest(".tab");
      if (!btn) return;
      switchTab(box, btn.dataset.tab);
    });

    // Open modal
    const modalEl = $("#profile-modal");
    if (modalEl) openModal(modalEl);
  }

  /* ---------------- Message modal (500-word limit) ---------------- */
  const WORD_LIMIT = 500;
  let wc = {};

  function openMessageModal(name, id){
    $("#messageToName").textContent = `To: ${name}`;
    $("#messageMemberId").value = id;

    if (wc.form) {
      wc.form.reset();
      wc.status.textContent = "";
      $("#wordCount").textContent = "0";
      const warn = $("#wordLimitWarning"); if (warn) warn.style.display = "none";
      wc.submitBtn.disabled = true;
    }
    const m = $("#send-message-modal");
    if (m) openModal(m);
  }

  function countWords(s){ return s.trim().split(/\s+/).filter(Boolean).length; }

  function onWordCountChange(){
    const c = countWords(wc.textarea.value);
    wc.wordCount.textContent = c;
    const over = c > WORD_LIMIT;
    const warn = $("#wordLimitWarning");
    if (warn) warn.style.display = over ? "inline" : "none";

    wc.submitBtn.disabled =
      over ||
      !wc.form.senderName.value.trim() ||
      !wc.form.senderEmail.value.trim() ||
      !wc.textarea.value.trim();
  }

  async function onSend(e){
    e.preventDefault();
    const c = countWords(wc.textarea.value);
    if (!c){ wc.status.textContent = "Please write a message."; return; }
    if (c > WORD_LIMIT){ wc.status.textContent = "Too long."; return; }

    wc.status.textContent = "Sending…";
    try{
      const r = await fetch("/api/send-team-message", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCSRFToken()
        },
        body: JSON.stringify({
          senderName: wc.form.senderName.value,
          senderEmail: wc.form.senderEmail.value,
          message: wc.textarea.value,
          memberId: wc.form.memberId.value
        })
      });
      if (!r.ok) throw new Error();
      wc.status.textContent = "Message Sent ✅";
      setTimeout(()=>{ const m=$("#send-message-modal"); if(m) closeModal(m); }, 900);
    }catch{
      wc.status.textContent = "Failed to send.";
    }
  }

  /* ---------------- Boot ---------------- */
  document.addEventListener("DOMContentLoaded", () => {
    // Cache message form controls (same IDs as the original)
    wc = {
      form: $("#sendMessageForm"),
      textarea: $("#messageTextarea"),
      wordCount: $("#wordCount"),
      submitBtn: $("#sendMessageBtnFinal"),
      status: $("#sendMessageStatus")
    };

    if (wc.form && wc.textarea && wc.submitBtn){
      wc.textarea.addEventListener("input", onWordCountChange);
      wc.form.senderName.addEventListener("input", onWordCountChange);
      wc.form.senderEmail.addEventListener("input", onWordCountChange);
      wc.form.addEventListener("submit", onSend);
    }

    loadTeam();
  });

  // expose if needed
  window.openMessageModal = openMessageModal;
  window.showProfileModal = showProfileModal;
})();
