const analyzeBtn = document.getElementById("analyze-btn");
const repoUrlInput = document.getElementById("repo-url");
const resultSection = document.getElementById("result-section");
const errorMessage = document.getElementById("error-message");

analyzeBtn.addEventListener("click", async () => {
    const url = repoUrlInput.value.trim();
    if (!url) return alert("Please enter a GitHub URL.");

    resultSection.classList.add("hidden");
    errorMessage.classList.add("hidden");

    try {
        const response = await fetch(`/analyze?url=${encodeURIComponent(url)}`);
        const data = await response.json();

        if (data.error) {
            errorMessage.textContent = data.error;
            errorMessage.classList.remove("hidden");
            return;
        }

        // Fill in data
        document.getElementById("repo-name").textContent = data.repository;
        document.getElementById("score-fill").style.width = `${data.score}%`;
        document.getElementById("score-text").textContent = `${data.score}/100`;
        document.getElementById("summary-text").textContent = data.summary;

        const roadmapList = document.getElementById("roadmap-list");
        roadmapList.innerHTML = "";
        data.roadmap.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            roadmapList.appendChild(li);
        });

        document.getElementById("commit-count").textContent = data.commit_count;
        document.getElementById("file-count").textContent = data.file_count;
        document.getElementById("folder-count").textContent = data.folder_count;
        document.getElementById("stars-count").textContent = data.stars;
        document.getElementById("forks-count").textContent = data.forks;
        document.getElementById("main-language").textContent = data.main_language || "Not detected";

        resultSection.classList.remove("hidden");

    } catch (err) {
        errorMessage.textContent = "Something went wrong. Please try again.";
        errorMessage.classList.remove("hidden");
        console.error(err);
    }
});
