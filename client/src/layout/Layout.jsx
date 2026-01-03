import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

function Layout({ children, monitoring }) {
  return (
    <div className="min-h-screen bg-pink-10">

      {/* Sidebar (fixed) */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="ml-56 flex flex-col min-h-screen">

        {/* Topbar */}
        <Topbar monitoring={monitoring} />

        {/* Scrollable Content */}
        <main className="flex-1 overflow-y-auto p-4">
          {children}
        </main>

      </div>
    </div>
  );
}

export default Layout;
