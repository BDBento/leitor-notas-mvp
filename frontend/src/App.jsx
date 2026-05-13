import React from "react";
import { createRoot } from "react-dom/client";

function App() {
  return (
    <main style={{ padding: "40px", fontFamily: "Arial" }}>
      <h1>Leitor de Notas MVP</h1>
      <p>Frontend funcionando com React + Vite.</p>
    </main>
  );
}

createRoot(document.getElementById("root")).render(<App />);