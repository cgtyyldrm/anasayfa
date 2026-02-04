export const GAS_API_URL = "https://script.google.com/macros/s/AKfycbz3XIo_AOZxmvW4658P6xRq_MACItUfGwb8zayv2XTeJm9eQsX1hZNmseQVOy76LRLLJg/exec";

export async function submitVote(panelistId: string, panelistName: string, scores: any) {
    if (GAS_API_URL.includes("BURAYA")) {
        console.warn("GAS URL not set. Logging to console instead.");
        console.log("Vote Data:", { panelistId, panelistName, scores });
        return { success: true };
    }

    try {
        const response = await fetch(GAS_API_URL, {
            method: "POST",
            body: JSON.stringify({
                action: "submitVote",
                panelistId,
                panelistName,
                scores
            })
        });
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return { success: false, error };
    }
}

export async function verifyLogin(username: string, password: string) {
    if (GAS_API_URL.includes("BURAYA")) {
        console.warn("GAS URL not set.");
        return { success: false, message: "API not configured" };
    }

    try {
        const response = await fetch(`${GAS_API_URL}?action=verifyLogin&username=${username}&password=${password}`);
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return { success: false, error };
    }
}

export async function getScores() {
    if (GAS_API_URL.includes("BURAYA")) {
        console.warn("GAS URL not set. Returning empty list.");
        return [];
    }

    try {
        const response = await fetch(`${GAS_API_URL}?action=getScores`);
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return [];
    }
}

export async function getGameState() {
    if (GAS_API_URL.includes("BURAYA")) {
        // Mock state for development if API not set
        return {
            activeCriteria: ["ozgun_deger", "yontem", "proje_yonetimi", "yaygin_etki"],
            resultsPublished: false
        };
    }

    try {
        const response = await fetch(`${GAS_API_URL}?action=getGameState`);
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return { activeCriteria: [], resultsPublished: false };
    }
}

export async function updateGameState(activeCriteria: string[], resultsPublished: boolean) {
    if (GAS_API_URL.includes("BURAYA")) {
        console.log("Mock updateGameState:", { activeCriteria, resultsPublished });
        return { success: true };
    }

    try {
        const response = await fetch(GAS_API_URL, {
            method: "POST",
            body: JSON.stringify({
                action: "updateGameState",
                activeCriteria,
                resultsPublished
            })
        });
        return await response.json();
    } catch (error) {
        console.error("API Error:", error);
        return { success: false, error };
    }
}
