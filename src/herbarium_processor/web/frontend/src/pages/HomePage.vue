<template>
  <div class="m-4 mt-8 space-y-4 max-w-4xl mx-auto">
    <div
      class="mx-4 rounded-lg bg-gradient-to-r from-blue-500 to-info to text-white py-3 px-6 text-center shadow-md"
    >
      <span class="font-bold"> 👋🏼 New here?</span> Parsely Studio turns specimen
      labels into digital records in 4 quick steps —
      <a
        href="/how-it-works"
        class="underline font-medium hover:text-green-100"
      >
        see how it works</a>.
    </div>
    <BaseCard class="mx-4">
      <template #header>
        Upload photos of specimens
      </template>
      <!-- Drop zone -->
      <div
        :class="[
          'border-2 border-dashed rounded p-12 text-center cursor-pointer transition-colors',
          isDragging ? 'border-primary bg-base-200' : 'border-base-content/25 bg-base-200/30 hover:border-base-content/35 hover:bg-base-200/50',
        ]"
        @click="triggerFileSelect"
        @dragover.prevent="onDragEnter"
        @dragenter.prevent="onDragEnter"
        @dragleave.prevent="onDragLeave"
        @drop.prevent="onDrop"
      >
        <p>
          Drag & drop images, or click to select
        </p>
        <p class="text-xs text-base-content/70">
          Current upload limit: {{ maxUploadCount }} image{{ maxUploadCount === 1 ? '' : 's' }}
        </p>
      </div>

      <!-- Hidden file input -->
      <input
        ref="fileInput"
        type="file"
        multiple
        accept="image/*"
        class="hidden"
        @change="onFileSelect"
      >

      <div class="mt-4">
        <div class="flex items-center gap-2">
          <button
            type="button"
            :class="['btn btn-sm', batchStore.selectedModel === 'gemini' ? 'btn-neutral' : 'btn-outline']"
            @click="selectModel('gemini')"
          >
            Default mode
          </button>
          <button
            type="button"
            :class="['btn btn-sm border-success bg-success/10 text-base-content hover:bg-success/20', batchStore.selectedModel === 'qwen' ? 'ring-1 ring-success' : '']"
            @click="selectModel('qwen')"
          >
            Eco mode
          </button>
          <RouterLink
            to="/environmental-impact"
            class="btn btn-ghost btn-circle btn-sm text-base-content/70 hover:text-emerald-700"
            aria-label="Learn about the environmental impact of each mode"
            title="Learn about environmental impact"
          >
            <Info
              :size="18"
              aria-hidden="true"
            />
          </RouterLink>
        </div>

        <p class="mt-2 max-w-md text-xs leading-relaxed text-base-content/70">
          {{ selectedModeDescription }}
        </p>
      </div>

      <!-- Thumbnails -->
      <div
        v-if="uploads.length"
        class="flex flex-wrap gap-4 mt-4"
      >
        <div
          v-for="(upload, index) in uploads"
          :key="index"
          class="relative w-24 h-24"
        >
          <img
            :src="upload.url"
            alt="preview"
            class="object-cover w-full h-full rounded"
          >
          <button
            type="button"
            class="absolute -top-2 -right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center"
            @click="removeImage(index)"
          >
            &times;
          </button>
        </div>
      </div>
      <div class="mt-4">
        <button
          type="button"
          class="btn btn-sm btn-outline"
          :aria-expanded="showAdvancedSettings"
          @click="showAdvancedSettings = !showAdvancedSettings"
        >
          Advanced settings
          <span aria-hidden="true">{{ showAdvancedSettings ? '▴' : '▾' }}</span>
        </button>
        <div
          v-if="showAdvancedSettings"
          class="mt-2 rounded-box bg-base-200 p-4 text-sm text-base-content/80 space-y-4"
        >
          <div class="form-control w-full mt-2">
            <label class="label justify-between mb-2">
              <span class="label-text text-base-content font-medium">Google API key</span>
              <span
                v-if="validatingKey"
                class="loading loading-spinner loading-xs text-primary"
              />
              <span
                v-else-if="isKeyValid === true && trimmedApiKey"
                class="text-success text-xs font-medium"
              >
                Valid ✅
              </span>
              <span
                v-else-if="isKeyValid === false && trimmedApiKey"
                class="text-error text-xs font-medium"
              >
                Invalid ❌
              </span>

            </label>
            <input
              v-model="apiKey"
              type="text"
              inputmode="text"
              autocomplete="off"
              spellcheck="false"
              placeholder="AIzaSy..."
              class="input input-bordered input-sm font-mono tracking-tight w-full"
              @blur="validateApiKey"
            >
            <label class="label">
              <span class="label-text-alt text-base-content/70 text-xs">
                Providing your own key raises the upload limit to 50 images.
              </span>
            </label>
            <p
              v-if="trimmedApiKey && keyError"
              class="text-xs text-error mt-1"
            >
              {{ keyError }}
            </p>
          </div>
          <!-- Skip Crop Checkbox -->
          <div class="form-control w-full mt-6">
            <label class="label cursor-pointer justify-start gap-3 p-0">
              <input
                v-model="skipCrop"
                type="checkbox"
                class="checkbox checkbox-primary"
              >
              <span class="label-text text-base-content font-medium">
                Skip cropping
              </span>
            </label>
            <p class="text-xs leading-relaxed text-base-content/70">
              Labels pre-cropped and rotated? Choose this to infer
              all images as-is, skipping the manual cropping step.
            </p>
          </div>
        </div>
      </div>

      <template #actions>
        <button
          class="btn btn-primary"
          :disabled="isUploading || !uploads.length"
          @click="handleUpload"
        >
          <span
            v-if="isUploading"
            class="loading loading-spinner mr-2"
          />
          {{ isUploading ? "Uploading…" : "Next" }}
        </button>
      </template>
    </BaseCard>
    <BaseCard class="mt-6 mb-12 mx-4">
      <HowItWorksStrip />
    </BaseCard>
  </div>
</template>

<script setup>
import { computed, ref } from "vue";
import { useRouter } from "vue-router";
import { Info } from "lucide-vue-next";
import BaseCard from "@/components/ui/BaseCard.vue";
import HowItWorksStrip from "../components/HowItWorksStrip.vue";
import { useBatchStore } from "@/stores/batch";

const router = useRouter();
const fileInput = ref(null);
const uploads = ref([]); // [{ file: File, url: string }]
const isUploading = ref(false);
const isDragging = ref(false);
const skipCrop = ref(false);
const apiKey = ref("");
const showAdvancedSettings = ref(false);
const batchStore = useBatchStore();

const trimmedApiKey = computed(() => apiKey.value.trim());
const selectedModeDescription = computed(() =>
  batchStore.selectedModel === "qwen"
    ? "Powered by Qwen 3.8 27B, an open-weight model. It has a lower environmental impact and is a more transparent option, with a trade-off in accuracy."
    : "Powered by Gemini 2.5 Pro. Provides the highest historical accuracy for transcribing complex, handwritten herbarium labels."
);

const selectModel = (model) => {
  batchStore.selectedModel = model;
};
const maxUploadCount = computed(() => (trimmedApiKey.value ? 50 : 5));
const validatingKey = ref(false);
const isKeyValid = ref(null); // true / false / null
const keyError = ref("");

const validateApiKey = async () => {
  if (!trimmedApiKey.value) return;
  validatingKey.value = true;
  isKeyValid.value = null;
  keyError.value = "";

  try {
    const res = await fetch(
      `https://generativelanguage.googleapis.com/v1beta/models?key=${trimmedApiKey.value}`
    );
    if (res.status === 200) {
      const data = await res.json();
      const modelIds = (data.models || []).map((m) => m.name || m.id || "");
      const hasGemini25 = modelIds.some((id) =>
        id.includes("gemini-2.5-pro")
      );
      if (hasGemini25) {
        isKeyValid.value = true;
      } else {
        isKeyValid.value = false;
        keyError.value =
          "Key is valid but does not have access to Gemini 2.5 Pro.";
      }
    } else if (res.status === 403) {
      isKeyValid.value = false;
      keyError.value =
        "API key is valid but unauthorized for the Gemini API (403).";
    } else if (res.status === 400) {
      isKeyValid.value = false;
      keyError.value = "Invalid API key or malformed request (400).";
    } else {
      isKeyValid.value = false;
      keyError.value = `Unexpected response: ${res.status}`;
    }
  } catch (err) {
    console.error("Error validating key:", err);
    isKeyValid.value = false;
    keyError.value = "Network or validation error.";
  } finally {
    validatingKey.value = false;
  }
};

const triggerFileSelect = () => {
  fileInput.value?.click();
};

const onFileSelect = (e) => {
  handleFiles(e.target.files);
  // reset value so selecting the same file again triggers change
  e.target.value = "";
};

const onDragEnter = () => {
  isDragging.value = true;
};

const onDragLeave = () => {
  isDragging.value = false;
};

const onDrop = (e) => {
  isDragging.value = false;
  handleFiles(e.dataTransfer.files);
};

const handleFiles = (fileList) => {
  const limit = maxUploadCount.value;
  const remaining = Math.max(limit - uploads.value.length, 0);
  const files = Array.from(fileList).slice(0, remaining);
  for (const file of files) {
    if (file.type.startsWith("image/")) {
      uploads.value.push({ file, url: URL.createObjectURL(file) });
    }
  }
  if (uploads.value.length >= limit && fileList.length > remaining) {
    const message = trimmedApiKey.value
      ? "You can upload up to 50 images when providing an API key."
      : "You can upload up to 5 images.";
    alert(message);
  }
};

const removeImage = (index) => {
  URL.revokeObjectURL(uploads.value[index].url);
  uploads.value.splice(index, 1);
};

const handleUpload = async () => {
  if (trimmedApiKey.value) {
    await validateApiKey();
    if (!isKeyValid.value && trimmedApiKey.value) {
      alert(
        keyError.value ||
          "Invalid or unauthorized Google API key. Please check it before continuing."
      );
      return;
    }
  }
  const limit = maxUploadCount.value;
  if (!uploads.value.length) {
    alert("Please choose a file first.");
    return;
  }
  if (uploads.value.length > limit) {
    alert(
      `Please remove ${uploads.value.length - limit} image${
        uploads.value.length - limit === 1 ? "" : "s"
      } to meet the ${limit}-image limit.`
    );
    return;
  }
  isUploading.value = true;

  const formData = new FormData();
  for (const { file } of uploads.value) {
    formData.append("files", file); // match the parameter name in FastAPI
  }

  try {
    const res = await fetch(
      "/api/batches",
      {
        method: "POST",
        body: formData,
        ...(trimmedApiKey.value
          ? { headers: { "X-API-Key": trimmedApiKey.value } }
          : {}),
      }
    );

    if (!res.ok) throw new Error(`Upload failed: ${res.status}`);

    const data = await res.json();
    const batchId = data?.batch_id ?? data?.id ?? data?.uuid;
    if (!batchId) throw new Error("Batch ID missing in response.");
    if (skipCrop.value) {
      // Populate the shared cache before the review page mounts. Otherwise the
      // worker and page can race to fetch separate batch objects, and the page
      // won't see the worker's inference updates.
      const batch = await batchStore.getBatch(batchId);
      queueAutoCropAndInfer(batchId, batch);
      router.replace({
        name: "labelWizard",
        params: { id: batchId },
        query: { skipCrop: "true" },
      });
    } else {
      // Navigate to the first step, cropping
      router.replace({ name: "cropWizard", params: { id: batchId } });
    }
  } catch (err) {
    console.error("❌ Error uploading:", err);
    alert("Upload failed. Check console for details.");
  } finally {
    isUploading.value = false;
  }
};

const loadImageDimensions = (url) =>
  new Promise((resolve, reject) => {
    const img = new Image();
    img.onload = () => {
      resolve({ width: img.naturalWidth, height: img.naturalHeight });
    };
    img.onerror = (err) => reject(err);
    img.src = url;
  });

const queueAutoCropAndInfer = (batchId, batch) => {
  // Fire-and-forget background processing; errors are logged but do not block navigation
  (async () => {
    try {
      const specimens = batch?.specimens ?? [];

      await Promise.all(
        specimens.map(async (specimen) => {
          try {
            const info = specimen?.image_info ?? {};
            const sourceUrl = info.pre_crop_url || info.url;
            if (!specimen?.id || !sourceUrl) return;

            const { width, height } = await loadImageDimensions(sourceUrl);
            await batchStore.cropAndInfer(batchId, specimen.id, {
              x: 0,
              y: 0,
              width,
              height,
              rotate: 0,
            });
          } catch (specimenErr) {
            console.error(
              `Auto crop_and_infer failed for specimen ${specimen?.id}`,
              specimenErr
            );
          }
        })
      );
    } catch (err) {
      console.error("Auto crop_and_infer failed", err);
    }
  })();
};
</script>

<style scoped></style>
