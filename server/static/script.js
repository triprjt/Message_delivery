document
  .getElementById("eventForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault();

    // Extract JSON string from the textarea
    const jsonString = document.getElementById("jsonInput").value;
    const responseStatusMessageDiv =
      document.getElementById("responseStatusDiv");
    try {
      const response = await fetch("http://localhost:5001/submit_event", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: jsonString,
      });

      const responseData = await response.json();
      const responseString = JSON.stringify(responseData, null, 2);

      if (response.status === 200) {
        responseStatusMessageDiv.innerHTML = `<pre style="color: green">${responseString}</pre>`;
        document.getElementById("jsonInput").value = "";
      } else {
        responseStatusMessageDiv.innerHTML = `<pre style="color: red">${responseString}</pre>`;
      }
    } catch (error) {
      console.error("There was an error:", error);
      responseStatusMessageDiv.textContent = "Error: " + error;
      responseStatusMessageDiv.style.color = "red";
    }
  });
