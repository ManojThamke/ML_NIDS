import React, { useState } from "react";
import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

/**
 * Global Layout (V4.5)
 * Controls the structural grid and theme propagation across the NIDS.
 */
function Layout({ children, monitoring, setMonitoring }) {
  // 🔹 Central Theme State: 'light' | 'dark' | 'contrast'
  const [theme, setTheme] = useState('light');

  // 🔹 Theme-based Background Logic
  const getPageBg = () => {
    switch (theme) {
      case 'dark': return "bg-slate-950 text-slate-100";
      case 'contrast': return "bg-black text-white";
      default: return "bg-gray-50/50 text-slate-900"; // Light
    }
  };

  return (
    <div className={`min-h-screen transition-colors duration-500 ${getPageBg()}`}>

      {/* 1. Sidebar (Fixed) - Pass theme to sync colors */}
      <Sidebar theme={theme} setTheme={setTheme} />

      {/* 2. Main Content Area */}
      <div className="ml-64 flex flex-col min-h-screen">

        {/* 🔒 STICKY TOPBAR - Centrally managed control */}
        <div className="sticky top-0 z-[1000]">
          <Topbar 
            monitoring={monitoring} 
            setMonitoring={setMonitoring} 
            theme={theme} 
          />
        </div>

        {/* 3. Scrollable Content Area */}
        <main className="flex-1 p-6 lg:p-8 animate-fade-in overflow-visible">
          {/* Clone children to pass theme prop automatically to Dashboard 
             or use a Context Provider if your app grows larger.
          */}
          {React.Children.map(children, child => {
            if (React.isValidElement(child)) {
              return React.cloneElement(child, { theme });
            }
            return child;
          })}
        </main>

        {/* 4. Forensic Footer Hint */}
        <footer className={`px-8 py-4 border-t text-[10px] font-black uppercase tracking-[0.3em] opacity-30 ${
          theme === 'dark' ? 'border-slate-800' : 'border-gray-100'
        }`}>
          NIDS Forensic Engine // Status: Encrypted // Node: Primary_Alpha
        </footer>

      </div>
    </div>
  );
}

export default Layout;