API_KEY = process.env.NEXT_PUBLIC_PERSONA_API_KEY || "";

function streamChat(conversatonId, message, handlers, signal?) {
  const eventSource = new EventSource(`/api/chat/stream?conversationId=${conversatonId}&message=${encodeURIComponent(message)}`);
    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);
        if (data.type === 'message') {
            handlers.onMessage?.(data.message);
        } else if (data.type === 'done') {
            handlers.onDone?.();
            eventSource.close();
        } else if (data.type === 'error') {
            handlers.onError?.(data.error);
            eventSource.close();
        } else {
            console.warn('Unknown event type:', data.type);
        } 
    };
    eventSource.onerror = (err) => {
        handlers.onError?.(err);
        eventSource.close();
    };
    signal?.addEventListener('abort', () => {
        eventSource.close();
    });
    return () => {
        eventSource.close();
    };
}

export { streamChat };
