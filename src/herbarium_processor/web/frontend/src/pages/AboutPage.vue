<template>
  <section class="w-full bg-base-100">
    <!-- Hero section -->
    <section class="mx-auto max-w-4xl px-4 pt-10">
      <h1 class="text-2xl sm:text-5xl md:text-6xl font-bold tracking-tight leading-tight">
        Accelerating digitization with research-informed AI.
      </h1>
      <p class="mt-6 max-w-3xl text-base sm:text-2xl text-base-content/70">
        We are a software engineer and a scientist with a bold but concrete
        goal:
        <span class="font-semibold text-base-content">increase herbarium digitization by 5% in 2026</span>.
      </p>
    </section>
    <!-- 5% more specimens digitized -->
    <section class="mx-auto max-w-4xl px-4 pb-10">
      <section
        class="mt-8 rounded-2xl border border-base-300 bg-gradient-to-br from-base-200 via-base-100 to-base-200 shadow-sm backdrop-blur p-6 sm:p-10"
      >
        <h2 class="text-2xl font-bold mb-3">
          Our Vision
        </h2>
        <p class="mt-3 text-base sm:text-lg text-base-content/80 max-w-3xl leading-relaxed">
          <span class="font-semibold text-base-content">Digitizing with Parsely represents a transformative change for
            the
            global herbarium community.</span><br><br>
          Based on early results, Parsely has the potential to make the current
          digitization rates 3 times faster. We believe a
          <span class="font-semibold text-secondary">5% global uplift in 2026 is entirely within
            reach</span>.<br><br>
          And the cost isn’t borne by any one herbarium: our
          back-of-the-envelope math puts the total global cost at just
          <span class="font-semibold text-primary">$46k<span class="align-top text-[0.65em]">†</span> for the whole
            community</span>.
        </p>
        <!-- Stats grid -->
        <div class="mt-6 grid gap-4 sm:grid-cols-3">
          <!-- Stat 1 -->
          <div class="rounded-xl border border-base-300 bg-base-100 p-5">
            <div class="mt-3 text-3xl font-bold tracking-tight">
              305k<span class="align-top text-xs ml-1">‡</span>
            </div>
            <p class="mt-1 text-sm text-base-content/70">
              Extra specimens needed worldwide for a 5% uplift
            </p>
          </div>
          <!-- Stat 2 -->
          <div class="rounded-xl border border-base-300 bg-base-100 p-5">
            <div class="mt-3 text-3xl font-bold tracking-tight">
              2.5%
            </div>
            <p class="mt-1 text-sm text-base-content/70">
              Of global baseline adopting fully (≈152.5k → 457.5k via Parsely)
            </p>
          </div>
          <!-- Stat 3 -->
          <div class="rounded-xl border border-base-300 bg-base-100 p-5">
            <div class="mt-3 text-3xl font-bold tracking-tight">
              $45.8k
            </div>
            <p class="mt-1 text-sm text-base-content/70">
              Estimated 2026 marginal costs at $0.10/specimen for ≈457.5k
              processed
            </p>
          </div>
        </div>
      </section>
      <p class="mt-4 text-xs text-base-content/60 max-w-3xl">
        † The cost estimate above reflects only marginal compute/hosting
        expenses. It does not include overhead, which are currently covered by
        volunteer time but would need support for long-term sustainability.<br>
        ‡ Baseline throughput is modeled on recent GBIF growth in
        <em>plant</em> preserved-specimen records (~6.1M/yr), a proxy for global
        digitization. Source:
        <a
          href="https://doi.org/10.1111/nph.70178"
          target="_blank"
          rel="noopener noreferrer"
          class="link link-primary"
        >New Phytologist (2025)</a>.
      </p>
    </section>
    <!-- About section -->

    <section class="max-w-6xl mx-auto px-4 py-12">
      <h2 class="text-2xl sm:text-3xl font-bold mb-8 text-center">
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
            The mix of science and engineering made Parsely stand out. It
            bridges the gap between research tools and polished apps. Parsely is
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
        Danielle is the scientist behind Parsely, contributing subject-matter
        expertise in herbarium curation and biodiversity research. She has
        experience across the entire herbarium pipeline, from field collections
        to systematics publications, ensuring Parsely combines scientific rigor
        with practical digitization workflows.
      </TeamMember>
      <TeamMember
        name="Liann Sun"
        title="Lead engineer"
        :img="liannImg"
      >
        Liann is the software engineer behind Parsely, bringing deep expertise
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
          With no extra training or onboarding required, Parsely is ready to be used
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
              It costs 10 cents per specimen to run Parsely's AI and image
              processing technology. These costs add up quickly when we imagine
              scaling it up to process thousands of specimens each month. We
              built Parsely for free and remain committed to providing it at no
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
          We’re exploring different paths for Parsely’s future — from
          grant funding to broader partnerships and shared infrastructure
          models. What’s clear is that <span class="font-bold">Parsely needs a durable home and
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
import TeamMember from "@/components/ui/TeamMember.vue";

import danielleImg from "@/assets/team/danielle.jpg";
import liannImg from "@/assets/team/liann.jpg";
</script>

<style scoped></style>
