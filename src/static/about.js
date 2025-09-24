/* ==========================================================
   File: about.js
   Purpose: Handles About page interactivity (pentagon + modals)
   Author: Steve Stylin
   ========================================================== */

// CSRF helper
function getCSRFToken() {
  return document.querySelector('meta[name="csrf-token"]').getAttribute('content');
}

// Pentagon position mapping
const pentagonPositions = ['noel', 'kyle', 'steve', 'riese', 'amit'];
function getPentagonClass(idx) { return pentagonPositions[idx] || ''; }

// Profiles cache
let profiles = {};

// Fetch team members dynamically
fetch('/api/team')
  .then(res => res.json())
  .then(members => {
    const layout = document.getElementById('pentagon-layout');
    layout.innerHTML = '';
    members.forEach((member, idx) => {
      profiles[member.id] = member;
      const card = document.createElement('article');
      card.className = `profile-pentagon ${getPentagonClass(idx)}`;
      card.tabIndex = 0;
      card.setAttribute('role', 'button');
      card.onclick = () => showModal(member.id);
      card.innerHTML = `
        <img src="{{ url_for('static', filename='images/') }}${member.profile_image}" 
             alt="${member.first_name} ${member.last_name}" 
             class="profile-img">
        <div class="profile-name">${member.first_name} ${member.last_name}</div>
        <div class="profile-role">${member.role}</div>
      `;
      layout.appendChild(card);
    });
  })
  .catch(err => console.error("Failed to load team data", err));

// Show profile modal
function showModal(memberId) {
  const profile = profiles[memberId];
  if (!profile) return;
  const content = document.getElementById('modal-content');
  const imgUrl = "{{ url_for('static', filename='images/') }}" + profile.profile_image;
  content.innerHTML = `
    <button class="modal-close" onclick="closeModal()" aria-label="Close">&times;</button>
    <img src="${imgUrl}" alt="${profile.first_name} ${profile.last_name}" class="modal-profile-img">
    <div class="modal-profile-name">${profile.first_name} ${profile.last_name}</div>
    <div class="modal-profile-role">${profile.role}</div>
    <div class="modal-profile-bio">${profile.bio}</div>
  `;
  document.getElementById('profile-modal').classList.add('active');
  document.body.style.overflow = 'hidden';
}
function closeModal() {
  document.getElementById('profile-modal').classList.remove('active');
  document.body.style.overflow = '';
}

// Message modal
function openMessageModal(memberName, memberId) {
  document.getElementById('send-message-modal').classList.add('active');
  document.getElementById('messageToName').textContent = 'To: ' + memberName;
  document.getElementById('messageMemberId').value = memberId;
}
function closeMessageModal() {
  document.getElementById('send-message-modal').classList.remove('active');
  document.body.style.overflow = '';
}

// Word count tracking
const textarea = document.getElementById('messageTextarea');
const wordCount = document.getElementById('wordCount');
const warning = document.getElementById('wordLimitWarning');
const maxWords = 500;
if (textarea) {
  textarea.addEventListener('input', () => {
    const count = textarea.value.trim().split(/\s+/).filter(Boolean).length;
    wordCount.textContent = count;
    warning.style.display = count > maxWords ? 'inline' : 'none';
  });
}

// Send message with CSRF
const form = document.getElementById('sendMessageForm');
if (form) {
  form.addEventListener('submit', async e => {
    e.preventDefault();
    const data = {
      senderName: form.senderName.value,
      senderEmail: form.senderEmail.value,
      message: form.message.value,
      memberId: form.memberId.value
    };
    const res = await fetch('/api/send-team-message', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCSRFToken()
      },
      body: JSON.stringify(data)
    });
    document.getElementById('sendMessageStatus').textContent =
      res.ok ? 'Message sent successfully!' : 'Failed to send message.';
  });
}
