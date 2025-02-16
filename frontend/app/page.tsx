"use client";

import { useState, useEffect } from "react";

export default function Home() {
  const [inputValue, setInputValue] = useState("");
  const [response, setResponse] = useState("");
  const [user, setUser] = useState<{ id: number; name: string }>({ id: -1, name: "unknown user" });
  const [conversation, setConversation] = useState<{ query: string; response: string }[]>([]);

  const getUser = async () => {
    const res = await fetch("/api/user");
    const data = await res.json();
    setUser(data);
  };

  const getConversation = async (userId: number) => {
    const res = await fetch(`/api/get_conversation?user=${userId}`);
    const data = await res.json();
    setConversation(data);
  };

  useEffect(() => {
    getUser().then(() => {
      if (user.id !== -1) {
        getConversation(user.id);
      }
    });
  }, [user.id]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    const res = await fetch("/api/query", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ user_id: user.id, query_input: inputValue }),
    });

    const data = await res.json();
    setResponse(data.response);

    setConversation((prev) => [...prev, { query: inputValue, response: data.response }]);
    setInputValue("");
  };

  return (
    <main className="flex flex-col items-center p-10">
      <h1 className="text-4xl font-bold font-sans">
        Hello, {user.name}! Welcome to the Coolest Bot Ever Made!
      </h1>

    <div className="mt-4 w-3/4">
      {conversation.map((entry, index) => (
        <div key={index} className="mb-4">
          <p className="w-full"><strong>{user.name}:</strong> {entry.query}</p>
          <p className="w-full"><strong>Coolest Bot Ever:</strong> {entry.response}</p>
        </div>
      ))}
    </div>

    <form onSubmit={handleSubmit} className="flex flex-col items-center w-3/4">
      <div className="flex flex-row items-center mb-4 w-full">
        <input
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          placeholder="Enter text"
          className="p-2 border text-black flex-grow"
          required
        />
        <button type="submit" className="p-2 bg-blue-500 text-white ml-2">
          Send
        </button>
      </div>
    </form>
    </main>
  );
}