import { Link } from "react-router-dom";
import logoLarge from "../../assets/logo-large.png";

export default function Footer() {
  return (
    <footer className="border-t border-gray-200 bg-white mt-24">
      <div className="mx-auto max-w-7xl px-6 py-12 grid grid-cols-1 md:grid-cols-4 gap-8 text-sm text-gray-600">

        {/* Brand */}
        <div>
          <img
            src={logoLarge}
            alt="Aegis AI logo"
            className="h-16 w-auto mb-4"
          />
          <h4 className="font-semibold text-black mb-2">
            Aegis AI
          </h4>
          <p className="text-gray-500 leading-relaxed mb-8">
            Automated video content moderation using modern machine learning.
          </p>

          {/* Social / Links */}
          <div className="flex flex-col gap-2 text-sm">
            <a
              href="https://github.com/Aksh3141/Cornerstone_project"
              target="_blank"
              rel="noopener noreferrer"
              className="text-gray-500 hover:text-black transition"
            >
              GitHub ↗
            </a>

            <Link
              to="/docs"
              className="text-gray-500 hover:text-black transition"
            >
              Docs
            </Link>

            <a
              href="mailto:verma4yuvi@gmail.com"
              className="text-gray-500 hover:text-black transition"
            >
              Contact
            </a>
          </div>
        </div>

        {/* Product */}
        <div>
          <h5 className="font-medium text-black mb-3">Product</h5>
          <ul className="space-y-2">
            <li>
              <Link
                to="/howitworks"
                className="hover:text-black transition"
              >
                How it works
              </Link>
            </li>
            <li>
              <Link
                to= "/?scroll=upload"
                className="hover:text-black transition"
              >
                Upload
              </Link>
            </li>
            <li>
              <span className="text-gray-400 cursor-not-allowed">
                Roadmap
              </span>
            </li>
          </ul>
        </div>

        {/* Technology */}
        <div>
          <h5 className="font-medium text-black mb-3">Technology</h5>
          <ul className="space-y-2 text-gray-500">
            <li>React + Tailwind</li>
            <li>Django REST</li>
            <li>Deep Learning Models</li>
          </ul>
        </div>

        {/* Legal */}
        <div>
          <h5 className="font-medium text-black mb-3">Legal</h5>
          <ul className="space-y-2">
            <li>
              <span className="text-gray-400 cursor-not-allowed">
                Privacy Policy
              </span>
            </li>
            <li>
              <span className="text-gray-400 cursor-not-allowed">
                Terms of Service
              </span>
            </li>
          </ul>
        </div>
      </div>

      {/* Trust / Status indicators */}
      <div className="flex flex-wrap justify-center gap-3 py-6 text-xs text-gray-600">
        <span className="rounded-full border border-gray-300 px-3 py-1">
          Research preview
        </span>
        <span className="rounded-full border border-gray-300 px-3 py-1">
          Beta
        </span>
        <span className="rounded-full border border-gray-300 px-3 py-1">
          No data stored
        </span>
      </div>

      <div className="border-t border-gray-100 py-6 text-center text-xs text-gray-400">
        © {new Date().getFullYear()} Aegis AI. All rights reserved.
      </div>
    </footer>
  );
}
