// get api key from .env

const API_KEY = process.env.NEXT_PUBLIC_PERSONA_API_KEY;

async function createConversation() {
  return fetch("/api/conversations", {
    method: "POST",
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  }).then((res) => res.json());
}

async function listConversations() {
  return fetch("/api/conversations", {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  }).then((res) => res.json());
}

async function listMessages(conversationId: string) {
  return fetch(`/api/conversations/${conversationId}/messages`, {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  }).then((res) =>
    res.json()
  );
}

async function listMemories() {
  return fetch("/api/memories", {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  }).then((res) => res.json());
}

async function getMemory(memoryId: string) {
  return fetch(`/api/memories/${memoryId}`, {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  }).then((res) => res.json());
}

async function getRetrievals(memoryId: string) {
  return fetch(`/api/memories/${memoryId}/retrievals`, {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  }).then((res) => res.json());
}

async function stats() {
  return fetch("/api/stats", {
    headers: {
      "Authorization": `Bearer ${API_KEY}`
    }
  }).then((res) => res.json());
}

export const api = {
  createConversation,
  listConversations,
    listMessages,
    listMemories,
    getMemory,
    getRetrievals,
    stats,
};

