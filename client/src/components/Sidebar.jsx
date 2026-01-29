import { NavLink } from "react-router-dom";
import { 
  MdDashboard, 
  MdListAlt, 
  MdAnalytics, 
  MdModelTraining, 
  MdSettings,
  MdShield,
  MdWbSunny,
  MdNightlight,
  MdContrast
} from "react-icons/md";

/**
 * Sidebar Component (V4.7)
 * Fix: Scrollbar hidden for a cleaner forensic UI.
 */
function Sidebar({ theme, setTheme }) {
  
  const sidebarStyles = {
    light: "bg-white border-slate-100 text-slate-800",
    dark: "bg-slate-900 border-slate-800 text-slate-100",
    contrast: "bg-black border-white border-r-2 text-white"
  };

  const linkClass = ({ isActive }) => {
    const base = "flex items-center gap-4 px-5 py-3.5 rounded-xl transition-all duration-300 group";
    if (isActive) {
      if (theme === 'contrast') return `${base} bg-white text-black font-black`;
      return `${base} bg-indigo-600 text-white shadow-lg shadow-indigo-500/20 font-bold`;
    }
    const hoverStyle = theme === 'dark' ? "hover:bg-slate-800 hover:text-indigo-400" : "hover:bg-indigo-50 hover:text-indigo-600";
    const textColor = theme === 'dark' ? "text-slate-400" : "text-slate-500";
    return `${base} ${textColor} ${hoverStyle}`;
  };

  return (
    <aside className={`fixed left-0 top-0 h-screen w-64 p-6 flex flex-col z-[1100] transition-colors duration-500 ${sidebarStyles[theme]}`}>

      {/* 🛡️ BRANDING */}
      <div className="flex items-center gap-3 mb-10 px-2 shrink-0">
        <div className={`p-2.5 rounded-xl shadow-lg ${theme === 'contrast' ? 'bg-white text-black' : 'bg-indigo-600 text-white shadow-indigo-500/20'}`}>
          <MdShield size={24} />
        </div>
        <div>
           <h2 className="text-xl font-black tracking-tighter leading-none">ML-NIDS</h2>
           <p className="text-[9px] font-black text-indigo-500 uppercase tracking-widest mt-1.5">Forensic Engine</p>
        </div>
      </div>

      {/* 🛰️ NAVIGATION: Scrollbar Hidden Logic */}
      <div className="flex-1 overflow-y-auto pr-0 scrollbar-hide" style={{ scrollbarWidth: 'none', msOverflowStyle: 'none' }}>
        {/* CSS for Chrome/Safari to hide scrollbar */}
        <style>{`
          .scrollbar-hide::-webkit-scrollbar {
            display: none;
          }
        `}</style>

        <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-3 px-3 opacity-60">Core Operations</p>
        <nav className="space-y-2 mb-8">
          <NavLink to="/" className={linkClass}><MdDashboard size={20} /> Dashboard</NavLink>
          <NavLink to="/logs" className={linkClass}><MdListAlt size={20} /> Traffic Logs</NavLink>
          <NavLink to="/stats" className={linkClass}><MdAnalytics size={20} /> System Stats</NavLink>
        </nav>

        <p className="text-[10px] font-black text-slate-400 uppercase tracking-[0.2em] mb-3 px-3 opacity-60">Management</p>
        <nav className="space-y-2">
          <NavLink to="/models" className={linkClass}><MdModelTraining size={20} /> Ensemble Intelligence</NavLink>
          <NavLink to="/settings" className={linkClass}><MdSettings size={20} /> Control Settings</NavLink>
        </nav>
      </div>

      {/* 🌓 THEME SWITCHER */}
      <div className={`mt-6 p-1.5 rounded-2xl flex items-center gap-1 border shrink-0 ${theme === 'dark' ? 'bg-slate-800 border-slate-700' : 'bg-slate-50 border-slate-100'}`}>
        <button onClick={() => setTheme('light')} className={`flex-1 flex justify-center py-2 rounded-xl transition-all ${theme === 'light' ? 'bg-white shadow-md text-indigo-600' : 'text-slate-400 hover:text-slate-600'}`}><MdWbSunny size={18} /></button>
        <button onClick={() => setTheme('dark')} className={`flex-1 flex justify-center py-2 rounded-xl transition-all ${theme === 'dark' ? 'bg-slate-700 shadow-md text-indigo-400' : 'text-slate-500 hover:text-slate-300'}`}><MdNightlight size={18} /></button>
        <button onClick={() => setTheme('contrast')} className={`flex-1 flex justify-center py-2 rounded-xl transition-all ${theme === 'contrast' ? 'bg-black text-white' : 'text-slate-500'}`}><MdContrast size={18} /></button>
      </div>

      {/* 👤 FOOTER */}
      <div className={`mt-6 pt-6 border-t shrink-0 ${theme === 'dark' ? 'border-slate-800' : 'border-slate-100'}`}>
        <div className={`${theme === 'dark' ? 'bg-slate-800/50' : 'bg-slate-50'} rounded-2xl p-4`}>
          <p className="text-[10px] font-black text-slate-400 uppercase tracking-widest mb-1.5">System Identity</p>
          <p className="text-xs font-bold text-gray-700">Manoj Thamke & Team</p>
          <div className="flex items-center gap-2 mt-3">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span className="text-[9px] font-black text-emerald-600 uppercase tracking-tighter">Telemetry Secure</span>
          </div>
        </div>
      </div>
    </aside>
  );
}

export default Sidebar;