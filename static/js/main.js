$(document).ready(() => {
  // Track time spent on each page
  const startTime = new Date()

  // Record page exit time
  $(window).on("beforeunload", () => {
    const endTime = new Date()
    const timeSpent = (endTime - startTime) / 1000 // in seconds

    // We can't use AJAX with beforeunload reliably, but in a real app
    // you would want to send this data to the server
    console.log("Time spent on page: " + timeSpent + " seconds")
  })

  // Animate elements on page load
  $(".lesson-container, .quiz-container, .results-container, .home-container").animate(
    {
      opacity: 1,
    },
    500,
  )

  // Add click animation to buttons
  $(".btn").on("click", function () {
    $(this).addClass("clicked")
    setTimeout(() => {
      $(this).removeClass("clicked")
    }, 200)
  })

  // Quiz form validation
  $("form").on("submit", (e) => {
    const answered = $('input[name="answer"]:checked').length > 0

    if (!answered) {
      e.preventDefault()
      alert("Please select an answer before continuing.")
    }
  })
})
