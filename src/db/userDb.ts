/**
 * User type definition
 */
export interface User {
  username: string;
  password: string;
}

const USERS_STORAGE_KEY = 'auth_demo_users';

/**
 * Safely parse users from localStorage
 */
function parseUsers(data: string | null): User[] {
  if (!data) {
    return [];
  }
  try {
    const parsed = JSON.parse(data);
    if (Array.isArray(parsed)) {
      return parsed;
    }
    return [];
  } catch {
    return [];
  }
}

/**
 * Initialize the database with default admin user if no users exist
 */
function initializeDb(): void {
  const existingUsers = localStorage.getItem(USERS_STORAGE_KEY);
  const users = parseUsers(existingUsers);
  
  // Only seed if no users exist at all
  if (users.length === 0) {
    const defaultUsers: User[] = [{ username: 'admin', password: 'admin' }];
    localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(defaultUsers));
  }
}

// Initialize on module load
initializeDb();

/**
 * Get all users from the database
 */
export function getUsers(): User[] {
  const users = localStorage.getItem(USERS_STORAGE_KEY);
  return parseUsers(users);
}

/**
 * Get a single user by username
 */
export function getUser(username: string): User | undefined {
  const users = getUsers();
  return users.find((u) => u.username.toLowerCase() === username.toLowerCase());
}

/**
 * Create a new user in the database
 * Returns true if successful, false if username already exists
 */
export function createUser(user: User): boolean {
  const users = getUsers();
  const exists = users.some(
    (u) => u.username.toLowerCase() === user.username.toLowerCase()
  );

  if (exists) {
    return false;
  }

  users.push(user);
  localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(users));
  return true;
}

/**
 * Update password for an existing user
 * Returns true if successful, false if user not found
 */
export function updatePassword(username: string, newPassword: string): boolean {
  const users = getUsers();
  const userIndex = users.findIndex(
    (u) => u.username.toLowerCase() === username.toLowerCase()
  );

  if (userIndex === -1) {
    return false;
  }

  // Create a new array with updated user to ensure immutability
  const updatedUsers = users.map((user, index) => 
    index === userIndex ? { ...user, password: newPassword } : user
  );
  
  localStorage.setItem(USERS_STORAGE_KEY, JSON.stringify(updatedUsers));
  
  // Verify the update was successful by re-reading
  const verifyUsers = getUsers();
  const updatedUser = verifyUsers.find(
    (u) => u.username.toLowerCase() === username.toLowerCase()
  );
  
  return updatedUser?.password === newPassword;
}

/**
 * Validate user credentials
 * Returns true if username and password match
 */
export function validateCredentials(
  username: string,
  password: string
): boolean {
  const user = getUser(username);
  return user !== undefined && user.password === password;
}

/**
 * Generate a random temporary password (10-12 characters)
 */
export function generateTemporaryPassword(): string {
  const chars =
    'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789';
  const length = Math.floor(Math.random() * 3) + 10; // 10-12 characters
  let password = '';
  for (let i = 0; i < length; i++) {
    password += chars.charAt(Math.floor(Math.random() * chars.length));
  }
  return password;
}
