import MarketingNavbar from "../components/layout/MarketingNavbar";
import UploadBox from "../components/upload/UploadBox";
import Footer from "../components/layout/Footer";

export default function Home() {
  return (
    <>
      <MarketingNavbar />

      {/* HERO SECTION */}
      <section className="bg-blue-50">
        <div className="relative z-10 mx-auto max-w-7xl px-6 pt-28 pb-16 text-center">

          {/* Context / trust line */}
          <div className="mb-6 flex justify-center">
            <span className="rounded-full border border-gray-300 bg-white px-4 py-1 text-xs text-gray-600">
              Research preview · No data stored · ML-powered
            </span>
          </div>

          {/* Headline */}
          <h1 className="text-4xl md:text-5xl font-bold tracking-tight text-black mb-6">
            AI-powered video content moderation
          </h1>

          {/* Description (HOW, not WHAT) */}
          <p className="mx-auto max-w-2xl text-gray-600 text-lg leading-relaxed mb-6">
            Aegis AI uses a multimodal approach that combines vision, audio, and
            text-based models to analyze video content holistically. This enables
            more reliable and context-aware moderation decisions.
          </p>

          {/* Capability bullets (WHAT the user gets) */}
          <div className="mt-6 flex flex-wrap justify-center gap-x-10 gap-y-4 text-sm text-gray-600">
            <div className="flex items-center gap-2">
              <span className="text-brand">•</span>
              <span>Classify sensitive content across multiple categories</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-brand">•</span>
              <span>Identify exact timestamps of problematic segments</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-brand">•</span>
              <span>Generate confidence scores with a final verdict</span>
            </div>
          </div>

          {/* CTAs */}
          <div className="mt-10 flex justify-center gap-4">
            <button
              className="group relative overflow-hidden rounded-lg bg-black px-6 py-3 text-sm font-medium text-white transition-all duration-300 ease-out hover:-translate-y-[1px] hover:shadow-[0_10px_30px_rgba(0,0,0,0.2)]"
              onClick={() =>
                document
                  .getElementById("upload-section")
                  ?.scrollIntoView({ behavior: "smooth" })
              }
            >
              <span className="relative z-10">Try it now</span>
              <span className="pointer-events-none absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
            </button>

            <a
              href="#how-it-works"
              className="rounded-lg border border-gray-300 bg-white px-6 py-3 text-sm font-medium text-gray-700 hover:border-black hover:text-black transition"
            >
              How it works
            </a>
          </div>
        </div>
      </section>

      {/* UPLOAD SECTION */}
      <section
        id="upload-section"
        className="px-6 pt-16 pb-24 bg-white"
      >
        {/* Divider belongs to upload section */}
        <div className="mx-auto max-w-3xl border-t border-gray-300 mb-16" />

        <UploadBox />
      </section>

      <Footer />
    </>
  );
}
