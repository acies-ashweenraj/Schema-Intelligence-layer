import { useState } from "react";
import ConfigPage from "./pages/ConfigPage";
import WorkspacePage from "./pages/WorkspacePage";
import ChatPage from "./pages/chat";

export default function App() {
  const [page, setPage] = useState("config");
  const [dbConfig, setDbConfig] = useState(null);
  const [metadata, setMetadata] = useState(null);

  function handleConnected(cfg, meta) {
    setDbConfig(cfg);
    setMetadata(meta);
    setPage("workspace");
  }

  function handleExit() {
    setPage("config");
    setDbConfig(null);
    setMetadata(null);
  }

  return (
    <>
      {page === "config" && <ConfigPage onConnected={handleConnected} />}
      {page === "workspace" && (
        <WorkspacePage
          dbConfig={dbConfig}
          metadata={metadata}
          onExit={handleExit}
          onGoChat={() => setPage("chat")} // ✅ WORKS
        />
      )}
      {page === "chat" && (
        <ChatPage onExit={() => setPage("workspace")} /> // back button
      )}
    </>
  );
}
