import { NavLink } from "react-router-dom";
import {
  MdDashboard,
  MdListAlt,
  MdAnalytics,
  MdModelTraining,
  MdSettings,
} from "react-icons/md";

function Sidebar() {
  const linkClass = ({ isActive }) =>
    `flex items-center gap-3 px-3 py-2 rounded-lg transition ${
      isActive
        ? "bg-pink-200 text-pink-700 font-semibold"
        : "text-gray-700 hover:bg-pink-50 hover:text-pink-700"
    }`;

  return (
    <aside className="fixed left-0 top-0 h-screen w-56 bg-pink-50 p-4 flex flex-col border-r border-pink-100 z-50">

      {/* Logo */}
      <h2 className="text-xl font-bold text-pink-600 mb-6 ml-3">
        ML-NIDS
      </h2>

      {/* Navigation */}
      <nav className="space-y-1 ml-1 text-sm">
        <NavLink to="/" className={linkClass}>
          <MdDashboard size={18} />
          Dashboard
        </NavLink>

        <NavLink to="/logs" className={linkClass}>
          <MdListAlt size={18} />
          Logs
        </NavLink>

        <NavLink to="/stats" className={linkClass}>
          <MdAnalytics size={18} />
          Stats
        </NavLink>

        <NavLink to="/models" className={linkClass}>
          <MdModelTraining size={18} />
          Models
        </NavLink>

        <NavLink to="/settings" className={linkClass}>
          <MdSettings size={18} />
          Settings
        </NavLink>
      </nav>

      {/* Footer */}
      <div className="mt-auto text-xs text-gray-500 ml-3">
        © ML-NIDS | Manoj Thamke & Team
      </div>
    </aside>
  );
}

export default Sidebar;
