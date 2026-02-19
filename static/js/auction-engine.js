// ============================
// DEBUG FLAG
// ============================
const DEBUG = true;

// ============================
// STATE
// ============================

let appState = {
    currentPlayer: null,
    highestBid: 0,
    highestTeam: null,
    status: "IDLE",
    teams: []
};

let socket = null;

// ============================
// UTILS
// ============================

function log(...args) {
    if (DEBUG) console.log("[AuctionEngine]", ...args);
}

function el(id) {
    return document.getElementById(id);
}

function setText(id, value) {
    const element = el(id);
    if (element) element.innerText = value || "";
}

// ============================
// RENDER FUNCTIONS
// ============================

function renderHeader() {
    if (appState.currentPlayer) {
        setText("player-name", appState.currentPlayer.name);
    } else {
        setText("player-name", "");
    }

    setText("highest-bid", appState.highestBid);

    if (appState.highestTeam) {
        setText("highest-team", appState.highestTeam.name);
    } else {
        setText("highest-team", "");
    }
}

function renderTimer() {
    setText("timer", appState.status);
}

function renderLeaderboard() {
    const container = el("leaderboard");
    if (!container || !appState.teams) return;

    container.innerHTML = "";

    appState.teams.forEach(team => {
        const div = document.createElement("div");
        div.className = "p-2 border-b border-gray-700";
        div.innerText = `${team.name} — ₹${team.budget_remaining}`;
        container.appendChild(div);
    });
}

function render() {
    renderHeader();
    renderTimer();
    renderLeaderboard();
}

// ============================
// FULL STATE LOAD
// ============================

async function loadFullState() {
    log("Loading full state...");
    const response = await fetch("/api/auction/full-state");
    if (!response.ok) {
        log("Full state fetch failed");
        return;
    }

    const data = await response.json();

    appState.currentPlayer = data.current_player;
    appState.highestBid = data.current_highest_bid;
    appState.highestTeam = data.current_highest_team;
    appState.status = data.status;
    appState.teams = data.teams;

    render();
}

// ============================
// EVENT HANDLER
// ============================

function handleEvent(data) {
    log("Event received:", data);

    switch (data.event) {

        case "PLAYER_LOADED":
            loadFullState();
            break;

        case "BIDDING_STARTED":
            appState.status = "OPEN";
            renderTimer();
            break;

        case "NEW_BID":
            appState.highestBid = data.amount;
            appState.highestTeam = {
                id: data.team_id,
                name: data.team_name
            };
            renderHeader();
            break;

        case "COUNTDOWN_TICK":
            appState.status = data.seconds + "s";
            renderTimer();
            break;

        case "COUNTDOWN_CANCELLED":
            appState.status = "OPEN";
            renderTimer();
            break;

        case "BIDDING_EXTENDED":
            appState.status = "EXTENDED";
            renderTimer();
            break;

        case "BIDDING_CLOSED":
            loadFullState();
            break;
    }
}

// ============================
// WEBSOCKET
// ============================

function initWebSocket() {
    log("Connecting WebSocket...");
    socket = new WebSocket(`ws://${window.location.host}/ws`);

    socket.onmessage = function (event) {
        const data = JSON.parse(event.data);
        handleEvent(data);
    };

    socket.onerror = function (err) {
        log("WebSocket error:", err);
    };
}

// ============================
// INIT
// ============================

document.addEventListener("DOMContentLoaded", function () {
    loadFullState();
    initWebSocket();
});
