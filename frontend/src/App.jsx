import { useEffect, useState } from "react";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from "./firebase";

import ConfigPage from "./pages/ConfigPage";
import WorkspacePage from "./pages/WorkspacePage";
import ChatPage from "./pages/chat";
import LoginPage from "./pages/LoginPage";

export default function App() {
  const [user, setUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  const [page, setPage] = useState("config");
  const [dbConfig, setDbConfig] = useState(null);
  const [metadata, setMetadata] = useState(null);

  /* ---------------- AUTH LISTENER ---------------- */
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      setUser(u);
      setLoadingAuth(false);
    });

    return () => unsub();
  }, []);

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

  async function handleLogout() {
    await signOut(auth);
    setPage("config");
  }

  /* ---------------- WAIT FOR AUTH ---------------- */
  if (loadingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  /* ---------------- NOT LOGGED IN ---------------- */
  if (!user) {
    return <LoginPage />;
  }

  /* ---------------- APP ---------------- */
  return (
    <>
      {page === "config" && <ConfigPage onConnected={handleConnected} />}

      {page === "workspace" && (
        <WorkspacePage
          dbConfig={dbConfig}
          metadata={metadata}
          onExit={handleLogout}   // 🔐 logout
          onGoChat={() => setPage("chat")}
        />
      )}

      {page === "chat" && (
        <ChatPage
          dbConfig={dbConfig}
          onExit={() => setPage("workspace")}
        />
      )}
    </>
  );
}
