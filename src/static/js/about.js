/* ==========================================================
   
   - Profile modal with tabs: Story / Contributions / Contact
   - Message modal with:
       • live email validation
       • 500-word limit
       • Cancel confirmation pop-card
       • After-send persistent success + Cancel→Close
   - Esc + overlay close; focus trap inside modals
   ========================================================== */
(() => {
  const $  = (s, r = document) => r.querySelector(s);
  const $$ = (s, r = document) => Array.from(r.querySelectorAll(s));

  const WORD_LIMIT = 500;
  const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

  function csrf() {
    return document.querySelector('meta[name="csrf-token"]')?.content || "";
  }

  /* ---------- Narrative copy (front-end only) ---------- */
  const STORY = {
    1: "Noel didn’t set out to collect degrees—he followed curiosity. Sociology taught him how people work; Criminal Justice showed him how systems hold up (or don’t). Software became the bridge between the two: code that serves people. On this project he gravitates to the hard, invisible parts—security, sessions, data flow—so the visible parts feel simple. When he’s not shipping features, you’ll probably find him plotting the next trail with his fiancé, trading screen light for dappled greens.",
    2: "Kyle grew up where the internet felt like a magic rope—one that reached beyond miles of quiet fields. That rope turned into a lifelong fascination with how things look, feel, and work. He collects little details the way others collect vinyl: button states, motion curves, color balance. If a moment on the site feels smooth or just “right,” there’s a good chance Kyle sanded the edges until your hand wouldn’t catch.",
    3: "Steve’s story starts with data—then keeps going. From analyst programmer to senior DBA, she’s been the person who makes sure the heart beats steady while everyone else is dancing. At Moffat Bay she carries that same calm precision into the app’s backbone and the little touches users notice: pages that load cleanly, flows that explain themselves, and an About page that feels like people, not profiles.",
    4: "Riese likes untangling knots. Throw a twisty bug or a half-baked idea on the table, and they’ll quietly start reshaping it until it’s clean, clear, and useful. That patience shows up across the project: registration flows that don’t fight users, pages that do what they promise, and details that click into place without calling attention to themselves.",
    5: "Amit changed lanes on purpose: from logistics to the logic of the browser. He brings a practical eye to the front end—layouts that read well, patterns you understand at a glance, and choices that travel nicely from phone to desktop. Out on the road he’ll take the long way for the view; in the code, he prefers the simple route that gets every traveler where they meant to go."
  };
  const CONTRIB = {
    1: "Noel set the rails. He stood up the project, wired the database, and made security a habit—not a hope. Logins feel instant because the plumbing is tight; reservations feel safe because the rules are consistent. He broke big tasks into small wins, kept the board honest, and made sure reviews felt like progress, not roadblocks.",
    2: "Kyle gave the site its voice. He built a living style guide, the modern login modal that keeps you on the page, and a layer of shared scripts that make little interactions feel alive. He tested designs with real flows and trimmed the parts that didn’t earn their keep.",
    3: "Steve drew the map and built the road. The ERD, the TDD, the attraction experiences, the functional tests—then the deployment to PythonAnywhere so real people could kick the tires. She listened hard to feedback, then tightened every seam that needed it. This About page layout? That’s her hand, too.",
    4: "Riese turned ideas into working doors. Registration that holds up, a reservation summary you can trust, and test runs that catch frayed edges before they fray users. Quiet momentum, durable results.",
    5: "Amit partnered across registration and reservation, keeping the interface clear and the path steady. He shaped the feel of the site—what goes where, what reads first, and how to move forward without thinking too hard."
  };
  const CONTRIB_BY_NAME = {
    Noel: CONTRIB[1],
    Kyle: CONTRIB[2],
    Steve: CONTRIB[3],
    Riese: CONTRIB[4],
    Amit: CONTRIB[5],
  };

  /* ---------- Modal infra (focus trap + Esc/overlay close) ---------- */
  let activeModal = null, lastFocus = null;
  const PROFILE_SCOPE = "#profile-modal";
  const MESSAGE_SCOPE = "#send-message-modal";

  function focusables(c){
    return $$('a[href],button:not([disabled]),textarea,input,[tabindex]:not([tabindex="-1"])', c);
  }
  function trap(e){
    if(!activeModal || e.key!=="Tab") return;
    const f = focusables(activeModal);
    if(!f.length) return;
    const a=f[0], z=f[f.length-1];
    if(e.shiftKey && document.activeElement===a){ e.preventDefault(); z.focus(); }
    else if(!e.shiftKey && document.activeElement===z){ e.preventDefault(); a.focus(); }
  }
  function onEsc(e){ if(e.key==="Escape" && activeModal) closeModal(activeModal); }
  function onOverlay(e){
    if(!activeModal) return;
    const box = activeModal.querySelector(".modal-content");
    if(box && !box.contains(e.target)) closeModal(activeModal);
  }
  function openModal(m){
    activeModal = m; lastFocus = document.activeElement;
    m.classList.add("active"); document.body.style.overflow="hidden";
    (focusables(m)[0]||m).focus();
    document.addEventListener("keydown", onEsc);
    document.addEventListener("keydown", trap);
    m.addEventListener("mousedown", onOverlay);
  }
  function closeModal(m){
    m.classList.remove("active"); document.body.style.overflow="";
    document.removeEventListener("keydown", onEsc);
    document.removeEventListener("keydown", trap);
    m.removeEventListener("mousedown", onOverlay);
    activeModal=null; if(lastFocus) lastFocus.focus();
  }

  // Support data-close-modal (used by profile modal X only)
  document.addEventListener("click", (e)=>{
    const btn = e.target.closest("[data-close-modal]");
    if(!btn) return;
    const modalEl = btn.closest(`${PROFILE_SCOPE}, ${MESSAGE_SCOPE}`);
    if(modalEl) closeModal(modalEl);
  });

  /* ---------- Data cache ---------- */
  const profiles = {};

  /* ---------- Build the layout (Noel left + 2×2 right) ---------- */
  async function loadTeam(){
    try{
      const res = await fetch("/api/team");
      if(!res.ok) throw new Error("Failed to load team");
      const members = await res.json();

      const root = $("#team-layout");
      if(!root) return;
      root.innerHTML = "";

      // LEFT: Noel
      const left = document.createElement("div");
      left.className = "team-left";
      const noel = members.find(m => m.first_name === "Noel");
      if(noel){
        profiles[noel.id] = noel;
        const fig = document.createElement("figure");
        fig.className = "team-lead";
        fig.innerHTML = `
          <img class="avatar-large" alt="${noel.first_name} ${noel.last_name}"
               src="${(window.STATIC_IMAGE_BASE||"") + (noel.profile_image || "placeholder.png")}">
          <figcaption>
            <div class="name">${noel.first_name} ${noel.last_name}</div>
            <a class="bio-link" href="#" data-member-id="${noel.id}">Read Bio →</a>
          </figcaption>`;
        fig.addEventListener("click",(e)=>{
          if(e.target.closest(".bio-link")) return;
          e.preventDefault(); showProfileModal(noel.id);
        });
        left.appendChild(fig);
      }

      // RIGHT: 2×2 grid
      const right = document.createElement("div");
      right.className = "team-right";
      const grid = document.createElement("div");
      grid.className = "right-grid";
      right.appendChild(grid);

      ["Kyle","Riese","Amit","Steve"].forEach(name=>{
        const m = members.find(x => x.first_name === name);
        if(!m) return;
        profiles[m.id] = m;

        const card = document.createElement("figure");
        card.className = "member";
        card.innerHTML = `
          <img class="avatar" alt="${m.first_name} ${m.last_name}"
               src="${(window.STATIC_IMAGE_BASE||"") + (m.profile_image || "placeholder.png")}">
          <figcaption class="member-info">
            <div class="name">${m.first_name} ${m.last_name}</div>
            <a class="bio-link" href="#" data-member-id="${m.id}">Read Bio →</a>
          </figcaption>`;
        card.addEventListener("click",(e)=>{
          if(e.target.closest(".bio-link")) return;
          e.preventDefault(); showProfileModal(m.id);
        });
        grid.appendChild(card);
      });

      root.append(left, right);

      // “Read Bio →” (delegated)
      root.addEventListener("click",(e)=>{
        const a = e.target.closest(".bio-link[data-member-id]");
        if(!a) return;
        e.preventDefault();
        const id = Number(a.getAttribute("data-member-id"));
        if(id) showProfileModal(id);
      });

    }catch(err){
      console.error(err);
      const root = $("#team-layout"); if(root) root.textContent = "Unable to load team.";
    }
  }

  /* ---------- Tabs helpers ---------- */
  function buildTabs(){
    const bar = document.createElement("div");
    bar.className = "tabbar";
    bar.innerHTML = `
      <button type="button" class="tab is-active" data-tab="story">Story</button>
      <button type="button" class="tab" data-tab="contrib">Contributions</button>
      <button type="button" class="tab" data-tab="contact">Contact</button>`;
    return bar;
  }
  function switchTab(container, name){
    $$(".tab", container).forEach(t => t.classList.toggle("is-active", t.dataset.tab===name));
    $$(".tab-panel", container).forEach(p => p.hidden = (p.dataset.panel!==name));
  }
  function section(title, el){
    const s = document.createElement("section");
    s.className = "modal-section";
    if (title) {
      const h = document.createElement("h3"); h.className="section-title"; h.textContent=title;
      s.append(h, el);
    } else {
      s.append(el);
    }
    return s;
  }

  /* ---------- Profile modal ---------- */
  function showProfileModal(id){
    const p = profiles[id]; if(!p) return;
    const box = $("#profile-modal-content"); if(!box) return;
    box.innerHTML = "";

    const closeBtn = document.createElement("button");
    closeBtn.className = "modal-close"; closeBtn.setAttribute("data-close-modal","");
    closeBtn.innerHTML = "&times;";
    box.appendChild(closeBtn);

    const header = document.createElement("div");
    header.className = "profile-modal-header";
    header.innerHTML = `
      <img class="modal-profile-img"
           alt="${p.first_name} ${p.last_name}"
           src="${(window.STATIC_IMAGE_BASE||"") + (p.profile_image || "placeholder.png")}">
      <div class="modal-profile-meta">
        <h2 class="modal-profile-name" id="profileModalTitle">${p.first_name} ${p.last_name}</h2>
        <div class="modal-profile-role">${p.role || ""}</div>
      </div>`;
    box.appendChild(header);

    const tabs = buildTabs(); box.appendChild(tabs);

    // Story
    const storyPanel = document.createElement("div");
    storyPanel.className = "tab-panel"; storyPanel.dataset.panel = "story";
    const story = document.createElement("div"); story.className="modal-profile-bio";
    story.textContent = STORY[id] || STORY_BY_NAME(p.first_name) || p.bio || "No story available.";
    const ff = document.createElement("div");
    if(p.fun_fact){ ff.textContent = p.fun_fact; }
    storyPanel.append( section("Story", story), p.fun_fact ? section("A little extra", ff) : document.createDocumentFragment() );

    // Contributions (robust fallback)
    const contribPanel = document.createElement("div");
    contribPanel.className = "tab-panel"; contribPanel.dataset.panel = "contrib";
    let text = CONTRIB[id] || CONTRIB_BY_NAME[p.first_name];
    if (!text) {
      if (Array.isArray(p.contributions) && p.contributions.length) {
        text = `Here’s how ${p.first_name} contributed:\n` + p.contributions.map(c=>`• ${c}`).join("\n");
      } else {
        text = `${p.first_name}’s contributions are being added shortly.`;
      }
    }
    const contrib = document.createElement("div"); contrib.className="modal-profile-bio"; contrib.textContent = text;
    contribPanel.append( section("Contributions", contrib) );

    // Contact (three equal pill buttons)
    const contactPanel = document.createElement("div");
    contactPanel.className = "tab-panel"; contactPanel.dataset.panel = "contact";

    const btnRow = document.createElement("div");
    btnRow.className = "contact-actions";

    // Leave Message
    const msgBtn = document.createElement("button");
    msgBtn.type = "button";
    msgBtn.className = "btn";
    msgBtn.textContent = "Leave Message";
    msgBtn.addEventListener("click", () => openMessageModal(`${p.first_name} ${p.last_name}`, p.id));

    // Send Email
    const emailBtn = document.createElement("a");
    emailBtn.className = "btn";
    if (p.email) {
      emailBtn.href = `mailto:${p.email}`;
      emailBtn.textContent = "Send Email";
      emailBtn.target = "_blank"; emailBtn.rel = "noopener";
    } else {
      emailBtn.href = "javascript:void(0)";
      emailBtn.textContent = "Send Email";
      emailBtn.setAttribute("aria-disabled","true");
      emailBtn.classList.add("is-disabled");
      emailBtn.title = "This team member doesn’t have an email listed.";
    }

    // GitHub Contact
    const ghBtn = document.createElement("a");
    ghBtn.className = "btn";
    if (p.github_url) {
      ghBtn.href = p.github_url;
      ghBtn.textContent = "GitHub Contact";
      ghBtn.target = "_blank"; ghBtn.rel = "noopener";
    } else {
      ghBtn.href = "javascript:void(0)";
      ghBtn.textContent = "GitHub Contact";
      ghBtn.setAttribute("aria-disabled","true");
      ghBtn.classList.add("is-disabled");
      ghBtn.title = "This team member doesn’t have a GitHub link.";
    }

    btnRow.append(msgBtn, emailBtn, ghBtn);
    contactPanel.append( section("", btnRow) );

    box.append(storyPanel, contribPanel, contactPanel);
    switchTab(box, "story");

    tabs.addEventListener("click", (e)=>{
      const b = e.target.closest(".tab"); if(!b) return;
      switchTab(box, b.dataset.tab);
    });

    openModal($("#profile-modal"));
  }

  function STORY_BY_NAME(name){
    const map = { Noel: STORY[1], Kyle: STORY[2], Steve: STORY[3], Riese: STORY[4], Amit: STORY[5] };
    return map[name];
  }

  /* ---------- Message modal (validation, word limit, cancel confirm) ---------- */
  let wc = {};
  function wordCount(s){ return s.trim().split(/\s+/).filter(Boolean).length; }

  function openMessageModal(name,id){
    $("#messageToName").textContent = `To: ${name}`;
    $("#messageMemberId").value = id;

    if(wc.form){
      wc.form.reset(); wc.status.textContent = "";
      $("#wordCount").textContent = "0"; $("#wordLimitWarning").style.display="none";
      $("#emailError").textContent = "";
      wc.submitBtn.disabled = true;

      // restore Cancel label & behavior
      const cancel = $("#cancelBtn");
      if (cancel) { cancel.textContent = "Cancel"; cancel.onclick = null; }
      const pop = $("#cancelConfirm"); if (pop) pop.hidden = true;
    }
    openModal($("#send-message-modal"));
  }

  function onChange(){
    const email = wc.form.senderEmail.value.trim();
    const hasEmail = EMAIL_RE.test(email);
    $("#emailError").textContent = hasEmail || !email ? "" : "Please enter a valid email address.";

    const c = wordCount(wc.textarea.value);
    wc.wordCount.textContent = c;
    const over = c > WORD_LIMIT;
    $("#wordLimitWarning").style.display = over ? "inline" : "none";

    wc.submitBtn.disabled = over ||
      !wc.form.senderName.value.trim() ||
      !hasEmail ||
      !wc.textarea.value.trim();
  }

  async function onSubmit(e){
    e.preventDefault();

    const email = wc.form.senderEmail.value.trim();
    if(!EMAIL_RE.test(email)){
      $("#emailError").textContent = "Please enter a valid email address.";
      return;
    }
    const c = wordCount(wc.textarea.value);
    if(!c){ wc.status.textContent="Please write a message."; return; }
    if(c>WORD_LIMIT){ wc.status.textContent="Too long."; return; }

    wc.status.textContent="Sending…";
    try{
      const r = await fetch("/api/send-team-message", {
        method:"POST",
        headers:{ "Content-Type":"application/json", "X-CSRFToken": csrf() },
        body: JSON.stringify({
          senderName: wc.form.senderName.value,
          senderEmail: email,
          message: wc.textarea.value,
          memberId: wc.form.memberId.value
        })
      });
      if(!r.ok) throw new Error();

      // Success UI persists; Cancel → Close
      setAfterSendUI(wc.form.senderName.value || 'Friend');
    }catch{
      wc.status.textContent = "Failed to send. Please try again.";
    }
  }

  function setAfterSendUI(name){
    const status = $("#sendMessageStatus");
    if (status) {
      status.innerHTML = `Thanks, <strong>${name}</strong>! Your message was sent. The team member will contact you soon.`;
    }
    const cancel = $("#cancelBtn");
    if (cancel) {
      cancel.textContent = 'Close';
      cancel.onclick = () => {
        const msgModal = $("#send-message-modal");
        if (msgModal) closeModal(msgModal);
      };
    }
    wc.submitBtn.disabled = true;
  }

  // Cancel confirmation pop-card behavior
  function showCancelConfirm(){ const pop = $("#cancelConfirm"); if(pop) pop.hidden = false; }
  function hideCancelConfirm(){ const pop = $("#cancelConfirm"); if(pop) pop.hidden = true; }
  function hasTypedAnything(){
    return (
      (wc.form?.senderName?.value?.trim() || '') !== '' ||
      (wc.form?.senderEmail?.value?.trim() || '') !== '' ||
      (wc.textarea?.value?.trim() || '') !== ''
    );
  }

  /* ---------- Boot ---------- */
  document.addEventListener("DOMContentLoaded", ()=>{
    // Cache message form controls (IDs preserved)
    wc = {
      form: $("#sendMessageForm"),
      textarea: $("#messageTextarea"),
      wordCount: $("#wordCount"),
      submitBtn: $("#sendMessageBtnFinal"),
      status: $("#sendMessageStatus")
    };
    if(wc.form && wc.textarea && wc.submitBtn){
      wc.textarea.addEventListener("input", onChange);
      wc.form.senderName.addEventListener("input", onChange);
      wc.form.senderEmail.addEventListener("input", onChange);
      wc.form.addEventListener("submit", onSubmit);

      // Cancel button: confirm if they typed something (no data-close-modal here)
      const cancelBtn = $('#cancelBtn');
      cancelBtn?.addEventListener('click', (e) => {
        if (hasTypedAnything()) {
          e.preventDefault();
          showCancelConfirm();
        } else {
          const msgModal = $("#send-message-modal");
          if (msgModal) closeModal(msgModal);
        }
      });
      // Confirm pop actions
      $("#confirmDiscardYes")?.addEventListener("click", ()=>{
        hideCancelConfirm();
        const msgModal = $("#send-message-modal");
        if (msgModal) closeModal(msgModal);
      });
      $("#confirmDiscardNo")?.addEventListener("click", ()=>{
        hideCancelConfirm();
        wc.textarea?.focus();
      });
    }
    loadTeam();
  });

  // expose for debugging
  window.showProfileModal = showProfileModal;
  window.openMessageModal = openMessageModal;
})();
