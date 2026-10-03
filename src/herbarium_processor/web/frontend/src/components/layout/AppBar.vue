<template>
  <header :class="computedClasses">
    <div class="flex-1">
      <a
        :href="brandHref"
        class="pl-2 pr-2 text-xl cursor-pointer"
      >
        <img
          class="w-13 inline pr-2"
          :src="blob"
        >
        <span class="font-semibold">Parsely</span>
        <span class="font-light"> Studio</span>
      </a>
      <span
        v-if="showBadge"
        class="badge badge-outline badge-xs badge-error translate-y-[-2px]"
      >
        {{ badgeText }}
      </span>
      <slot name="status" />
    </div>

    <div class="flex-none">
      <slot name="right" />
    </div>

    <progress
      v-if="progressPercent !== null"
      class="progress progress-primary absolute bottom-0 left-0 w-full h-1"
      :value="progressPercent ?? 0"
      style="border-radius: 0"
      max="100"
    />
  </header>
</template>

<script setup>
import { computed } from "vue";
import blob from "@/assets/blob.svg";

const props = defineProps({
  brandHref: { type: String, default: "/" },
  showBadge: { type: Boolean, default: true },
  badgeText: { type: String, default: "1.0.0" },
  sticky: { type: Boolean, default: false },
  progressPercent: { type: Number, default: null },
});

const baseClasses = "navbar bg-base-100";

const computedClasses = computed(() => {
  const classes = [baseClasses];
  if (props.progressPercent === null) classes.push("border-y border-base-300");
  if (props.sticky) classes.push("top-0 sticky z-30 relative");
  return classes.join(" ");
});
</script>

<style scoped>
/* shared app bar styles if needed */
</style>
