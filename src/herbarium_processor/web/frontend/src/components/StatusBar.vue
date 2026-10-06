<template>
  <AppBar
    :sticky="true"
    :progress-percent="progressPercent"
    badge-text="1.0.0"
  />
</template>

<script setup>
import { ref, onMounted, inject } from "vue";
import { useBatchStore } from "@/stores/batch";
import AppBar from "@/components/layout/AppBar.vue";

const props = defineProps({
  id: { type: [String, Number], default: null },
});

const batchStore = useBatchStore();
const specimens = ref([]);
const loading = ref(true);
const error = ref(null);
const progressPercent = inject('progressPercent')

onMounted(async () => {
  try {
    const batch = await batchStore.getBatch(props.id); // use store
    specimens.value = batch.specimens ?? [];
  } catch (err) {
    error.value = err?.message || "Unknown error";
  } finally {
    loading.value = false;
  }
});
</script>
