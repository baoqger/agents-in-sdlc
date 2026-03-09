<!--
  HighContrastToggle.svelte
  A toggle button component that enables/disables high contrast mode.
  The user's preference is persisted in localStorage so it is restored
  across page loads.
-->
<script lang="ts">
    /** Whether high contrast mode is currently active. */
    let isHighContrast = $state(false);

    /**
     * Apply or remove the 'high-contrast' class on <html> and sync the
     * current state with localStorage.
     */
    const applyHighContrast = (enabled: boolean): void => {
        if (enabled) {
            document.documentElement.classList.add('high-contrast');
        } else {
            document.documentElement.classList.remove('high-contrast');
        }
    };

    /** Toggle high contrast mode and persist the preference. */
    const toggleHighContrast = (): void => {
        isHighContrast = !isHighContrast;
        localStorage.setItem('highContrast', String(isHighContrast));
        applyHighContrast(isHighContrast);
    };

    /** Read the stored preference from localStorage on mount. */
    $effect(() => {
        const stored = localStorage.getItem('highContrast');
        isHighContrast = stored === 'true';
        // The inline script in Layout.astro already applies the class before first paint.
        // Only update the DOM if the current class state doesn't match the stored preference,
        // to avoid unnecessary DOM mutations.
        const classApplied = document.documentElement.classList.contains('high-contrast');
        if (isHighContrast !== classApplied) {
            applyHighContrast(isHighContrast);
        }
    });
</script>

<button
    data-testid="high-contrast-toggle"
    onclick={toggleHighContrast}
    aria-pressed={isHighContrast}
    aria-label={isHighContrast ? 'Disable high contrast mode' : 'Enable high contrast mode'}
    class="flex items-center gap-2 px-3 py-1.5 rounded-lg border border-white/40 hover:bg-white/10 transition-colors duration-200 text-sm font-medium focus:outline-none focus:ring-2 focus:ring-white focus:ring-offset-1 focus:ring-offset-blue-700"
    title={isHighContrast ? 'Switch to normal mode' : 'Switch to high contrast mode'}
>
    <!-- Half-filled circle icon representing contrast -->
    <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-4 w-4"
        viewBox="0 0 24 24"
        fill="currentColor"
        aria-hidden="true"
    >
        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-1 17.93c-3.95-.49-7-3.85-7-7.93 0-4.08 3.05-7.44 7-7.93v15.86z"/>
    </svg>
    <span>{isHighContrast ? 'Normal Mode' : 'High Contrast'}</span>
</button>
