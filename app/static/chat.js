const form = document.querySelector("#prompt-form");
const promptInput = document.querySelector("#prompt");
const send = form.querySelector(".send");
const error = document.querySelector("#composer-alert");
const conversation = document.querySelector("#conversation");
const pendingTemplate = document.querySelector("#pending-turn");
const replyStatus = document.querySelector("#reply-status");
const turnMediaType = "text/vnd.medica.turn+html";

for (const example of document.querySelectorAll(".example")) {
    example.addEventListener("click", (event) => {
        event.preventDefault();
        promptInput.value = example.value;
        promptInput.focus();
    });
}

promptInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter" && !event.shiftKey && !event.isComposing) {
        event.preventDefault();
        if (!send.disabled) form.requestSubmit();
    }
});

form.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (send.disabled) return;

    const question = promptInput.value.trim();
    if (!question) {
        error.textContent = "Bir sağlık sorusu yazın.";
        error.hidden = false;
        promptInput.focus();
        return;
    }

    error.hidden = true;
    send.disabled = true;
    promptInput.value = "";
    promptInput.focus();
    replyStatus.textContent = "Yanıt hazırlanıyor…";

    const welcome = document.querySelector("#welcome");
    if (welcome) welcome.hidden = true;
    const pending = pendingTemplate.content.firstElementChild.cloneNode(true);
    pending.querySelector(".user-text").textContent = question;
    conversation.append(pending);
    pending.scrollIntoView({ block: "start" });

    try {
        const response = await fetch(form.action, {
            method: "POST",
            headers: { Accept: turnMediaType },
            body: new URLSearchParams({ prompt: question }),
        });
        if (!response.ok || !response.headers.get("Content-Type")?.startsWith(turnMediaType)) {
            throw new Error("Unexpected response");
        }

        // The Flask partial escapes all user, model, and source text.
        const turn = document.createElement("template");
        turn.innerHTML = (await response.text()).trim();
        pending.replaceWith(turn.content);
        replyStatus.textContent = "Medica RAG yanıtı hazır.";
    } catch {
        pending.remove();
        if (welcome && !conversation.querySelector(".turn")) welcome.hidden = false;
        if (!promptInput.value) promptInput.value = question;
        replyStatus.textContent = "";
        error.textContent = "Mesaj gönderilemedi. Lütfen yeniden deneyin.";
        error.hidden = false;
    } finally {
        send.disabled = false;
    }
});
