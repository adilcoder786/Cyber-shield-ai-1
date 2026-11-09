import { Routes, Route } from "react-router-dom";
import Sidebar from "./components/Sidebar";
import MobileNav from "./components/MobileNav";
import Dashboard from "./pages/Dashboard";
import UrlScanner from "./pages/UrlScanner";
import MessageAnalyzer from "./pages/MessageAnalyzer";
import FileAnalyzer from "./pages/FileAnalyzer";
import History from "./pages/History";

export default function App() {
  return (
    <div className="flex min-h-screen bg-ink">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0 pb-16 md:pb-0">
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/url-scanner" element={<UrlScanner />} />
          <Route path="/message-analyzer" element={<MessageAnalyzer />} />
          <Route path="/file-analyzer" element={<FileAnalyzer />} />
          <Route path="/history" element={<History />} />
        </Routes>
      </div>
      <MobileNav />
    </div>
  );
}
