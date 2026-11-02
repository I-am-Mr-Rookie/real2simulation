// Presentation only: Clerk widget styling that mirrors the --r2s-* tokens. No auth behaviour or config.
export const clerkAppearance = {
  variables: {
    // Clerk 7 uses Foreground/Input, not the removed colorText/colorInputBackground keys.
    colorPrimary: 'var(--r2s-accent)', colorPrimaryForeground: 'var(--r2s-accent-ink)',
    colorForeground: 'var(--r2s-ink)', colorMutedForeground: 'var(--r2s-muted)',
    colorBackground: 'var(--r2s-surface)', colorMuted: 'var(--r2s-surface)',
    colorInput: 'var(--r2s-surface)', colorInputForeground: 'var(--r2s-ink)',
    colorNeutral: 'var(--r2s-ink)', colorBorder: 'var(--r2s-border-strong)',
    colorDanger: 'var(--r2s-danger)', colorSuccess: 'var(--r2s-ok)', colorWarning: 'var(--r2s-warn)',
    colorRing: 'var(--r2s-focus)',
    fontFamily: 'var(--r2s-font-sans)', borderRadius: '6px'
  },
  elements: {
    card: { borderWidth: '1.5px', borderStyle: 'solid', borderColor: 'var(--r2s-ink)', boxShadow: 'var(--r2s-shadow)' },
    // Clerk's variant rules reset border-width to zero after base element styles.
    socialButtonsBlockButton: { color: 'var(--r2s-ink)', borderWidth: '1px !important', borderStyle: 'solid', borderColor: 'var(--r2s-border-strong)' },
    socialButtonsBlockButtonText: { color: 'var(--r2s-ink)' },
    formFieldInput: { borderWidth: '1px !important', borderStyle: 'solid', borderColor: 'var(--r2s-border-strong)', '&::placeholder': { color: 'var(--r2s-muted)', opacity: 1 } },
    dividerLine: { backgroundColor: 'var(--r2s-border-strong)' },
    formButtonPrimary: { borderWidth: '1.5px', borderStyle: 'solid', borderColor: 'var(--r2s-ink)', boxShadow: 'var(--r2s-shadow-sm)', backgroundImage: 'none' }
  }
};
