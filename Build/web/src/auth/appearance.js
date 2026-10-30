// Presentation only: Clerk widget styling that mirrors the --r2s-* tokens. No auth behaviour or config.
export const clerkAppearance = {
  variables: {
    colorPrimary: '#b23a0e', colorText: '#1c1a16', colorTextSecondary: '#5a554b',
    colorBackground: '#fffcf5', colorInputBackground: '#fffcf5', colorInputText: '#1c1a16',
    fontFamily: 'var(--r2s-font-sans)', borderRadius: '6px'
  },
  elements: {
    card: { border: '1.5px solid #1c1a16', boxShadow: '4px 4px 0 #1c1a16' },
    formButtonPrimary: { border: '1.5px solid #1c1a16', boxShadow: '2px 2px 0 #1c1a16' }
  }
};
