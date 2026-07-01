import { render, screen } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import { AuthProvider, useAuth } from '../../context/AuthContext';
import React from 'react';

function RoleProbe() {
  const { user, setRole } = useAuth();
  return (
    <>
      <span data-testid="role">{user.role}</span>
      <span data-testid="email">{user.email}</span>
      <button onClick={() => setRole('viewer')}>Set Viewer</button>
    </>
  );
}

describe('AuthContext', () => {
  it('provides default demo user with architect role', () => {
    render(
      <AuthProvider>
        <RoleProbe />
      </AuthProvider>
    );
    expect(screen.getByTestId('role')).toHaveTextContent('architect');
    expect(screen.getByTestId('email')).toHaveTextContent('architect@tkkvalidator.local');
  });

  it('updates role when setRole is called', async () => {
    const user = userEvent.setup();
    render(
      <AuthProvider>
        <RoleProbe />
      </AuthProvider>
    );
    await user.click(screen.getByRole('button', { name: /set viewer/i }));
    expect(screen.getByTestId('role')).toHaveTextContent('viewer');
  });
});
