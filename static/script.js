async function getTranscript() {

    const url = document.getElementById("url").value.trim();

    const result = document.getElementById("result");

    if (!url) {
        alert("Please enter a YouTube URL.");
        return;
    }

    result.value = "Fetching transcript...";

    try {

        const response = await fetch("/api/transcript", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                url: url
            })
        });

        const data = await response.json();

        if (data.success) {
            result.value = data.transcript;
        } else {
            result.value = "Error: " + data.message;
        }

    } catch (error) {
        result.value = "Failed to connect to the server.";
        console.error(error);
    }

}

function copyTranscript() {

    const result = document.getElementById("result");

    if (!result.value) {
        alert("Nothing to copy.");
        return;
    }

    navigator.clipboard.writeText(result.value)
        .then(() => {
            alert("Transcript copied successfully!");
        })
        .catch(() => {
            result.select();
            document.execCommand("copy");
            alert("Transcript copied.");
        });

}
