import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { AuthProvider, useAuth } from '../context/AuthContext';
import React from 'react';

function RoleProbe() {
  const { user, isAuthenticated, setRole, login } = useAuth();
  return (
    <>
      <span data-testid="authenticated">{String(isAuthenticated)}</span>
      <span data-testid="role">{user?.role ?? ""}</span>
      <span data-testid="email">{user?.email ?? ""}</span>
      <button onClick={() => login('architect', 'Architect@123')}>Login Architect</button>
      <button onClick={() => setRole('viewer')}>Set Viewer</button>
    </>
  );
}

describe('AuthContext', () => {
  it('starts unauthenticated before login', () => {
    render(
      <AuthProvider>
        <RoleProbe />
      </AuthProvider>
    );
    expect(screen.getByTestId('authenticated')).toHaveTextContent('false');
    expect(screen.getByTestId('role')).toHaveTextContent('');
  });

  it('logs in with predefined credentials and updates role', async () => {
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <RoleProbe />
      </AuthProvider>
    );

    await user.click(screen.getByRole('button', { name: /login architect/i }));
    expect(screen.getByTestId('authenticated')).toHaveTextContent('true');
    expect(screen.getByTestId('email')).toHaveTextContent('architect@tkkvalidator.local');

    await user.click(screen.getByRole('button', { name: /set viewer/i }));
    expect(screen.getByTestId('role')).toHaveTextContent('viewer');
  });
});
