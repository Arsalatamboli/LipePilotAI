// LifePilot AI Assistant Asynchronous AJAX Stream Script

document.addEventListener('DOMContentLoaded', () => {
  const chatForm = document.getElementById('chat-form');
  const chatInput = document.getElementById('chat-input');
  const chatBody = document.getElementById('chat-body');

  if (!chatForm || !chatInput || !chatBody) return;

  chatForm.addEventListener('submit', async (e) => {
    e.preventDefault();

    const userMessage = chatInput.value.trim();
    if (!userMessage) return;

    // 1. Append User Bubble
    appendUserBubble(userMessage);
    chatInput.value = '';

    // Scroll to bottom
    chatBody.scrollTop = chatBody.scrollHeight;

    // 2. Append Loading Indicator
    const loadingId = appendLoadingIndicator();

    try {
      // 3. Post to AI API Endpoint
      const response = await fetch('/ai-assistant/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ message: userMessage })
      });

      const data = await response.json();
      removeElement(loadingId);

      if (data.status === 'success') {
        appendAssistantBubble(data.response_text, data.recommendations, data.schedule);
      } else {
        appendAssistantBubble("Sorry, I encountered an error processing your query. Please try again.");
      }
    } catch (err) {
      removeElement(loadingId);
      appendAssistantBubble("Connection error. Please check your network and try again.");
    }

    chatBody.scrollTop = chatBody.scrollHeight;
  });

  function appendUserBubble(text) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble user-bubble';
    bubble.innerText = text;
    chatBody.appendChild(bubble);
  }

  function appendAssistantBubble(text, recommendations = [], schedule = []) {
    const bubble = document.createElement('div');
    bubble.className = 'chat-bubble assistant-bubble';

    let html = `<p>${text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</p>`;

    if (recommendations && recommendations.length > 0) {
      html += '<div style="margin-top: 0.75rem;">';
      recommendations.forEach(rec => {
        html += `<div style="background:#ECFDF5; padding:0.5rem 0.75rem; border-radius:6px; border-left:3px solid #10B981; margin-bottom:0.4rem; font-size:0.88rem;">${rec.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')}</div>`;
      });
      html += '</div>';
    }

    if (schedule && schedule.length > 0) {
      html += '<div class="schedule-box">';
      schedule.forEach(item => {
        html += `
          <div class="schedule-item">
            <span class="schedule-time">${item.time}</span>
            <span><i class="fa-solid ${item.icon || 'fa-clock'}"></i> ${item.activity}</span>
          </div>
        `;
      });
      html += '</div>';
    }

    bubble.innerHTML = html;
    chatBody.appendChild(bubble);
  }

  function appendLoadingIndicator() {
    const id = 'loading-' + Date.now();
    const bubble = document.createElement('div');
    bubble.id = id;
    bubble.className = 'chat-bubble assistant-bubble';
    bubble.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> LifePilot AI is thinking...';
    chatBody.appendChild(bubble);
    return id;
  }

  function removeElement(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
  }
});
