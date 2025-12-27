import { useState, FormEvent } from 'react';
import { Link } from 'react-router-dom';
import { getUser, updatePassword, generateTemporaryPassword } from '../db/userDb';

export function ForgotPasswordPage() {
  const [username, setUsername] = useState('');
  const [error, setError] = useState('');
  const [tempPassword, setTempPassword] = useState('');

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    setError('');
    setTempPassword('');

    if (!username.trim()) {
      setError('Please enter your username');
      return;
    }

    const user = getUser(username);

    if (!user) {
      setError('User not found');
      return;
    }

    // Generate and store temporary password
    const newTempPassword = generateTemporaryPassword();
    const updated = updatePassword(username, newTempPassword);

    if (updated) {
      setTempPassword(newTempPassword);
    } else {
      setError('Failed to generate temporary password. Please try again.');
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-100">
      <div className="bg-white p-8 rounded-lg shadow-md w-full max-w-md">
        <h1 className="text-2xl font-bold text-center mb-6 text-gray-800">
          Forgot Password
        </h1>

        {error && (
          <div
            className="mb-4 p-3 bg-red-100 border border-red-400 text-red-700 rounded"
            role="alert"
          >
            {error}
          </div>
        )}

        {tempPassword && (
          <div
            className="mb-4 p-3 bg-green-100 border border-green-400 text-green-700 rounded"
            role="alert"
          >
            <p className="font-medium">Temporary password generated:</p>
            <p className="mt-1 font-mono text-lg break-all">{tempPassword}</p>
            <p className="mt-2 text-sm">
              Please use this password to login and change it immediately.
            </p>
          </div>
        )}

        <form onSubmit={handleSubmit} noValidate>
          <div className="mb-6">
            <label
              htmlFor="username"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoComplete="username"
              required
            />
          </div>

          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 transition-colors"
          >
            Reset Password
          </button>
        </form>

        <div className="mt-6 text-center">
          <Link
            to="/"
            className="text-blue-600 hover:text-blue-800 hover:underline"
          >
            Back to Login
          </Link>
        </div>
      </div>
    </div>
  );
}
