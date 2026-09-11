/* =========================
   AI CHAT
========================= */

function toggleChat() {

    const chat = document.getElementById("ai-chat");

    if (chat.style.display === "block") {

        chat.style.display = "none";

    } else {

        chat.style.display = "block";

        document
            .getElementById("chat-input")
            .focus();

    }

}


/* =========================
   SEND AI MESSAGE
========================= */

async function sendMessage() {

    const input =
        document.getElementById("chat-input");

    const message =
        input.value.trim();

    if (!message) {
        return;
    }


    const chat =
        document.getElementById("chat-messages");


    // USER MESSAGE

    const userMessage =
        document.createElement("div");

    userMessage.className =
        "user-message";

    userMessage.innerText =
        message;

    chat.appendChild(userMessage);


    input.value = "";


    // LOADING

    const loading =
        document.createElement("div");

    loading.className =
        "bot-message";

    loading.innerText =
        "Thinking...";

    chat.appendChild(loading);


    try {

        const response =
            await fetch("/ai", {

                method: "POST",

                headers: {
                    "Content-Type":
                        "application/json"
                },

                body: JSON.stringify({
                    message: message
                })

            });


        const data =
            await response.json();


        loading.innerText =
            data.reply;


    } catch (error) {

        console.error(error);

        loading.innerText =
            "Sorry, something went wrong.";

    }


    chat.scrollTop =
        chat.scrollHeight;

}


/* =========================
   ENTER KEY
========================= */

function handleEnter(event) {

    if (event.key === "Enter") {

        sendMessage();

    }

}


/* =========================
   SCROLL REVEAL
========================= */

function revealElements() {

    const elements =
        document.querySelectorAll(".reveal");


    elements.forEach(element => {

        const position =
            element.getBoundingClientRect()
                   .top;

        const windowHeight =
            window.innerHeight;


        if (position < windowHeight - 80) {

            element.classList.add("active");

        }

    });

}


window.addEventListener(
    "scroll",
    revealElements
);


window.addEventListener(
    "load",
    revealElements
);


/* =========================
   GARMENT MOTION PARALLAX
========================= */

const garmentParallax = () => {
    const heroSection = document.querySelector(".hero-section");
    const heroImageWrap = document.querySelector(".hero-image-wrapper");
    const floatingTags = document.querySelectorAll(".fabric-tag");

    if (!heroSection || !heroImageWrap) return;

    heroSection.addEventListener("mousemove", (event) => {
        const rect = heroSection.getBoundingClientRect();
        const x = (event.clientX - rect.left) / rect.width - 0.5;
        const y = (event.clientY - rect.top) / rect.height - 0.5;

        heroImageWrap.style.transform = `perspective(1200px) rotateX(${(-y * 10).toFixed(2)}deg) rotateY(${(x * 12).toFixed(2)}deg) translateY(${(-y * 8).toFixed(2)}px)`;

        floatingTags.forEach((tag, index) => {
            const offset = (index + 1) * 4;
            tag.style.transform = `translate(${(x * offset * 10).toFixed(2)}px, ${(y * offset * 10).toFixed(2)}px)`;
        });
    });

    heroSection.addEventListener("mouseleave", () => {
        heroImageWrap.style.transform = "perspective(1200px) rotateX(0deg) rotateY(0deg) translateY(0px)";
        floatingTags.forEach(tag => {
            tag.style.transform = "translate(0, 0)";
        });
    });
};

window.addEventListener("load", garmentParallax);