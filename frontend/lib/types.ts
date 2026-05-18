const types = ['MemoryType', 'Memory', 'Conversation', 'Message', 'Stats', 'ChatDone']
export type MemoryType = {
  id: string;
  name: string;
  description: string;
};

export type Memory = {
  id: string;
  typeId: string;
  content: string;
  timestamp: number;
};

export type Conversation = {
  id: string;
  memoryId: string;
  messages: Message[];
};

export type Message = {
  id: string;
  conversationId: string;
  content: string;
  sender: 'user' | 'system';
  timestamp: number;
};

export type Stats = {
  totalMemories: number;
  totalConversations: number;
  totalMessages: number;
};

export type ChatDone = {
  id: string;
  conversationId: string;
  timestamp: number;
};
