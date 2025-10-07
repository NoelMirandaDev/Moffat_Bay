(() => {
  const $ = (s, r=document) => r.querySelector(s);
  const $$ = (s, r=document) => Array.from(r.querySelectorAll(s));

  function getCSRF(){
    const el = document.querySelector('meta[name="csrf-token"]');
    return el ? el.getAttribute("content") : "";
  }

  /* Modal infra for send message (same endpoint already in your routes) */
  let active=null, last=null;
  function focusables(c){ return $$('a[href],button:not([disabled]),textarea,input,[tabindex]:not([tabindex="-1"])',c); }
  function trap(e){ if(!active||e.key!=="Tab") return; const f=focusables(active); if(!f.length) return; const first=f[0], lastF=f[f.length-1]; if(e.shiftKey&&document.activeElement===first){ e.preventDefault(); lastF.focus(); } else if(!e.shiftKey&&document.activeElement===lastF){ e.preventDefault(); first.focus(); } }
  function onKey(e){ if(e.key==="Escape"&&active) closeModal(active); }
  function onOverlay(e){ const box=active.querySelector(".modal-content"); if(!box.contains(e.target)) closeModal(active); }
  function openModal(m){ active=m; last=document.activeElement; m.classList.add("active"); document.body.style.overflow="hidden"; (focusables(m)[0]||m).focus(); document.addEventListener("keydown",onKey); document.addEventListener("keydown",trap); m.addEventListener("mousedown",onOverlay); }
  function closeModal(m){ m.classList.remove("active"); document.body.style.overflow=""; document.removeEventListener("keydown",onKey); document.removeEventListener("keydown",trap); m.removeEventListener("mousedown",onOverlay); active=null; if(last) last.focus(); }
  document.addEventListener("click",e=>{ const b=e.target.closest("[data-close-modal]"); if(b){ const m=b.closest(".modal"); if(m) closeModal(m); } });

  const maxWords=500; let els={};
  function words(s){ return s.trim().split(/\s+/).filter(Boolean).length; }

  function openMessageModal(name,id){
    $("#messageToName").textContent = `To: ${name}`;
    $("#messageMemberId").value = id;
    els.form.reset();
    els.status.textContent = "";
    $("#wordCount").textContent = "0";
    $("#wordLimitWarning").style.display = "none";
    els.submitBtn.disabled = true;
    openModal($("#send-message-modal"));
  }
  window.openMessageModal = openMessageModal;

  function update(){
    const c=words(els.textarea.value);
    els.wordCount.textContent=c;
    const over=c>maxWords;
    $("#wordLimitWarning").style.display = over ? "inline" : "none";
    els.submitBtn.disabled = over ||
      !els.form.senderName.value.trim() ||
      !els.form.senderEmail.value.trim() ||
      !els.textarea.value.trim();
  }

  async function send(e){
    e.preventDefault();
    const c=words(els.textarea.value);
    if(!c){ els.status.textContent="Please write a message."; return; }
    if(c>maxWords){ els.status.textContent="Too long."; return; }
    const payload={
      senderName: els.form.senderName.value,
      senderEmail: els.form.senderEmail.value,
      message: els.textarea.value,
      memberId: els.form.memberId.value
    };
    els.status.textContent="Sending…";
    try{
      const r=await fetch("/api/send-team-message", {
        method:"POST",
        headers:{ "Content-Type":"application/json", "X-CSRFToken":getCSRF() },
        body:JSON.stringify(payload)
      });
      if(!r.ok) throw new Error();
      els.status.textContent="Sent ✅";
      setTimeout(()=>{ const m=$("#send-message-modal"); if(m) m.classList.remove("active"); }, 900);
    }catch{
      els.status.textContent="Failed to send.";
    }
  }

  document.addEventListener("DOMContentLoaded", ()=>{
    els = {
      form: $("#sendMessageForm"),
      textarea: $("#messageTextarea"),
      wordCount: $("#wordCount"),
      submitBtn: $("#sendMessageBtnFinal"),
      status: $("#sendMessageStatus")
    };
    if(!els.form) return;
    els.textarea.addEventListener("input", update);
    els.form.senderName.addEventListener("input", update);
    els.form.senderEmail.addEventListener("input", update);
    els.form.addEventListener("submit", send);
  });
})();
