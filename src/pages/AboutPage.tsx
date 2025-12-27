import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

export function AboutPage() {
  const { currentUser, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <div className="flex items-center space-x-8">
              <span className="text-xl font-semibold text-gray-800">
                Auth Demo
              </span>
              <div className="flex space-x-4">
                <Link
                  to="/home"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Home
                </Link>
                <Link
                  to="/about"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  About Us
                </Link>
                <Link
                  to="/test-generator"
                  className="text-gray-600 hover:text-gray-900 px-3 py-2 rounded-md text-sm font-medium"
                >
                  Test Generator
                </Link>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-600">
                Logged in as: {currentUser}
              </span>
              <button
                onClick={handleLogout}
                type="button"
                className="bg-red-600 text-white py-2 px-4 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2 transition-colors text-sm"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
        <div className="bg-white rounded-lg shadow-md p-8">
          <h1 className="text-3xl font-bold text-gray-800 mb-6">About Us</h1>

          <div className="prose prose-gray max-w-none">
            <p className="text-gray-600 mb-4">
              This is a demo application showcasing a simple authentication
              system built with React 18, Vite, TypeScript, and Tailwind CSS.
            </p>

            <h2 className="text-xl font-semibold text-gray-800 mt-6 mb-3">
              Features
            </h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>User login with credential validation</li>
              <li>Account registration with validation</li>
              <li>Password reset functionality</li>
              <li>Protected routes requiring authentication</li>
              <li>Local storage-based user database</li>
              <li>Session persistence across page refreshes</li>
            </ul>

            <h2 className="text-xl font-semibold text-gray-800 mt-6 mb-3">
              Technology Stack
            </h2>
            <ul className="list-disc list-inside text-gray-600 space-y-2">
              <li>React 18</li>
              <li>TypeScript</li>
              <li>Vite</li>
              <li>React Router v6</li>
              <li>Tailwind CSS</li>
            </ul>
          </div>

          <div className="mt-8">
            <Link
              to="/home"
              className="text-blue-600 hover:text-blue-800 hover:underline"
            >
              ← Back to Home
            </Link>
          </div>
        </div>
      </main>
    </div>
  );
}
