<template>
  <section class="bg-base-100 py-10 sm:py-14">
    <div class="mx-auto max-w-5xl px-5 sm:px-8">
      <div>
        <p class="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.16em] text-emerald-700">
          <Leaf :size="18" aria-hidden="true" />
          Environmental impact
        </p>
        <h1 class="text-4xl font-semibold tracking-tight text-base-content sm:text-5xl">
          What is the environmental impact of using Parsely Studio?
        </h1>
        <p class="mt-5 text-lg leading-relaxed text-base-content/75">
          Herbarium specimens are records of the natural world, and those of us who digitize them tend to care a lot
          about protecting it. Ironically, using AI to automate specimen label digitization relies on data centers that
          consume enormous amounts of energy. We believe that users should have some ability to reduce their impact
          whenever possible by choosing lower energy cost, open models. That's why we offer the choice between two
          modes for Parsely Studio - the
          <strong class="font-bold text-base-content">Default mode</strong> and
          the <strong class="font-bold text-emerald-700">Eco mode</strong>.
        </p>
        <p class="mt-4 text-lg leading-relaxed text-base-content/75">
          The <strong class="font-bold text-base-content">Default mode</strong> uses Gemini 2.5 Pro, which is the original
          model we used to build Parsely Studio. It has the highest historical accuracy for transcribing complex,
          handwritten herbarium labels. The <strong class="font-bold text-emerald-700">Eco mode</strong> uses Qwen 3.8 27B,
          a smaller open-weight model. It generally requires less computing power per request and prioritizes
          transparency compared to closed frontier models like Gemini, Claude, and ChatGPT. Its openness makes its
          energy use more directly measurable and its environmental claims easier to examine.
        </p>
      </div>

      <div v-if="loading" class="mt-10 flex min-h-72 items-center justify-center rounded-2xl border border-base-300 bg-base-200/50">
        <span class="loading loading-spinner loading-md text-primary" aria-label="Loading live carbon data" />
      </div>

      <div v-else-if="error" class="mt-10 rounded-2xl border border-warning/40 bg-warning/10 p-6">
        <h2 class="font-semibold">Live data is temporarily unavailable</h2>
        <p class="mt-2 text-sm text-base-content/75">{{ error }}</p>
        <button class="btn btn-sm btn-outline mt-4" type="button" @click="loadImpact">
          <RefreshCw :size="16" aria-hidden="true" />
          Try again
        </button>
      </div>

      <template v-else-if="comparison">
        <section class="mt-10 grid gap-5 lg:grid-cols-2" aria-label="Model energy comparison">
          <article class="rounded-3xl bg-slate-800 p-6 text-white shadow-lg shadow-slate-900/10 sm:p-7">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xl font-medium text-slate-300">Default mode</p>
                <h2 class="mt-1 text-3xl font-semibold">Gemini 2.5 Pro model</h2>
                <p class="mt-1 text-sm text-slate-300">Estimated using general frontier-model values</p>
              </div>
              <div class="rounded-2xl bg-white/10 p-3 text-white"><Sparkles :size="22" aria-hidden="true" /></div>
            </div>
            <dl class="mt-7 grid grid-cols-2 gap-x-4">
              <div>
                <dt class="text-xs font-medium uppercase tracking-wide text-slate-400">Power</dt>
                <dd class="mt-1 text-2xl font-semibold">{{ formatWatts(comparison.frontierWatts) }}</dd>
              </div>
              <div>
                <dt class="text-xs font-medium uppercase tracking-wide text-slate-400">CO₂ / token</dt>
                <dd class="mt-1 text-2xl font-semibold">{{ formatCarbon(comparison.frontierCarbonPerToken) }}</dd>
              </div>
            </dl>
            <p class="mt-6 border-t border-white/15 pt-4 text-xs leading-relaxed text-slate-300">
              The frontier estimate follows its <a class="underline decoration-slate-400 underline-offset-2 hover:text-white" href="https://carbon-api.nrp-nautilus.io/methodology" target="_blank" rel="noopener noreferrer">published methodology</a>:
              5,400 W idle baseline + 0.5 W per prompt token/s + 6 W per generated token/s.
            </p>
          </article>

          <article class="rounded-3xl bg-gradient-to-br from-emerald-600 to-emerald-800 p-6 text-white shadow-lg shadow-emerald-900/15 sm:p-7">
            <div class="flex items-start justify-between gap-4">
              <div>
                <p class="text-xl font-medium text-emerald-100">Eco mode</p>
                <h2 class="mt-1 text-3xl font-semibold">Qwen 3.8 27B model</h2>
                <p class="mt-1 text-sm text-emerald-100">Measured in real time by National Research Platform</p>
              </div>
              <div class="rounded-2xl bg-white/15 p-3 text-white"><Leaf :size="22" aria-hidden="true" /></div>
            </div>
            <dl class="mt-7 grid grid-cols-2 gap-x-4">
              <div>
                <dt class="text-xs font-medium uppercase tracking-wide text-emerald-100">Power</dt>
                <dd class="mt-1 text-2xl font-semibold">{{ formatWatts(comparison.qwenWatts) }}</dd>
              </div>
              <div>
                <dt class="text-xs font-medium uppercase tracking-wide text-emerald-100">CO₂ / token</dt>
                <dd class="mt-1 text-2xl font-semibold">{{ formatCarbon(comparison.qwenCarbonPerToken) }}</dd>
              </div>
            </dl>
          </article>
        </section>

        <section class="mt-5 rounded-3xl border border-emerald-200 bg-emerald-50/60 p-6 sm:p-7" aria-label="Overall energy savings">
          <div class="flex items-center gap-3 text-emerald-900">
            <div class="rounded-xl bg-emerald-100 p-2"><Leaf :size="22" aria-hidden="true" /></div>
            <div>
              <p class="text-sm font-semibold">Relative energy use</p>
              <p class="text-sm text-emerald-900/70">Updates daily to reflect fluctuating energy use based on traffic.</p>
            </div>
          </div>
          <div class="mt-6 grid gap-4 sm:grid-cols-[1fr_auto] sm:items-end">
            <div class="space-y-3">
              <div class="grid grid-cols-[5.5rem_1fr] items-center gap-3">
                <span class="text-sm font-medium text-slate-700">Default</span>
                <div class="h-3 overflow-hidden rounded-full bg-slate-200"><div class="h-full w-full rounded-full bg-slate-600" /></div>
              </div>
              <div class="grid grid-cols-[5.5rem_1fr] items-center gap-3">
                <span class="text-sm font-medium text-emerald-800">Eco mode</span>
                <div class="h-3 overflow-hidden rounded-full bg-emerald-100">
                  <div
                    class="h-full rounded-full bg-emerald-600"
                    :style="{ width: `${Math.max(4, Math.min(100, 100 / comparison.energyRatio))}%` }"
                  />
                </div>
              </div>
            </div>
            <p class="text-2xl font-semibold text-emerald-800">{{ comparison.energyRatio.toFixed(1) }}× less energy</p>
          </div>
          <p class="mt-5 border-t border-emerald-200 pt-4 text-sm text-slate-500">Daily snapshot saved {{ formattedUpdatedAt }}.</p>
        </section>

        <section class="mt-6 space-y-6" aria-label="Mode comparison notes">
          <article>
            <h2 class="text-3xl font-semibold tracking-tight text-black">Our comparison</h2>
            <p class="mt-3 text-base leading-relaxed text-base-content/75">
              We use the National Research Platform (NRP), a shared research computing platform that hosts open-weight
              AI models. Its Carbon Dashboard shows real-time GPU-power measurements that vary with traffic, alongside
              an estimate for closed frontier models. Together, these provide the basis for the estimates above.
            </p>
          </article>
          <a
            href="https://carbon-api.nrp-nautilus.io/"
            target="_blank"
            rel="noopener noreferrer"
            class="inline-block text-2xl font-semibold tracking-tight text-sky-800 underline decoration-sky-500 underline-offset-4 hover:text-sky-700"
          >Explore the NRP Carbon Dashboard ↗</a>
        </section>

        <section class="mt-10 overflow-hidden rounded-3xl bg-gradient-to-br from-slate-950 via-slate-900 to-emerald-950 p-7 text-white shadow-xl shadow-slate-900/15 sm:p-9" aria-labelledby="motivation-heading">
          <h2 id="motivation-heading" class="text-3xl font-semibold tracking-tight">Motivation</h2>
          <p class="mt-4 max-w-3xl text-base leading-relaxed text-slate-300">
            We live in a time where closed frontier models are often the default, but don't need to be. For scientific
            research, data privacy (particularly for sensitive data like endangered species locations), and energy
            consumption are important principles to consider when using AI. We care about transparency of energy use
            and model choice, which is why we offer Parsely Studio users options and share the differences between them.
            We've been inspired by recent work like "Why scientists should lead the shift away from AI mega data centres"
            and want to contribute to a more sustainable and just future.
          </p>
          <a
            href="https://www.nature.com/articles/d41586-026-02451-2"
            target="_blank"
            rel="noopener noreferrer"
            class="mt-6 block max-w-3xl rounded-2xl border border-white/15 bg-white/10 p-4 transition hover:border-emerald-300/70 hover:bg-white/15"
          >
            <span class="text-xs font-semibold uppercase tracking-[0.14em] text-emerald-300">Nature</span>
            <span class="mt-1 block font-semibold text-white underline decoration-emerald-400 underline-offset-4">Why scientists should lead the shift away from AI mega data centres ↗</span>
            <span class="mt-2 block text-sm text-slate-300">Cassidy K. Buhler, Fernando Pérez &amp; Carl Boettiger</span>
          </a>
        </section>

      </template>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, ref } from "vue";
import { Leaf, RefreshCw, Sparkles } from "lucide-vue-next";

const CARBON_API_URL = "https://carbon-api.nrp-nautilus.io/api/v1/carbon";
const DAILY_SNAPSHOT_KEY = "parsely-environmental-impact-snapshot";
const DAILY_SNAPSHOT_MS = 24 * 60 * 60 * 1000;
const loading = ref(true);
const error = ref("");
const models = ref([]);
const updatedAt = ref("");

const comparison = computed(() => {
  const qwenInstances = models.value.filter((model) =>
    model.model_name?.toLowerCase().includes("qwen3.8-27b"),
  );

  if (!qwenInstances.length) return null;

  const total = qwenInstances.reduce((sum, model) => ({
    watts: sum.watts + (model.power_watts || 0),
    promptTokens: sum.promptTokens + (model.prompt_tokens_per_sec || 0),
    generatedTokens: sum.generatedTokens + (model.generation_tokens_per_sec || 0),
    tokens: sum.tokens + (model.tokens_per_sec || 0),
    carbonGramsPerHour: sum.carbonGramsPerHour + (model.co2_grams_per_hour || 0),
  }), { watts: 0, promptTokens: 0, generatedTokens: 0, tokens: 0, carbonGramsPerHour: 0 });

  const frontierWatts = 5400 + (total.promptTokens * 0.5) + (total.generatedTokens * 6);
  const qwenCarbonPerToken = total.tokens
    ? (total.carbonGramsPerHour * 1000) / (total.tokens * 3600)
    : null;
  const averageIntensity = total.watts ? total.carbonGramsPerHour / total.watts : 0;
  const frontierCarbonPerToken = total.tokens
    ? (frontierWatts * averageIntensity * 1000) / (total.tokens * 3600)
    : null;

  return {
    instanceCount: qwenInstances.length,
    qwenWatts: total.watts,
    tokensPerSecond: total.tokens,
    qwenCarbonPerToken,
    frontierWatts,
    frontierCarbonPerToken,
    energyRatio: total.watts ? frontierWatts / total.watts : 0,
  };
});

const formattedUpdatedAt = computed(() => updatedAt.value
  ? new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short" }).format(new Date(updatedAt.value))
  : "just now");

function getDailySnapshot() {
  try {
    const snapshot = JSON.parse(window.localStorage.getItem(DAILY_SNAPSHOT_KEY));
    if (snapshot?.savedAt && Date.now() - snapshot.savedAt < DAILY_SNAPSHOT_MS) return snapshot;
  } catch {
    // An unavailable or malformed browser cache should not prevent a fresh request.
  }
  return null;
}

async function loadImpact(forceRefresh = false) {
  loading.value = true;
  error.value = "";

  try {
    const cachedSnapshot = forceRefresh ? null : getDailySnapshot();
    if (cachedSnapshot) {
      models.value = cachedSnapshot.models;
      updatedAt.value = cachedSnapshot.updatedAt;
      return;
    }

    const response = await fetch(CARBON_API_URL);
    if (!response.ok) throw new Error(`The data service returned ${response.status}.`);

    const payload = await response.json();
    models.value = payload.models || [];
    updatedAt.value = payload.updated_at || new Date().toISOString();
    if (!comparison.value) throw new Error("Qwen 3.8 27B is not currently reported by the data service.");
    window.localStorage.setItem(DAILY_SNAPSHOT_KEY, JSON.stringify({
      models: models.value,
      updatedAt: updatedAt.value,
      savedAt: Date.now(),
    }));
  } catch (fetchError) {
    error.value = fetchError.message || "Please check your connection and try again.";
  } finally {
    loading.value = false;
  }
}

function formatNumber(value) {
  return new Intl.NumberFormat(undefined, { maximumFractionDigits: 0 }).format(value);
}

function formatWatts(value) {
  return `${formatNumber(value)} W`;
}

function formatCarbon(value) {
  return value === null ? "Not available" : `${value.toFixed(value < 0.1 ? 3 : 2)} mg`;
}

onMounted(() => {
  loadImpact();
});
</script>
