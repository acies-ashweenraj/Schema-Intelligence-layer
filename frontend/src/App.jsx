import { useEffect, useState } from "react";
import { onAuthStateChanged, signOut } from "firebase/auth";
import { auth } from "./firebase";

import ConfigPage from "./pages/ConfigPage";
import WorkspacePage from "./pages/WorkspacePage";
import LoginPage from "./pages/LoginPage";

const METADATA_KEY = "metadata_state_v1";

export default function App() {
  const [user, setUser] = useState(null);
  const [loadingAuth, setLoadingAuth] = useState(true);

  const [page, setPage] = useState("config");
  const [dbConfig, setDbConfig] = useState(null);
  const [metadata, setMetadata] = useState(null);

  /* ================= AUTH LISTENER ================= */
  useEffect(() => {
    const unsub = onAuthStateChanged(auth, (u) => {
      if (!u) {
        // 🔥 AUTH BOUNDARY RESET
        resetWorkspace();
        setUser(null);
        setPage("config");
      } else {
        setUser(u);
      }

      setLoadingAuth(false);
    });

    return () => unsub();
  }, []);

  /* ================= WORKSPACE RESET ================= */
  function resetWorkspace() {
    sessionStorage.removeItem(METADATA_KEY);
    setDbConfig(null);
    setMetadata(null);
  }

  /* ================= PAGE TRANSITION WATCHER ================= */
  useEffect(() => {
    if (page === "config") {
      // 🔥 CONFIG PAGE = NEW WORKSPACE
      resetWorkspace();
    }
  }, [page]);

  /* ================= CONNECT ================= */
  function handleConnected(cfg, meta) {
    setDbConfig(cfg);
    setMetadata(meta);
    setPage("workspace");
  }

  /* ================= LOGOUT ================= */
  async function handleLogout() {
    resetWorkspace();
    await signOut(auth);
    setPage("config");
  }

  /* ================= UI ================= */
  if (loadingAuth) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        Loading...
      </div>
    );
  }

  if (!user) {
    return <LoginPage />;
  }

  return (
    <>
      {page === "config" && (
        <ConfigPage
          onConnected={handleConnected}
          onExit={handleLogout}
        />
      )}

      {page === "workspace" && (
        <WorkspacePage
          key="workspace"
          dbConfig={dbConfig}
          metadata={metadata}
          onExit={handleLogout}
        />
      )}
    </>
  );
}
