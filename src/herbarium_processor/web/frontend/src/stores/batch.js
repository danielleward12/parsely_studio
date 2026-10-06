// src/stores/batch.js
import { defineStore } from "pinia";

/**
 * @typedef {Object} CropOperation
 * @property {number} x
 * @property {number} y
 * @property {number} width
 * @property {number} height
 * @property {number} rotate
 */

// Data from the backend API
/**
 * @typedef {Object} ImageInfo
 * @property {string} id
 * @property {string} name
 * @property {string} [url]
 * @property {string} [pre_crop_url]
 * @property {string} [post_crop_url]
 * @property {string} [ocr_bounding_url]
 * @property {any} [llm_output]
 * @property {any} [user_edited_llm_output]

 */

/**
 * @typedef {Object} SpecimenRecord
 * @property {ImageInfo} image_info
 * @property {boolean} [waiting_on_llm]
 */

/**
 * @typedef {Object} Batch
 * @property {string} batch_id
 * @property {SpecimenRecord[]} specimens
 */

export const useBatchStore = defineStore("batches", {
  state: () => ({
    // Acts as an in-memory cache: { [id]: Batch }
    /** @type {Record<string, Batch>} */
    batches: {},
    processingErrors: {},
  }),
  actions: {
    // Convenience: get specimens array for a batch (always an array)
    _getSpecimens(batchId) {
      const batch = this.batches[batchId];
      return batch && Array.isArray(batch.specimens) ? batch.specimens : [];
    },
    // Convenience: get ImageInfo from a specimen record (supports both shapes)
    _getImageInfoFromItem(item) {
      return item?.image_info || null;
    }, // Convenience: find index by image id regardless of item shape
    _findIndexByImageId(batchId, imageId) {
      const arr = this._getSpecimens(batchId);
      return arr.findIndex(
        (it) => this._getImageInfoFromItem(it)?.id === imageId
      );
    },
    // Convenience: merge fields into the specimen record (image_info and/or waiting_on_llm)
    _mergeSpecimenRecord(batchId, imageId, patch) {
      const arr = this._getSpecimens(batchId);
      const idx = this._findIndexByImageId(batchId, imageId);
      if (idx === -1) return;

      const curr = arr[idx] || {};
      const next = { ...curr };

      if (
        patch &&
        Object.prototype.hasOwnProperty.call(patch, "waiting_on_llm")
      ) {
        next.waiting_on_llm = !!patch.waiting_on_llm;
      }
      if (patch && patch.image_info) {
        next.image_info = { ...(curr.image_info || {}), ...patch.image_info };
      }
      arr[idx] = next;
    },
    /**
     * @param {string} id
     * @returns {{cropping: number, digitizing: number, ready: number}}
     */
    getItemsInEachState(id) {
      const batch = this.batches[id];
      if (!batch?.specimens?.length)
        return { cropping: 0, digitizing: 0, ready: 0, reviewed: 0 };

      let cropping = 0,
        digitizing = 0,
        ready = 0,
        reviewed = 0;
      for (const item of batch.specimens) {
        const img = item.image_info;

        if (item.waiting_on_llm) {
          digitizing++;
        } else if (!img?.post_crop_url) {
          cropping++;
        } else if (!img?.llm_output) {
          digitizing++;
        } else if (!img?.user_edited_llm_output) {
          ready++;
        } else {
          reviewed++;
        }
      }
      return { cropping, digitizing, ready, reviewed };
    },
    /**
     * @param {string} id
     * @returns {"cropping"|"digitizing"}
     */ getBatchState(id) {
      if (this.getItemsInEachState(id).cropping > 0) return "cropping";
      return "labeling";
    },
    /**
     * Returns the batch for `id`.
     * - If already cached, returns it immediately.
     * - Otherwise fetches from `/api/batches/:id`, stores it, then returns.
     */
    /**
     * @param {string} id
     * @returns {Promise<Batch>}
     */
    async getBatch(id) {
      if (this.batches[id]) {
        // cache hit
        return this.batches[id];
      }

      // cache miss
      const res = await fetch(`/api/batches/${id}`);
      if (!res.ok) throw new Error(`Failed to fetch ${id}`);

      const data = await res.json();
      const piniaBatch = {};
      piniaBatch.batch_id = data.batch_id;
      piniaBatch.specimens = data.images.map((img) => ({
        id: img.id,
        image_info: img,
      }));
      this.batches[id] = piniaBatch;

      return piniaBatch;
    },

    /**
     * Crop and infer for a single image in a batch.
     * - Fires POST to backend and merges response into the store when available.
     * - Returns a promise that resolves with the parsed JSON (or null if none).
     */
    /**
     * @param {string} batchId
     * @param {string} imageId
     * @param {CropOperation} cropOp
     * @returns {Promise<ImageInfo|null>}
     */
    async cropAndInfer(batchId, imageId, cropOp) {
      const url = `/api/batches/${batchId}/crop_and_infer/${imageId}`;
      const processingKey = `${batchId}:${imageId}`;

      // Set waiting flag true at start
      this._mergeSpecimenRecord(batchId, imageId, {
        waiting_on_llm: true,
        image_info: {
          post_crop_url: `/tmp/batch_${batchId}/images/${imageId}/post_crop.jpg`,
        },
      });
      delete this.processingErrors[processingKey];

      let updated = null;
      try {
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(cropOp),
        });
        if (!res.ok) {
          let message = `Crop/infer failed: ${res.status}`;
          try {
            const errorBody = await res.json();
            message = errorBody?.detail || message;
          } catch {
            // Keep the status-based message when the response isn't JSON.
          }
          throw new Error(message);
        }

        // Backend may return JSON object with updated fields; guard empty body
        try {
          updated = await res.json();
        } catch {
          updated = null;
        }

        // Merge returned fields into the item's image_info
        this._mergeSpecimenRecord(batchId, imageId, {
          image_info: updated || {},
        });
        if (!updated?.llm_output) {
          this.processingErrors[processingKey] =
            "Processing finished without parsed fields. Please try again.";
        }
      } catch (err) {
        this.processingErrors[processingKey] =
          err?.message || "Image processing failed. Please try again.";
        throw err;
      } finally {
        // Clear waiting flag regardless of success/failure
        this._mergeSpecimenRecord(batchId, imageId, { waiting_on_llm: false });
      }

      return updated;
    },

    async postUserUpdatedLlmLabels(batchId, imageId, labels) {
      const url = `/api/batches/${batchId}/save_label_edits/${imageId}`;

      let updated = null;
      try {
        const res = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(labels),
        });
        if (!res.ok) throw new Error(`Crop/infer failed: ${res.status}`);

        // Backend may return JSON object with updated fields; guard empty body
        try {
          updated = await res.json();
        } catch {
          updated = null;
        }

        // Merge returned fields into the item's image_info
        this._mergeSpecimenRecord(batchId, imageId, {
          image_info: updated || {},
        });
      } finally {
        // Clear waiting flag regardless of success/failure
        console.log("saved user edits");
      }

      return updated;
    },

    /**
     * Fetch CSV export for the batch and trigger a browser download.
     * @param {string} batchId
     * @returns {Promise<void>}
     */
    async downloadCsv(batchId) {
      const url = `/api/batches/${batchId}/get_csv`;

      const res = await fetch(url);
      if (!res.ok) {
        throw new Error(`CSV download failed: ${res.status}`);
      }

      const blob = await res.blob();

      const disposition = res.headers.get("content-disposition") || "";
      const match = disposition.match(/filename="?([^";]+)"?/i);
      const filename = match ? match[1] : `parsely_export_${Date.now()}.csv`;

      const link = document.createElement("a");
      const blobUrl = URL.createObjectURL(blob);
      link.href = blobUrl;
      link.download = filename;
      document.body.appendChild(link);
      link.click();
      link.remove();
      URL.revokeObjectURL(blobUrl);
    },
  },
});
