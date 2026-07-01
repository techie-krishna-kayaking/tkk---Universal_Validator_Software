import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.tkkvalidator.app',
  appName: 'TKK Universal Validator',
  webDir: '../frontend/dist',
  server: {
    androidScheme: 'https',
  },
  plugins: {
    SplashScreen: {
      launchShowDuration: 0,
      backgroundColor: '#1a1a2e',
    },
  },
};

export default config;
