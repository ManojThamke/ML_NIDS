import Sidebar from "../components/Sidebar";
import Topbar from "../components/Topbar";

function Layout({ children, monitoring }) {
  return (
    <div className="min-h-screen flex bg-pink-10">
      
      {/* 🔹 Sidebar (Navigation) */}
      <Sidebar />

      {/* 🔹 Main Content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        
        {/* 🔹 Topbar (Status + Controls) */}
        <Topbar monitoring={monitoring} />

        {/* 🔹 Page Content */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>

      </div>
    </div>
  );
}

export default Layout;
