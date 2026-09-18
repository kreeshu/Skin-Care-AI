document.addEventListener("click", (event) => {
  const reveal = event.target.closest("[data-reveal]");
  if (reveal) {
    document.getElementById(reveal.dataset.reveal)?.classList.toggle("visible");
    return;
  }

  const option = event.target.closest("[data-answer]");
  if (!option) return;
  const quiz = option.closest("[data-quiz]");
  quiz.querySelectorAll("[data-answer]").forEach((button) => {
    button.classList.remove("correct", "incorrect");
  });
  const correct = option.dataset.answer === "correct";
  option.classList.add(correct ? "correct" : "incorrect");
  quiz.querySelector(".feedback").textContent = correct
    ? "Correct. The model scores concerns; rules and catalog data select products."
    : "Not quite. Separate the vision model from the recommendation engine.";
});
