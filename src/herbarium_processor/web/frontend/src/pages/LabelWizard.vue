<template>
  <WizardLayout :batch-id="id">
    <main class="h-full flex-1 overflow-hidden">
      <div
        v-if="loading"
        class="h-full grid place-items-center"
      >
        Loading batch…
      </div>

      <div
        v-else-if="error"
        class="h-full grid place-items-center text-error"
      >
        Failed to load batch: {{ error }}
      </div>
      <div
        v-else-if="specimens.length === 0"
        class="h-full grid place-items-center text-base-content/60"
      >
        No images in this batch.
      </div>
      <div
        v-else
        class="h-full"
      >
        <div v-if="!currentSpecimen?.image_info?.llm_output">
          <div class="flex h-full items-center justify-center">
            <div class="flex flex-col items-center space-y-3 pt-24">
              <span class="loading loading-spinner loading-lg" />
              <p class="text-sm text-base-content/60">
                Parsely is assigning label text to fields. This may take up to a minute...
              </p>
            </div>
          </div>
        </div>
        <div
          v-else
          :key="currentSpecimen?.image_info?.id ?? currentIndex"
          class="mx-auto grid grid-cols-1 md:grid-cols-[1fr_auto] h-full"
        >
          <!-- Left card (stretches) -->
          <ImageExplorer
            :specimen="currentSpecimen"
            :image-url="currentSpecimen.image_info.ocr_bounding_url"
          />

          <!-- Right card (fixed w-64, scrollable) -->
          <div class="w-64 h-full overflow-y-auto border-l border-base-300 p-4">
            <h2>Digitized fields</h2>
            <p class="text-xs leading-snug text-base-content/60">
              The id field is populated from the original image filename. Other
              fields were autocompleted by an AI model and may contain errors.
              Please review and correct them before finalizing.
            </p>
            <div
              v-for="(val, key) in form"
              :key="key"
              class="form-control mb-3"
            >
              <label class="label py-1">
                <span class="label-text text-xs">{{ key }}</span>
              </label>
              <textarea
                v-model="form[key]"
                rows="1"
                class="textarea textarea-bordered textarea-sm w-full overflow-hidden max-h-60 [field-sizing:content] min-h-0 py-1"
              />
            </div>
          </div>
        </div>
      </div>
    </main>
    <!-- Bottom bar content -->
    <template #bottom-left />

    <template
      v-if="currentSpecimen?.image_info?.llm_output"
      #bottom-right
    >
      <span class="text-gray-700 mr-4">{{ currentIndex + 1 }}/{{ specimens.length }}
      </span>
      <button
        class="btn btn-primary"
        @click="saveLabel"
      >
        {{
          currentIndex < specimens.length - 1
            ? "Save & next"
            : "Save & download CSV"
        }}
      </button>
    </template>
  </WizardLayout>
</template>

<script setup>
import { ref, provide, computed, onMounted, reactive, watch } from "vue";
import { useRoute, useRouter } from "vue-router";
import WizardLayout from "@/components/WizardLayout.vue";
import ImageExplorer from "@/components/ImageExplorer.vue";
import { useBatchStore } from "@/stores/batch"; // our Pinia store
import { useAlertStore } from "@/stores/alerts";

const props = defineProps({
  id: { type: String, required: true },
});
const router = useRouter();
const route = useRoute();
const specimens = ref([]);
const loading = ref(true);
const error = ref(null);
const currentIndex = ref(0);
// add progressPercent to provide/inject the status bar
const progressPercent = ref(66)
provide('progressPercent', progressPercent)
const batchStore = useBatchStore();
const alertStore = useAlertStore();
const hasSpecimens = computed(() => specimens.value.length > 0);
const currentSpecimen = computed(() =>
  hasSpecimens.value ? specimens.value[currentIndex.value] : null
);
const form = reactive({
  ...(currentSpecimen.value?.image_info?.llm_output || {}),
});

function setFormFrom(obj) {
  for (const k of Object.keys(form)) {
    if (!(obj && Object.prototype.hasOwnProperty.call(obj, k))) {
      delete form[k];
    }
  }
  const imageInfo = currentSpecimen.value?.image_info;
  form.id = imageInfo?.name || imageInfo?.id || "";
  if (obj) {
    for (const [k, v] of Object.entries(obj)) {
      if (k !== "id") form[k] = v;
    }
  }
}

async function saveLabel() {
  if (!currentSpecimen.value) return;
  const payload = JSON.parse(JSON.stringify(form));
  await batchStore.postUserUpdatedLlmLabels(
    props.id,
    currentSpecimen.value.image_info.id,
    payload
  );
  if (currentIndex.value < specimens.value.length - 1) {
    currentIndex.value++;
  } else {
    try {
      await batchStore.downloadCsv(props.id);
      alertStore.addAlert("Your CSV export was successful!", "success");
    } catch {
      alertStore.addAlert("CSV download failed", "error");
    } finally {
      router.push({ name: "home" }); // Go back to home after downloading
    }
  }
}

watch(
  () => currentSpecimen.value?.image_info?.llm_output,
  (newVal) => setFormFrom(newVal || {}),
  { immediate: true, deep: true }
);

onMounted(async () => {
  try {
    const batch = await batchStore.getBatch(props.id); // use store
    specimens.value = batch.specimens ?? [];

    // Auto-navigate to CropWizard if the stage is "cropping"
    const skipCroppingGuard = ["true", "1", "yes"].includes(
      String(route.query.skipCrop || "").toLowerCase()
    );
    const stage = batchStore.getBatchState(props.id);
    if (stage === "cropping" && !skipCroppingGuard) {
      router.replace({ name: "cropWizard", params: { id: props.id } });
      return;
    }
  } catch (err) {
    error.value = err.message || "Unknown error";
  } finally {
    loading.value = false;
  }
});
</script>
