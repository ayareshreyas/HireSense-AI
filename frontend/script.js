const API_URL = "http://127.0.0.1:8000/analyze";

const analyzeButton = document.getElementById("analyze-button");
const resumeInput = document.getElementById("resume");
const jobDescriptionInput = document.getElementById("job-description");

const resultsSection = document.getElementById("results");
const skillCoverageElement = document.getElementById("skill-coverage");
const semanticSimilarityElement = document.getElementById(
    "semantic-similarity"
);

const matchedSkillsList = document.getElementById("matched-skills");
const missingSkillsList = document.getElementById("missing-skills");
const recommendationsList = document.getElementById(
    "recommendations-list"
);


analyzeButton.addEventListener("click", async () => {
    const resumeFile = resumeInput.files[0];
    const jobDescription = jobDescriptionInput.value.trim();

    if (!resumeFile) {
        alert("Please upload your resume.");
        return;
    }

    if (!jobDescription) {
        alert("Please paste a job description.");
        return;
    }

    if (
        resumeFile.type &&
        resumeFile.type !== "application/pdf"
    ) {
        alert("Please upload a PDF resume.");
        return;
    }

    const formData = new FormData();

    formData.append("resume", resumeFile);
    formData.append("job_description", jobDescription);

    setLoadingState(true);

    try {
        const response = await fetch(API_URL, {
            method: "POST",
            body: formData
        });

        const data = await response.json();

        if (!response.ok) {
            const message =
                data.detail ||
                "Resume analysis failed.";

            throw new Error(message);
        }

        console.log("HireSense API response:", data);

        displayResults(data);

    } catch (error) {
        console.error("HireSense error:", error);

        alert(
            `Analysis failed: ${error.message}`
        );

    } finally {
        setLoadingState(false);
    }
});


function displayResults(data) {
    if (!resultsSection) {
        throw new Error(
            'HTML element with id="results" was not found.'
        );
    }

    if (!skillCoverageElement) {
        throw new Error(
            'HTML element with id="skill-coverage" was not found.'
        );
    }

    if (!semanticSimilarityElement) {
        throw new Error(
            'HTML element with id="semantic-similarity" was not found.'
        );
    }

    if (!matchedSkillsList) {
        throw new Error(
            'HTML element with id="matched-skills" was not found.'
        );
    }

    if (!missingSkillsList) {
        throw new Error(
            'HTML element with id="missing-skills" was not found.'
        );
    }

    if (!recommendationsList) {
        throw new Error(
            'HTML element with id="recommendations-list" was not found.'
        );
    }


    skillCoverageElement.textContent =
        formatPercentage(data.skill_coverage);

    semanticSimilarityElement.textContent =
        formatPercentage(data.semantic_similarity);


    renderList(
        matchedSkillsList,
        data.matched_skills,
        formatSkillName
    );

    renderList(
        missingSkillsList,
        data.missing_skills,
        formatSkillName
    );

    renderList(
        recommendationsList,
        data.recommendations
    );


    resultsSection.hidden = false;

    resultsSection.scrollIntoView({
        behavior: "smooth",
        block: "start"
    });
}


function renderList(element, items, formatter = null) {
    element.innerHTML = "";

    if (!Array.isArray(items) || items.length === 0) {
        const listItem = document.createElement("li");

        listItem.textContent = "None";

        element.appendChild(listItem);

        return;
    }

    items.forEach((item) => {
        const listItem = document.createElement("li");

        listItem.textContent =
            formatter
                ? formatter(item)
                : item;

        element.appendChild(listItem);
    });
}


function formatPercentage(value) {
    const number = Number(value);

    if (Number.isNaN(number)) {
        return "N/A";
    }

    return `${number}%`;
}


function formatSkillName(skill) {
    if (typeof skill !== "string") {
        return String(skill);
    }

    const specialNames = {
        aws: "AWS",
        sql: "SQL",
        html: "HTML",
        css: "CSS",
        nlp: "NLP",
        ai: "AI",
        ml: "ML",
        javascript: "JavaScript",
        fastapi: "FastAPI",
        github: "GitHub",
        tensorflow: "TensorFlow",
        numpy: "NumPy",
        pandas: "Pandas",
        matplotlib: "Matplotlib",
        docker: "Docker",
        python: "Python",
        java: "Java",
        git: "Git"
    };

    const normalizedSkill = skill.toLowerCase();

    if (specialNames[normalizedSkill]) {
        return specialNames[normalizedSkill];
    }

    return skill
        .split(" ")
        .map((word) => {
            return (
                word.charAt(0).toUpperCase() +
                word.slice(1)
            );
        })
        .join(" ");
}


function setLoadingState(isLoading) {
    analyzeButton.disabled = isLoading;

    if (isLoading) {
        analyzeButton.textContent = "Analyzing...";
    } else {
        analyzeButton.textContent = "Analyze Resume";
    }
}