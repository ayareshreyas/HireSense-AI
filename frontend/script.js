const API_URL = "http://127.0.0.1:8000/analyze";


const analyzeButton = document.getElementById(
    "analyze-button"
);

const resumeInput = document.getElementById(
    "resume"
);

const jobDescriptionInput = document.getElementById(
    "job-description"
);

const statusMessage = document.getElementById(
    "status-message"
);

const errorMessage = document.getElementById(
    "error-message"
);


const resultsSection = document.getElementById(
    "results"
);

const overallMatchScoreElement = document.getElementById(
    "overall-match-score"
);

const skillCoverageElement = document.getElementById(
    "skill-coverage"
);

const semanticSimilarityElement = document.getElementById(
    "semantic-similarity"
);

const matchedSkillsList = document.getElementById(
    "matched-skills"
);

const missingSkillsList = document.getElementById(
    "missing-skills"
);

const skillEvidenceList = document.getElementById(
    "skill-evidence-list"
);

const requiredSkillsElement = document.getElementById(
    "required-skills"
);

const preferredSkillsElement = document.getElementById(
    "preferred-skills"
);

const experienceRequirementsList = document.getElementById(
    "experience-requirements"
);

const educationRequirementsList = document.getElementById(
    "education-requirements"
);

const recommendationsList = document.getElementById(
    "recommendations-list"
);


analyzeButton.addEventListener("click", async () => {

    clearMessages();

    const resumeFile = resumeInput.files[0];

    const jobDescription =
        jobDescriptionInput.value.trim();


    if (!resumeFile) {
        showError(
            "Please upload your resume."
        );

        return;
    }


    if (!jobDescription) {
        showError(
            "Please paste a job description."
        );

        return;
    }


    if (
        resumeFile.type &&
        resumeFile.type !== "application/pdf"
    ) {
        showError(
            "Please upload a PDF resume."
        );

        return;
    }


    const formData = new FormData();

    formData.append(
        "resume",
        resumeFile
    );

    formData.append(
        "job_description",
        jobDescription
    );


    setLoadingState(true);

    resultsSection.hidden = true;

    showStatus(
        "Analyzing your resume against the job description..."
    );


    try {

        const response = await fetch(
            API_URL,
            {
                method: "POST",
                body: formData
            }
        );


        let data;

        try {
            data = await response.json();

        } catch {
            throw new Error(
                "The server returned an invalid response."
            );
        }


        if (!response.ok) {

            const message =
                data.detail ||
                "Resume analysis failed.";

            throw new Error(message);
        }


        console.log(
            "HireSense API response:",
            data
        );


        displayResults(data);

        hideStatus();


    } catch (error) {

        console.error(
            "HireSense error:",
            error
        );


        hideStatus();

        showError(
            error.message ||
            "Something went wrong while analyzing your resume."
        );


    } finally {

        setLoadingState(false);
    }
});


function displayResults(data) {

    validateRequiredElements();


    overallMatchScoreElement.textContent =
        formatPercentage(
            data.overall_match_score
        );


    skillCoverageElement.textContent =
        formatPercentage(
            data.skill_coverage
        );


    semanticSimilarityElement.textContent =
        formatPercentage(
            data.semantic_similarity
        );


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


    renderSkillEvidence(
        data.skill_evidence
    );


    renderJobRequirements(
        data.job_requirements
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


function validateRequiredElements() {

    const requiredElements = [
        [
            "analyze-button",
            analyzeButton
        ],
        [
            "resume",
            resumeInput
        ],
        [
            "job-description",
            jobDescriptionInput
        ],
        [
            "status-message",
            statusMessage
        ],
        [
            "error-message",
            errorMessage
        ],
        [
            "results",
            resultsSection
        ],
        [
            "overall-match-score",
            overallMatchScoreElement
        ],
        [
            "skill-coverage",
            skillCoverageElement
        ],
        [
            "semantic-similarity",
            semanticSimilarityElement
        ],
        [
            "matched-skills",
            matchedSkillsList
        ],
        [
            "missing-skills",
            missingSkillsList
        ],
        [
            "skill-evidence-list",
            skillEvidenceList
        ],
        [
            "required-skills",
            requiredSkillsElement
        ],
        [
            "preferred-skills",
            preferredSkillsElement
        ],
        [
            "experience-requirements",
            experienceRequirementsList
        ],
        [
            "education-requirements",
            educationRequirementsList
        ],
        [
            "recommendations-list",
            recommendationsList
        ]
    ];


    requiredElements.forEach(
        ([id, element]) => {

            if (!element) {
                throw new Error(
                    `HTML element with id="${id}" was not found.`
                );
            }
        }
    );
}


function renderSkillEvidence(skillEvidence) {

    skillEvidenceList.innerHTML = "";


    if (
        !skillEvidence ||
        typeof skillEvidence !== "object" ||
        Object.keys(skillEvidence).length === 0
    ) {

        const message =
            document.createElement("p");

        message.textContent =
            "No skill evidence was detected.";

        skillEvidenceList.appendChild(
            message
        );

        return;
    }


    Object.entries(skillEvidence).forEach(
        ([skill, sections]) => {

            const card =
                document.createElement("div");

            card.className =
                "evidence-card";


            const skillTitle =
                document.createElement("h4");

            skillTitle.textContent =
                formatSkillName(skill);

            card.appendChild(
                skillTitle
            );


            const tagsContainer =
                document.createElement("div");

            tagsContainer.className =
                "evidence-tags";


            if (
                Array.isArray(sections) &&
                sections.length > 0
            ) {

                sections.forEach((section) => {

                    const tag =
                        document.createElement(
                            "span"
                        );

                    tag.className =
                        "evidence-tag";

                    tag.textContent =
                        section;

                    tagsContainer.appendChild(
                        tag
                    );
                });

            } else {

                const tag =
                    document.createElement(
                        "span"
                    );

                tag.className =
                    "evidence-tag";

                tag.textContent =
                    "No section evidence";

                tagsContainer.appendChild(
                    tag
                );
            }


            card.appendChild(
                tagsContainer
            );


            skillEvidenceList.appendChild(
                card
            );
        }
    );
}


function renderJobRequirements(
    jobRequirements
) {

    const requirements =
        jobRequirements || {};


    renderRequirementTags(
        requiredSkillsElement,
        requirements.required_skills
    );


    renderRequirementTags(
        preferredSkillsElement,
        requirements.preferred_skills
    );


    renderList(
        experienceRequirementsList,
        requirements.experience_requirements,
        formatRequirementText
    );


    renderList(
        educationRequirementsList,
        requirements.education_requirements,
        formatRequirementText
    );
}


function renderRequirementTags(
    element,
    skills
) {

    element.innerHTML = "";


    if (
        !Array.isArray(skills) ||
        skills.length === 0
    ) {

        const tag =
            document.createElement("span");

        tag.className =
            "requirement-tag empty-tag";

        tag.textContent =
            "None detected";

        element.appendChild(
            tag
        );

        return;
    }


    skills.forEach((skill) => {

        const tag =
            document.createElement("span");

        tag.className =
            "requirement-tag";

        tag.textContent =
            formatSkillName(skill);

        element.appendChild(
            tag
        );
    });
}


function renderList(
    element,
    items,
    formatter = null
) {

    element.innerHTML = "";


    if (
        !Array.isArray(items) ||
        items.length === 0
    ) {

        const listItem =
            document.createElement("li");

        listItem.textContent =
            "None detected";

        element.appendChild(
            listItem
        );

        return;
    }


    items.forEach((item) => {

        const listItem =
            document.createElement("li");


        listItem.textContent =
            formatter
                ? formatter(item)
                : item;


        element.appendChild(
            listItem
        );
    });
}


function formatPercentage(value) {

    if (
        value === null ||
        value === undefined ||
        value === ""
    ) {
        return "N/A";
    }


    const number =
        Number(value);


    if (Number.isNaN(number)) {
        return "N/A";
    }


    return `${number}%`;
}


function formatSkillName(skill) {

    if (typeof skill !== "string") {
        return String(skill);
    }


    const normalizedSkill =
        skill.toLowerCase().trim();


    if (normalizedSkill.includes(" or ")) {

        return normalizedSkill
            .split(" or ")
            .map((part) => {
                return formatSkillName(part);
            })
            .join(" or ");
    }


    const specialNames = {

        aws: "AWS",
        gcp: "GCP",
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

        pytorch: "PyTorch",

        numpy: "NumPy",

        pandas: "Pandas",

        matplotlib: "Matplotlib",

        docker: "Docker",

        kubernetes: "Kubernetes",

        python: "Python",

        java: "Java",

        git: "Git",

        aws: "AWS",

        azure: "Azure",

        gcp: "GCP",

        "node.js": "Node.js",

        "scikit-learn": "Scikit-learn",

        "machine learning":
            "Machine Learning",

        "artificial intelligence":
            "Artificial Intelligence",

        "generative ai":
            "Generative AI"
    };


    if (specialNames[normalizedSkill]) {

        return specialNames[
            normalizedSkill
        ];
    }


    return normalizedSkill
        .split(" ")
        .map((word) => {

            return (
                word.charAt(0).toUpperCase() +
                word.slice(1)
            );
        })
        .join(" ");
}


function formatRequirementText(text) {

    if (typeof text !== "string") {
        return String(text);
    }


    if (!text.length) {
        return text;
    }


    return (
        text.charAt(0).toUpperCase() +
        text.slice(1)
    );
}


function showStatus(message) {

    statusMessage.textContent =
        message;

    statusMessage.hidden =
        false;
}


function hideStatus() {

    statusMessage.textContent =
        "";

    statusMessage.hidden =
        true;
}


function showError(message) {

    errorMessage.textContent =
        message;

    errorMessage.hidden =
        false;

    errorMessage.scrollIntoView({
        behavior: "smooth",
        block: "center"
    });
}


function hideError() {

    errorMessage.textContent =
        "";

    errorMessage.hidden =
        true;
}


function clearMessages() {

    hideStatus();
    hideError();
}


function setLoadingState(isLoading) {

    analyzeButton.disabled =
        isLoading;

    resumeInput.disabled =
        isLoading;

    jobDescriptionInput.disabled =
        isLoading;


    if (isLoading) {

        analyzeButton.textContent =
            "Analyzing Resume...";

    } else {

        analyzeButton.textContent =
            "Analyze Resume";
    }
}

