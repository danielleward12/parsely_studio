<template>
  <section class="w-full bg-base-100">
    <!-- About section -->
    <section class="p-6 max-w-4xl mx-auto">
      <p class="mb-3 flex items-center gap-2 text-sm font-semibold uppercase tracking-[0.16em] text-emerald-700">
        <Leaf :size="18" aria-hidden="true" />
        Our mission
      </p>
      <h1 class="text-4xl font-semibold tracking-tight text-black sm:text-5xl">
        To support herbarium specimen digitization with research-informed AI
      </h1>
    </section>

    <section class="p-6 max-w-4xl mx-auto">
      <h2 class="text-3xl font-semibold mb-6">
        How It Started
      </h2>

      <div class="grid md:grid-cols-3 gap-6">
        <div class="rounded-xl border border-base-300 bg-base-100/70 p-6 shadow-sm">
          <h3 class="font-semibold text-primary mb-2">
            💬 The Conversation
          </h3>
          <p class="text-sm sm:text-base text-base-content/80">
            Danielle, a scientist, described the bottlenecks and backlogs of
            digitization. Liann, an engineer, envisioned how new AI could
            address these issues.
          </p>
        </div>
        <div class="rounded-xl border border-base-300 bg-base-100/70 p-6 shadow-sm">
          <h3 class="font-semibold text-secondary mb-2">
            🛠️ The Prototype
          </h3>
          <p class="text-sm sm:text-base text-base-content/80">
            Together, we built a basic tool just to test our idea. The results
            were striking: quality was high, workflows sped up dramatically, and
            human judgment remained central.
          </p>
        </div>
        <div class="rounded-xl border border-base-300 bg-base-100/70 p-6 shadow-sm">
          <h3 class="font-semibold text-accent mb-2">
            🚀 The Breakthrough
          </h3>
          <p class="text-sm sm:text-base text-base-content/80">
            The mix of science and engineering made Parsely Studio stand out. It
            bridges the gap between research tools and polished apps. Parsely Studio is
            <span>practical, reliable, and scalable</span>.
          </p>
        </div>
      </div>
    </section>

    <!-- Bio section -->
    <section class="p-6 max-w-4xl mx-auto space-y-6">
      <h2 class="text-3xl font-semibold mb-6">
        Who we are
      </h2>
      <TeamMember
        name="Danielle Ward"
        title="Lead scientist"
        :img="danielleImg"
        class="mb-6"
      >
        Danielle is the scientist behind Parsely Studio, contributing subject-matter
        expertise in herbarium curation and biodiversity research. She has
        experience across the entire herbarium pipeline, from field collections
        to systematics publications, ensuring Parsely Studio combines scientific rigor
        with practical digitization workflows.
      </TeamMember>
      <TeamMember
        name="Liann Sun"
        title="Lead engineer"
        :img="liannImg"
      >
        Liann is the software engineer behind Parsely Studio, bringing deep expertise
        in building polished, user-focused technology. She has over a decade of
        experience at startups and major tech companies and now applies her
        skills to creating tools that are intuitive, reliable, and impactful.
      </TeamMember>
    </section>
    <!-- Sustainability -->
    <section class="mx-auto max-w-4xl px-4 pb-10">
      <section class="mt-8 rounded-2xl bg-base-100/60 px-6 sm:px-10 sm:py-0 relative">
        <!-- accent bar -->
        <div
          class="pointer-events-none absolute left-0 top-0 h-full w-1 rounded-l-2xl bg-gradient-to-b from-primary to-secondary"
        />
        <h2 class="text-2xl font-bold mb-3 pl-4 sm:pl-0">
          Sustainability
        </h2>
        <!-- Intro -->
        <p class="text-base sm:text-lg text-base-content/80 leading-relaxed">
          With no extra training or onboarding required, Parsely Studio is ready to be used
          by herbaria today. To carry it from a promising tool to real global
          impact, the challenge now is covering the marginal compute/hosting
          costs and ensuring the ongoing maintenance required for a reliable
          service.
        </p>

        <!-- Callout card with two rows -->
        <div class="mt-6 rounded-xl border border-base-300 bg-base-200/60 p-6 space-y-6">
          <div>
            <h3 class="font-semibold text-base-content">
              Compute & hosting
            </h3>
            <p class="mt-1 text-sm text-base-content/80">
              It costs 10 cents per specimen to run Parsely Studio's AI and image
              processing technology. These costs add up quickly when we imagine
              scaling it up to process thousands of specimens each month. We
              built Parsely Studio for free and remain committed to providing it at no
              cost to herbaria, but these expenses need a stable funding source.
            </p>
          </div>
          <div class="border-t border-base-300 pt-6">
            <h3 class="font-semibold text-base-content">
              Stewardship
            </h3>
            <p class="mt-1 text-sm text-base-content/80">
              Running an institution-grade service means monitoring, security
              updates, and ongoing support. Today that’s our volunteer time;
              long-term, it needs a stable home.
            </p>
          </div>
        </div>

        <!-- Closing -->
        <p class="mt-6 text-base sm:text-lg text-base-content/80 leading-relaxed">
          We’re exploring different paths for Parsely Studio’s future — from
          grant funding to broader partnerships and shared infrastructure
          models. What’s clear is that <span class="font-bold">Parsely Studio needs a durable home and
            champions who share the vision of keeping it free and accessible</span>,
          while scaling to global impact. If you see a way to help shape that
          future, reach out at
          <a
            href="mailto:danielleward@berkeley.edu"
            class="font-medium text-primary underline underline-offset-4 hover:text-primary/80"
          >danielleward@berkeley.edu</a>.
        </p>
      </section>
    </section>
  </section>
</template>

<script setup>
import { Leaf } from "lucide-vue-next";
import TeamMember from "@/components/ui/TeamMember.vue";

import danielleImg from "@/assets/team/danielle.jpg";
import liannImg from "@/assets/team/liann.jpg";
</script>

<style scoped></style>
