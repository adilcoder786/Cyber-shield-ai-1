import React from "react";
import { ShieldAlert, RotateCcw } from "lucide-react";

export default class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { error: null };
  }

  static getDerivedStateFromError(error) {
    return { error };
  }

  componentDidCatch(error, info) {
    // Surface the real error in the console so it's easy to debug during dev/demo.
    console.error("CyberShield AI crashed:", error, info?.componentStack);
  }

  render() {
    if (this.state.error) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-ink px-6">
          <div className="panel max-w-md w-full p-6 text-center space-y-3">
            <ShieldAlert className="h-8 w-8 text-verdict-malicious mx-auto" />
            <p className="font-display text-lg font-semibold text-ash-50">Something went wrong</p>
            <p className="text-sm text-ash-400">
              The interface hit an unexpected error. This is usually caused by the backend API
              being unreachable. Check that it's running and that{" "}
              <code className="font-mono text-ash-300">VITE_API_URL</code> in{" "}
              <code className="font-mono text-ash-300">frontend/.env</code> points to it, then reload.
            </p>
            <pre className="text-left text-[11px] text-ash-600 bg-ink-raised rounded-md p-3 overflow-auto max-h-32">
              {String(this.state.error?.message || this.state.error)}
            </pre>
            <button
              onClick={() => window.location.reload()}
              className="inline-flex items-center gap-2 rounded-md bg-signal px-4 py-2 text-sm font-medium text-ink hover:bg-signal-soft transition-colors"
            >
              <RotateCcw className="h-3.5 w-3.5" /> Reload
            </button>
          </div>
        </div>
      );
    }
    return this.props.children;
  }
}
