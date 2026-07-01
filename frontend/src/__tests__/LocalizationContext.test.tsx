import { render, screen, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { describe, expect, it } from 'vitest';
import {
  LocalizationProvider,
  useLocalization,
} from '../../context/LocalizationContext';
import React from 'react';

function TranslationProbe({ translationKey }: { translationKey: string }) {
  const { t, locale } = useLocalization();
  return (
    <>
      <span data-testid="value">{t(translationKey as Parameters<typeof t>[0])}</span>
      <span data-testid="locale">{locale}</span>
    </>
  );
}

function LocaleSwitcher() {
  const { setLocale } = useLocalization();
  return (
    <button onClick={() => setLocale('es')}>Switch to ES</button>
  );
}

describe('LocalizationContext', () => {
  it('renders English translations by default', () => {
    render(
      <LocalizationProvider>
        <TranslationProbe translationKey="nav.dashboard" />
      </LocalizationProvider>
    );
    expect(screen.getByTestId('value')).toHaveTextContent('Dashboard');
    expect(screen.getByTestId('locale')).toHaveTextContent('en');
  });

  it('switches locale to Spanish when setLocale is called', async () => {
    const user = userEvent.setup();
    render(
      <LocalizationProvider>
        <LocaleSwitcher />
        <TranslationProbe translationKey="nav.dashboard" />
      </LocalizationProvider>
    );
    await user.click(screen.getByRole('button', { name: /switch to es/i }));
    expect(screen.getByTestId('value')).toHaveTextContent('Panel');
    expect(screen.getByTestId('locale')).toHaveTextContent('es');
  });

  it('returns known keys for all standard nav entries', () => {
    const keys = [
      'nav.dashboard',
      'nav.validations',
      'nav.projects',
      'nav.reports',
      'nav.connections',
      'nav.settings',
      'nav.admin',
    ] as const;

    function AllKeys() {
      const { t } = useLocalization();
      return (
        <ul>
          {keys.map((k) => (
            <li key={k} data-testid={k}>{t(k)}</li>
          ))}
        </ul>
      );
    }

    render(<LocalizationProvider><AllKeys /></LocalizationProvider>);
    expect(screen.getByTestId('nav.dashboard')).toHaveTextContent('Dashboard');
    expect(screen.getByTestId('nav.validations')).toHaveTextContent('Validations');
    expect(screen.getByTestId('nav.admin')).toHaveTextContent('Administration');
  });
});
