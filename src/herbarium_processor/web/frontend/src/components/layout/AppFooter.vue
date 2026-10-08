<template>
  <footer class="bg-slate-900 text-slate-200">
    <div class="max-w-4xl mx-4 md:mx-auto my-12 grid gap-8 md:grid-cols-2 md:px-4">
      <!-- Left: Open source + version -->
      <div>
        <p class="text-sm text-slate-400 max-w-xs">
          Parsely Studio is made with ❤️ in Oakland, CA and built to make
          specimen digitization faster for everyone.
        </p>

        <!-- GitHub link -->
        <div class="mt-4">
          <a
            href="https://github.com/danielleward12/parsely_studio"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-flex items-center gap-2 text-sm text-emerald-400 hover:text-emerald-300"
          >
            <svg
              xmlns="http://www.w3.org/2000/svg"
              viewBox="0 0 16 16"
              fill="currentColor"
              class="w-4 h-4"
            >
              <path
                d="M8 0C3.58 0 0 3.58 0 8a8 8 0 005.47 7.59c.4.07.55-.17.55-.38
            0-.19-.01-.82-.01-1.49-2 .37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52
            0-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95
            0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82a7.56 7.56 0 012-.27c.68 0
            1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82
            2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01
            2.2 0 .21.15.46.55.38A8.01 8.01 0 0016 8c0-4.42-3.58-8-8-8z"
              />
            </svg>
            View the GitHub repo
          </a>
        </div>
        <p class="mt-6 text-sm text-slate-500">
          © {{ year }} Parsely Project. All rights reserved.
        </p>
      </div>

      <!-- Middle: Site links -->
      <div>
        <h4
          class="text-sm font-semibold uppercase tracking-wide text-slate-300"
        >
          Explore
        </h4>
        <ul class="mt-3 space-y-2 text-sm">
          <li>
            <a
              href="/how-it-works"
              class="hover:text-white"
            >How it works</a>
          </li>
          <li>
            <a
              href="/about"
              class="hover:text-white"
            >Our mission</a>
          </li>
          <li>
            <a
              href="/"
              class="hover:text-white"
            >Upload specimens</a>
          </li>
        </ul>
      </div>
    </div>
  </footer>
</template>
<script setup>
const year = new Date().getFullYear();
</script>
