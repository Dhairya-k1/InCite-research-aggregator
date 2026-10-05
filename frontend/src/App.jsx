import { useEffect, useState } from "react";
import "./App.css";

const API_URL = "http://localhost:5000/api/papers";

function App() {


    // ==================================================
    // PREFERENCE STATE
    // ==================================================
    const [preferences, setPreferences] =
        useState(null);

    const [field, setField] =
        useState("");

    const [interests, setInterests] =
        useState("");

    const [goal, setGoal] =
        useState("");


    // ==================================================
    // PAPER STATE
    // ==================================================

    const [papers, setPapers] =
        useState([]);

    const [loading, setLoading] =
        useState(false);

    const [error, setError] =
        useState("");

    const [selectedPaper, setSelectedPaper] =
        useState(null);


    // ==================================================
    // SEARCH STATE
    // ==================================================

    const [searchValue, setSearchValue] =
        useState("");


    // ==================================================
    // CHECK SAVED PREFERENCES
    // ==================================================

    useEffect(() => {
    const saved = localStorage.getItem("incitePreferences");

    if (saved) {
        const parsed = JSON.parse(saved);

        setPreferences(parsed);
        setField(parsed.field);
        setInterests(parsed.interests);
        setGoal(parsed.goal);

        // Tell the browser that the current page is
        // the Research Feed, not the Preference page.
        window.history.replaceState(
            { view: "feed" },
            "",
            window.location.pathname
        );
    }
}, []);
useEffect(() => {
    const handleBrowserBack = () => {
        // If the browser goes back from a paper,
        // return to the Research Feed.
        setSelectedPaper(null);
    };

    window.addEventListener(
        "popstate",
        handleBrowserBack
    );

    return () => {
        window.removeEventListener(
            "popstate",
            handleBrowserBack
        );
    };
}, []);


    // ==================================================
    // FETCH PERSONALIZED PAPERS
    // ==================================================

    const fetchPapers = async (
        selectedPreferences
    ) => {

        try {

            setLoading(true);

            setError("");


            const params =
                new URLSearchParams({

                    field:
                        selectedPreferences.field,

                    interests:
                        selectedPreferences.interests,

                    goal:
                        selectedPreferences.goal
                });


            const response =
                await fetch(
                    `${API_URL}?${params.toString()}`
                );


            if (!response.ok) {

                throw new Error(
                    "Failed to fetch research papers"
                );
            }


            const data =
                await response.json();


            setPapers(
                data.papers || []
            );


        } catch (err) {

            console.error(err);

            setError(
                "Unable to load research papers. Make sure the backend is running."
            );

        } finally {

            setLoading(false);
        }
    };


    // ==================================================
    // SAVE PREFERENCES
    // ==================================================

    const savePreferences = (event) => {

        event.preventDefault();


        if (
            !field.trim() ||
            !interests.trim() ||
            !goal.trim()
        ) {

            setError(
                "Please complete all three fields."
            );

            return;
        }


        const newPreferences = {

            field:
                field.trim(),

            interests:
                interests.trim(),

            goal:
                goal.trim()
        };


        localStorage.setItem(
            "incitePreferences",
            JSON.stringify(
                newPreferences
            )
        );


        setPreferences(
            newPreferences
        );

        setError("");

        fetchPapers(
            newPreferences
        );
    };


    // ==================================================
    // CHANGE PREFERENCES
    // ==================================================

    const changePreferences = () => {

        setPreferences(null);

        setSelectedPaper(null);

        setPapers([]);

    };


    // ==================================================
    // SEARCH WITHIN INTEREST
    // ==================================================

    const handleSearch = async (
        event
    ) => {

        event.preventDefault();


        if (
            !searchValue.trim()
        ) {
            return;
        }


        const searchPreferences = {

            field,

            interests:
                searchValue,

            goal
        };


        fetchPapers(
            searchPreferences
        );
    };


    // ==================================================
    // PAPER DETAILS
    // ==================================================

    if (selectedPaper) {

        return (

            <div className="app">

                <nav className="navbar">

                    <div
                        className="logo"
                        onClick={() =>
                            setSelectedPaper(null)
                        }
                    >
                        InCite
                    </div>

                    <div className="nav-links">

                        <span
                            onClick={() =>
                                setSelectedPaper(null)
                            }
                        >
                            Research
                        </span>

                        <span
                            onClick={
                                changePreferences
                            }
                        >
                            Preferences
                        </span>

                    </div>

                </nav>


                <main className="paper-details">

                    <button
                        className="back-button"
                        onClick={() => {
                            window.history.back();
                        }}
                    >
                        ← Back to Research
                    </button>


                    <div className="paper-source">

                        {selectedPaper.source}

                    </div>


                    <h1>
                        {selectedPaper.title}
                    </h1>


                    <div className="paper-meta">

                        <strong>
                            Authors:
                        </strong>

                        <span>
                            {selectedPaper.authors?.join(
                                ", "
                            ) || "Unknown"}
                        </span>

                    </div>


                    <div className="paper-meta">

                        <strong>
                            Published:
                        </strong>

                        <span>
                            {selectedPaper.publicationDate ||
                                selectedPaper.year ||
                                "Unknown"}
                        </span>

                    </div>


                    <div className="paper-meta">

                        <strong>
                            Citations:
                        </strong>

                        <span>
                            {selectedPaper.citationCount ??
                                "Not available"}
                        </span>

                    </div>


                    <section>

                        <h2>
                            Abstract
                        </h2>

                        <p>
                            {selectedPaper.abstract ||
                                "Abstract not available."}
                        </p>

                    </section>


                    {selectedPaper.topics?.length >
                        0 && (

                        <section>

                            <h2>
                                Topics
                            </h2>

                            <div className="topics">

                                {selectedPaper.topics.map(
                                    (
                                        topic,
                                        index
                                    ) => (

                                        <span
                                            className="topic"
                                            key={index}
                                        >
                                            {topic}
                                        </span>

                                    )
                                )}

                            </div>

                        </section>

                    )}


                    <section>

                        <h2>
                            Paper Links
                        </h2>


                        <div className="paper-actions">

                            {selectedPaper.url && (

                                <a
                                    href={
                                        selectedPaper.url
                                    }
                                    target="_blank"
                                    rel="noreferrer"
                                    className="primary-button"
                                >
                                    View Paper
                                </a>

                            )}


                            {selectedPaper.pdfUrl && (

                                <a
                                    href={
                                        selectedPaper.pdfUrl
                                    }
                                    target="_blank"
                                    rel="noreferrer"
                                    className="secondary-button"
                                >
                                    Open PDF
                                </a>

                            )}

                        </div>

                    </section>


                    <section className="chat-section">

                        <h2>
                            Chat About This Paper
                        </h2>

                        <p>
                            AI-powered paper
                            discussion will be
                            added next.
                        </p>

                    </section>

                </main>

            </div>
        );
    }


    // ==================================================
    // ONBOARDING SCREEN
    // ==================================================

    if (!preferences) {

        return (

            <div className="app">

                <nav className="navbar">

                    <div className="logo">
                        InCite
                    </div>

                </nav>


                <main className="onboarding">

                    <div className="onboarding-card">

                        <div className="onboarding-label">
                            PERSONALIZE YOUR RESEARCH
                        </div>


                        <h1>
                            What are you interested in?
                        </h1>


                        <p className="onboarding-description">

                            Tell InCite what you want
                            to research. We'll use your
                            preferences to find the
                            latest research papers from
                            OpenAlex and arXiv.

                        </p>


                        <form
                            onSubmit={
                                savePreferences
                            }
                        >

                            <label>
                                What field are you
                                interested in?
                            </label>


                            <select
                                value={field}
                                onChange={(event) =>
                                    setField(
                                        event.target.value
                                    )
                                }
                            >

                                <option value="">
                                    Select a field
                                </option>

                                <option>
                                    Artificial Intelligence
                                </option>

                                <option>
                                    Machine Learning
                                </option>

                                <option>
                                    Data Science
                                </option>

                                <option>
                                    Computer Science
                                </option>

                                <option>
                                    Computer Vision
                                </option>

                                <option>
                                    Natural Language Processing
                                </option>

                                <option>
                                    Robotics
                                </option>

                                <option>
                                    Autonomous Vehicles
                                </option>

                                <option>
                                    Cybersecurity
                                </option>

                                <option>
                                    Software Engineering
                                </option>

                                <option>
                                    Other
                                </option>

                            </select>


                            <label>
                                What topics are you
                                interested in?
                            </label>


                            <input
                                type="text"
                                value={interests}
                                onChange={(event) =>
                                    setInterests(
                                        event.target.value
                                    )
                                }
                                placeholder="e.g. YOLO, LLMs, RAG, autonomous driving"
                            />


                            <label>
                                What do you want to
                                know about this field?
                            </label>


                            <textarea
                                value={goal}
                                onChange={(event) =>
                                    setGoal(
                                        event.target.value
                                    )
                                }
                                placeholder="e.g. I want to learn about the latest techniques, research trends and important developments."
                                rows="5"
                            />


                            {error && (

                                <div className="form-error">
                                    {error}
                                </div>

                            )}


                            <button
                                className="discover-button"
                                type="submit"
                            >
                                Discover My Research →
                            </button>

                        </form>

                    </div>

                </main>

            </div>
        );
    }


    // ==================================================
    // MAIN RESEARCH FEED
    // ==================================================

    return (

        <div className="app">

            <nav className="navbar">

                <div className="logo">
                    InCite
                </div>


                <div className="nav-links">

                    <span>
                        Research
                    </span>

                    <span
                        onClick={
                            changePreferences
                        }
                    >
                        Preferences
                    </span>

                    <span>
                        About
                    </span>

                </div>

            </nav>


            <section className="research-hero">

                <div>

                    <div className="personalized-label">
                        YOUR PERSONALIZED FEED
                    </div>


                    <h1>
                        Latest Research
                        <br />
                        For You.
                    </h1>


                    <p>

                        Latest papers in{" "}

                        <strong>
                            {field}
                        </strong>

                        {" "}based on your interests in{" "}

                        <strong>
                            {interests}
                        </strong>

                    </p>

                </div>


                <form
                    className="search-form"
                    onSubmit={
                        handleSearch
                    }
                >

                    <input
                        type="text"
                        value={searchValue}
                        onChange={(event) =>
                            setSearchValue(
                                event.target.value
                            )
                        }
                        placeholder="Explore another topic..."
                    />


                    <button type="submit">
                        Search
                    </button>

                </form>

            </section>


            <main className="research-container">

                <div className="preference-summary">

                    <div>

                        <strong>
                            Your research goal
                        </strong>

                        <p>
                            {goal}
                        </p>

                    </div>


                    <button
                        onClick={
                            changePreferences
                        }
                    >
                        Change Preferences
                    </button>

                </div>


                <div className="results-header">

                    <div>

                        <h2>
                            Latest Research
                        </h2>

                        <p>
                            Papers from the last
                            {" "}
                            <strong>
                                2 years
                            </strong>
                            , newest first
                        </p>

                    </div>


                    {!loading &&
                        !error && (

                            <div className="result-count">

                                {papers.length}
                                {" "}
                                papers

                            </div>

                        )}

                </div>


                {loading && (

                    <div className="status-message">

                        <div className="loader"></div>

                        <p>
                            Finding the latest
                            research for you...
                        </p>

                    </div>

                )}


                {!loading &&
                    error && (

                        <div className="error-message">

                            <h3>
                                Something went wrong
                            </h3>

                            <p>
                                {error}
                            </p>

                        </div>

                    )}


                {!loading &&
                    !error &&
                    papers.length === 0 && (

                        <div className="status-message">

                            <h3>
                                No recent papers found
                            </h3>

                            <p>
                                Try adding more
                                specific interests.
                            </p>

                        </div>

                    )}


                {!loading &&
                    !error &&
                    papers.length > 0 && (

                        <div className="papers-grid">

                            {papers.map(
                                paper => (

                                    <article
                                        className="paper-card"
                                        key={paper.id}
                                    >

                                        <div className="card-top">

                                            <span className="source-badge">
                                                {paper.source}
                                            </span>


                                            <span className="year">

                                                {paper.publicationDate ||
                                                    paper.year ||
                                                    "N/A"}

                                            </span>

                                        </div>


                                        <h3>
                                            {paper.title}
                                        </h3>


                                        <p className="authors">

                                            {paper.authors?.join(
                                                ", "
                                            ) ||
                                                "Unknown authors"}

                                        </p>


                                        <p className="abstract">

                                            {paper.abstract
                                                ? paper.abstract.length >
                                                  250
                                                    ? paper.abstract.substring(
                                                        0,
                                                        250
                                                    ) + "..."
                                                    : paper.abstract
                                                : "Abstract not available."}

                                        </p>


                                        <div className="card-bottom">

                                            <div className="citation">

                                                Citations:
                                                {" "}

                                                {paper.citationCount ??
                                                    "N/A"}

                                            </div>


                                            <button
                                                onClick={() => {
                                                    window.history.pushState(
                                                        {
                                                            view: "paper",
                                                            paperId: paper.id
                                                        },
                                                        "",
                                                        window.location.pathname
                                                    );

                                                    setSelectedPaper(paper);
                                                }}
                                            >
                                                Read Paper →
                                            </button>

                                        </div>

                                    </article>

                                )
                            )}

                        </div>

                    )}

            </main>


            <footer>

                <p>
                    InCite — AI Powered Research Aggregator
                </p>

                <p>
                    Personalized using OpenAlex & arXiv
                </p>

            </footer>

        </div>
    );
}

export default App;