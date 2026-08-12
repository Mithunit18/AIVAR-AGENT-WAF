import { useState, useEffect, useRef } from 'react';

export function useSSE(url) {
  const [events, setEvents] = useState([]);
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef(null);

  useEffect(() => {
    let retryCount = 0;
    
    const connect = () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
      
      const eventSource = new EventSource(url);
      eventSourceRef.current = eventSource;

      eventSource.onopen = () => {
        setIsConnected(true);
        retryCount = 0;
      };
      
      eventSource.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type !== 'ping') {
            setEvents((prev) => {
              // Deduplicate slightly by event_id
              if (prev.some(e => e.event_id === data.event_id)) return prev;
              return [data, ...prev].slice(0, 100);
            });
          }
        } catch (e) {
          console.error("Error parsing SSE data", e);
        }
      };

      eventSource.onerror = () => {
        setIsConnected(false);
        eventSource.close();
        
        // Exponential backoff reconnect
        const timeout = Math.min(10000, 1000 * Math.pow(2, retryCount));
        retryCount++;
        setTimeout(connect, timeout);
      };
    };

    connect();

    return () => {
      if (eventSourceRef.current) {
        eventSourceRef.current.close();
      }
    };
  }, [url]);

  return { events, isConnected, setEvents };
}
