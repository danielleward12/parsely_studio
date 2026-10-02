<template>
  <WizardLayout :batch-id="id">
    <!-- Main content: make it fill and scroll *inside* the middle pane if needed -->
    <!-- Middle: fills between top/bottom bars; page itself won't scroll -->
    <main class="h-full flex-1 overflow-hidden">
      <!-- States -->
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

      <!-- Two-panel workspace -->
      <div
        v-else
        class="h-full grid grid-cols-1 md:grid-cols-[1fr_280px]"
      >
        <!-- Left: work area (scrolls internally if needed) -->
        <section class="h-full overflow-auto bg-black">
          <SpecimenCropView
            v-if="currentSpecimen"
            :key="currentSpecimen?.id ?? currentIndex"
            :ref="setCropperRef"
            :specimen="currentSpecimen"
            class=""
          />
        </section>

        <!-- Right: inspector/notes (fixed narrow pane, internal scroll) -->
        <aside class="h-full overflow-auto border-l border-base-300 p-4">
          <h2 class="text-lg font-semibold tracking-tight text-base-content">
            Crop · {{ currentSpecimen.image_info.name }}
          </h2>

          <p class="mt-2 text-sm text-base-content/80">
            Click and drag the borders of the cropping tool so that it only captures the specimen label. Do not include
            barcodes, color palettes, rulers, and the specimens themselves.
          </p>
        </aside>
      </div>
    </main>

    <!-- Bottom bar content -->
    <template #bottom-left />

    <template #bottom-right>
      <span class="text-gray-700 mr-4">{{ currentIndex + 1 }} of {{ specimens.length }}</span>
      <button
        class="btn btn-primary"
        :disabled="isUploading"
        @click="handleUpload"
      >
        <span
          v-if="isUploading"
          class="loading loading-spinner mr-2"
        />
        {{
          isUploading
            ? "Saving & extracting…"
            : currentIndex < specimens.length - 1 ? "Save & next" : "Save & move to validation" }}
      </button>
      <p v-if="saveError" class="ml-3 max-w-sm text-sm text-error" role="alert">
        {{ saveError }}
      </p>
    </template>
  </WizardLayout>
</template>

<script setup>
import {
  ref,
  computed,
  provide,
  onMounted,
  onBeforeUpdate,
} from "vue";
import { useRouter } from "vue-router";
import WizardLayout from "@/components/WizardLayout.vue";
import SpecimenCropView from "@/components/SpecimenCropView.vue";
import { useBatchStore } from "@/stores/batch";

const props = defineProps({
  id: { type: String, required: true },
});

const router = useRouter();
const specimens = ref([]);
const loading = ref(true);
const error = ref(null);
const saveError = ref(null);
const cropperRefs = ref([]);
const isUploading = ref(false);
const currentIndex = ref(0);
// add progressPercent to provide/inject the status bar
const progressPercent = ref(33)
provide('progressPercent', progressPercent)


const batchStore = useBatchStore();

const hasSpecimens = computed(() => specimens.value.length > 0);
const currentSpecimen = computed(() =>
  hasSpecimens.value ? specimens.value[currentIndex.value] : null
);

// Avoid stale element refs between patches
onBeforeUpdate(() => {
  cropperRefs.value = [];
});

onMounted(async () => {
  try {
    const batch = await batchStore.getBatch(props.id); // use store
    if (batchStore.getBatchState(props.id) !== "cropping") {
      router.push({ name: "home" });
    }
    specimens.value = batch.specimens ?? [];
    cropperRefs.value = Array(specimens.value.length).fill(null); // ensure array length matches specimens
  } catch (err) {
    error.value = err?.message || "Unknown error";
  } finally {
    loading.value = false;
  }
});

// Safe function ref: never use .value from template; set here.
function setCropperRef(el) {
  // Function refs fire with el (instance) on mount and el=null on unmount.
  if (!el) return;
  const i = currentIndex.value;
  if (!Array.isArray(cropperRefs.value)) cropperRefs.value = [];
  // Make sure our array is at least i+1 long
  if (cropperRefs.value.length < i + 1) {
    cropperRefs.value.length = i + 1;
  }
  cropperRefs.value[i] = el;
}

async function handleUpload() {
  if (!hasSpecimens.value) return;
  isUploading.value = true;
  saveError.value = null;

  try {
    const specimen = specimens.value[currentIndex.value];
    const cropperRef = cropperRefs.value[currentIndex.value];

    if (!specimen) throw new Error("Missing current image");
    if (!cropperRef || typeof cropperRef.getCropOperation !== "function") {
      throw new Error("Cropper not ready");
    }

    const cropOp = await cropperRef.getCropOperation();
    if (!cropOp) throw new Error("No crop operation");

    // Wait for the crop and inference response before advancing. The next
    // screen derives its stage from post_crop_url and llm_output in the store.
    await batchStore.cropAndInfer(props.id, specimen.id, cropOp);

    // Advance only after the server has completed the crop and inference.
    if (currentIndex.value < specimens.value.length - 1) {
      currentIndex.value++;
    } else {
      console.log("Done cropping; go to labeling");
      router.push({ name: "labelWizard", params: { id: props.id } });
    }
  } catch (err) {
    console.error("crop_and_infer error", err);
    saveError.value = err?.message || "Could not save this crop. Please try again.";
  } finally {
    isUploading.value = false;
  }
}
</script>
