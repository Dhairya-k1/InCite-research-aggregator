const express = require("express");
const cors = require("cors");

const app = express();

const PORT = 5000;

app.use(cors());
app.use(express.json());


// ======================================================
// HELPER FUNCTIONS
// ======================================================

function cleanText(text) {

    if (!text) {
        return "";
    }

    return text
        .replace(/\s+/g, " ")
        .trim();
}


// ======================================================
// GET DATE FOR LATEST PAPERS
// ======================================================

function getRecentStartDate() {

    const date = new Date();

    // Last 2 years
    date.setFullYear(
        date.getFullYear() - 2
    );

    return date
        .toISOString()
        .split("T")[0];
}


// ======================================================
// RECONSTRUCT OPENALEX ABSTRACT
// ======================================================

function reconstructAbstract(invertedIndex) {

    if (!invertedIndex) {
        return "";
    }

    const words = [];

    for (
        const [word, positions]
        of Object.entries(invertedIndex)
    ) {

        for (
            const position
            of positions
        ) {

            words[position] = word;
        }
    }

    return words.join(" ");
}


// ======================================================
// SEARCH ARXIV
// ======================================================

async function searchArxiv(
    query,
    maxResults = 10
) {

    try {

        console.log(
            `Searching arXiv for: ${query}`
        );


        const startDate =
            getRecentStartDate()
                .replaceAll("-", "");


        const endDate =
            new Date()
                .toISOString()
                .split("T")[0]
                .replaceAll("-", "");


        const searchQuery =
            `all:${query} AND ` +
            `submittedDate:[${startDate}000000 TO ${endDate}235959]`;


        const url =
            `https://export.arxiv.org/api/query?` +
            `search_query=${encodeURIComponent(searchQuery)}` +
            `&start=0` +
            `&max_results=${maxResults}` +
            `&sortBy=submittedDate` +
            `&sortOrder=descending`;


        const response =
            await fetch(url);


        if (!response.ok) {

            throw new Error(
                `arXiv returned HTTP ${response.status}`
            );
        }


        const xml =
            await response.text();


        const entries =
            xml
                .split("<entry>")
                .slice(1);


        const papers = [];


        for (
            const entry
            of entries
        ) {

            const idMatch =
                entry.match(
                    /<id>(.*?)<\/id>/
                );


            const titleMatch =
                entry.match(
                    /<title>([\s\S]*?)<\/title>/
                );


            const abstractMatch =
                entry.match(
                    /<summary>([\s\S]*?)<\/summary>/
                );


            const publishedMatch =
                entry.match(
                    /<published>(.*?)<\/published>/
                );


            const id =
                idMatch
                    ? idMatch[1].trim()
                    : "";


            const title =
                titleMatch
                    ? cleanText(
                        titleMatch[1]
                    )
                    : "";


            const abstract =
                abstractMatch
                    ? cleanText(
                        abstractMatch[1]
                    )
                    : "";


            const published =
                publishedMatch
                    ? publishedMatch[1]
                    : "";


            const authors = [
                ...entry.matchAll(
                    /<name>(.*?)<\/name>/g
                )
            ].map(
                match =>
                    cleanText(match[1])
            );


            const pdfMatch =
                entry.match(
                    /<link[^>]+title="pdf"[^>]+href="([^"]+)"/
                );


            const pdfUrl =
                pdfMatch
                    ? pdfMatch[1]
                    : "";


            const arxivId =
                id
                    ? id.split("/").pop()
                    : "";


            papers.push({

                id:
                    `arxiv:${arxivId}`,

                source:
                    "arXiv",

                title,

                authors,

                abstract,

                year:
                    published
                        ? new Date(
                            published
                        ).getFullYear()
                        : null,

                publicationDate:
                    published || null,

                url:
                    id,

                pdfUrl,

                topics: [],

                citationCount:
                    null,

                openAccess:
                    true
            });
        }


        console.log(
            `arXiv returned ${papers.length} recent papers`
        );


        return papers;


    } catch (error) {

        console.error(
            "arXiv error:",
            error.message
        );

        return [];
    }
}


// ======================================================
// SEARCH OPENALEX
// ======================================================

async function searchOpenAlex(
    query,
    maxResults = 10
) {

    try {

        console.log(
            `Searching OpenAlex for: ${query}`
        );


        const startDate =
            getRecentStartDate();


        const url =
            `https://api.openalex.org/works?` +
            `search=${encodeURIComponent(query)}` +
            `&filter=from_publication_date:${startDate}` +
            `&sort=publication_date:desc` +
            `&per-page=${maxResults}`;


        const response =
            await fetch(url);


        if (!response.ok) {

            throw new Error(
                `OpenAlex returned HTTP ${response.status}`
            );
        }


        const data =
            await response.json();


        const papers =
            data.results.map(
                paper => {

                    const authors =
                        (
                            paper.authorships ||
                            []
                        )
                        .map(
                            authorship =>
                                authorship.author
                                    ?.display_name
                        )
                        .filter(Boolean);


                    const topics =
                        (
                            paper.topics ||
                            []
                        )
                        .map(
                            topic =>
                                topic.display_name
                        )
                        .filter(Boolean);


                    const pdfUrl =
                        paper.best_oa_location
                            ?.pdf_url ||
                        paper.primary_location
                            ?.pdf_url ||
                        null;


                    const landingPage =
                        paper.primary_location
                            ?.landing_page_url ||
                        paper.doi ||
                        paper.id;


                    return {

                        id:
                            `openalex:${paper.id
                                .split("/")
                                .pop()}`,

                        source:
                            "OpenAlex",

                        title:
                            cleanText(
                                paper.title
                            ),

                        authors,

                        abstract:
                            reconstructAbstract(
                                paper.abstract_inverted_index
                            ),

                        year:
                            paper.publication_year ||
                            null,

                        publicationDate:
                            paper.publication_date ||
                            null,

                        url:
                            landingPage,

                        pdfUrl,

                        topics,

                        citationCount:
                            paper.cited_by_count ||
                            0,

                        openAccess:
                            paper.open_access
                                ?.is_oa ||
                            false,

                        doi:
                            paper.doi ||
                            null,

                        openAlexId:
                            paper.id,

                        type:
                            paper.type ||
                            null
                    };
                }
            );


        console.log(
            `OpenAlex returned ${papers.length} recent papers`
        );


        return papers;


    } catch (error) {

        console.error(
            "OpenAlex error:",
            error.message
        );

        return [];
    }
}


// ======================================================
// NORMALIZE TITLE
// ======================================================

function normalizeTitle(title) {

    return title
        .toLowerCase()
        .replace(
            /[^a-z0-9\s]/g,
            ""
        )
        .replace(
            /\s+/g,
            " "
        )
        .trim();
}


// ======================================================
// REMOVE DUPLICATES
// ======================================================

function deduplicatePapers(
    papers
) {

    const unique =
        new Map();


    for (
        const paper
        of papers
    ) {

        const title =
            normalizeTitle(
                paper.title
            );


        const key =
            `${title}|${paper.year}`;


        if (
            !unique.has(key)
        ) {

            unique.set(
                key,
                paper
            );

        } else {

            const existing =
                unique.get(key);


            // Prefer OpenAlex if
            // both sources contain
            // the same paper.

            if (
                existing.source ===
                "arXiv" &&
                paper.source ===
                "OpenAlex"
            ) {

                unique.set(
                    key,
                    paper
                );
            }
        }
    }


    return Array.from(
        unique.values()
    );
}


// ======================================================
// SORT BY PUBLICATION DATE
// ======================================================

function sortByLatest(
    papers
) {

    return papers.sort(
        (a, b) => {

            const dateA =
                new Date(
                    a.publicationDate ||
                    `${a.year || 1900}-01-01`
                );


            const dateB =
                new Date(
                    b.publicationDate ||
                    `${b.year || 1900}-01-01`
                );


            return (
                dateB - dateA
            );
        }
    );
}


// ======================================================
// MAIN SEARCH API
// ======================================================

app.get(
    "/api/papers",
    async (req, res) => {

        try {

            const field =
                req.query.field ||
                "";


            const interests =
                req.query.interests ||
                "";


            const goal =
                req.query.goal ||
                "";


            const oldQuery =
                req.query.q ||
                "";


            /*
             * Build a personalized
             * research query.
             */

            const query =
                [
                    field,
                    interests,
                    goal,
                    oldQuery
                ]
                .filter(Boolean)
                .join(" ");


            const finalQuery =
                query ||
                "artificial intelligence";


            const limit =
                Math.min(
                    parseInt(
                        req.query.limit
                    ) || 10,
                    20
                );


            console.log(
                "===================================="
            );

            console.log(
                "Personalized research search"
            );

            console.log(
                `Field: ${field}`
            );

            console.log(
                `Interests: ${interests}`
            );

            console.log(
                `Goal: ${goal}`
            );

            console.log(
                `Query: ${finalQuery}`
            );

            console.log(
                "===================================="
            );


            const [
                arxivPapers,
                openAlexPapers
            ] =
                await Promise.all([

                    searchArxiv(
                        finalQuery,
                        limit
                    ),

                    searchOpenAlex(
                        finalQuery,
                        limit
                    )
                ]);


            const combined = [

                ...arxivPapers,

                ...openAlexPapers

            ];


            const unique =
                deduplicatePapers(
                    combined
                );


            const papers =
                sortByLatest(
                    unique
                );


            res.json({

                success:
                    true,

                preferences: {

                    field,

                    interests,

                    goal
                },

                query:
                    finalQuery,

                latestPeriod:
                    `Last 2 years`,

                totalResults:
                    papers.length,

                sources: {

                    arxiv:
                        arxivPapers.length,

                    openAlex:
                        openAlexPapers.length
                },

                papers
            });


        } catch (error) {

            console.error(
                "Search API error:",
                error
            );


            res.status(500).json({

                success:
                    false,

                error:
                    "Failed to fetch research papers",

                details:
                    error.message
            });
        }
    }
);


// ======================================================
// HOME
// ======================================================

app.get(
    "/",
    (req, res) => {

        res.json({

            message:
                "InCite Backend is running successfully!",

            sources: [
                "OpenAlex",
                "arXiv"
            ],

            latestOnly:
                true,

            endpoints: {

                search:
                    "/api/papers",

                example:
                    "/api/papers?field=Artificial%20Intelligence&interests=Computer%20Vision&goal=Latest%20research%20trends"
            }
        });
    }
);


// ======================================================
// START SERVER
// ======================================================

app.listen(
    PORT,
    () => {

        console.log(
            "===================================="
        );

        console.log(
            "InCite Backend Started"
        );

        console.log(
            "Sources: OpenAlex + arXiv"
        );

        console.log(
            "Mode: Latest personalized research"
        );

        console.log(
            `Server: http://localhost:${PORT}`
        );

        console.log(
            "===================================="
        );
    }
);