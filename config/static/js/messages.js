(() => {
  const list = document.querySelector("[data-message-poll]");
  if (!list) return;

  const status = document.querySelector("[data-message-status]");
  const known = new Set(
    Array.from(list.querySelectorAll("[data-message-id]")).map((item) =>
      item.dataset.messageId,
    ),
  );

  const addMessage = (message) => {
    const row = document.createElement("div");
    row.className = `message-row${message.mine ? " message-mine" : ""}`;
    row.dataset.messageId = message.id;

    const avatar = document.createElement("span");
    avatar.className = "avatar avatar-tiny";
    if (message.avatar) {
      const image = document.createElement("img");
      image.src = message.avatar;
      image.alt = "";
      avatar.append(image);
    } else {
      avatar.textContent = message.initial;
    }

    const bubble = document.createElement("div");
    bubble.className = "message-bubble";
    const sender = document.createElement("strong");
    sender.textContent = message.mine ? "You" : message.sender;
    const content = document.createElement("p");
    content.textContent = message.content;
    const time = document.createElement("small");
    time.textContent = new Date(message.created_at).toLocaleString([], {
      dateStyle: "medium",
      timeStyle: "short",
    });

    bubble.append(sender, content, time);
    row.append(avatar, bubble);
    list.append(row);
  };

  const poll = async () => {
    if (document.hidden) return;
    const atBottom =
      list.scrollHeight - list.scrollTop - list.clientHeight < 80;
    try {
      const response = await fetch(list.dataset.messagePoll, {
        headers: { Accept: "application/json" },
        credentials: "same-origin",
      });
      if (!response.ok) throw new Error(`Message refresh failed (${response.status}).`);
      const data = await response.json();
      list.querySelector(".conversation-empty")?.remove();
      for (const message of data.messages) {
        const id = String(message.id);
        if (!known.has(id)) {
          known.add(id);
          addMessage(message);
        }
      }
      if (atBottom) list.scrollTop = list.scrollHeight;
      if (status) status.textContent = "";
    } catch (error) {
      if (status) status.textContent = "Reconnecting to messages…";
      console.error(error);
    }
  };

  list.scrollTop = list.scrollHeight;
  window.setInterval(poll, 5000);
})();
