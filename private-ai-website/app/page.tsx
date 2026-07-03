import Navbar from "@/components/Navbar";
import Hero from "@/components/Hero";
import Problem from "@/components/Problem";
import Solution from "@/components/Solution";
import UseCases from "@/components/UseCases";
import HowItWorks from "@/components/HowItWorks";
import PrivacyControl from "@/components/PrivacyControl";
import Technology from "@/components/Technology";
import Benefits from "@/components/Benefits";
import Packages from "@/components/Packages";
import About from "@/components/About";
import FinalCTA from "@/components/FinalCTA";
import ContactSection from "@/components/ContactSection";
import Footer from "@/components/Footer";

export default function Home() {
  return (
    <>
      <Navbar />
      <main>
        <Hero />
        <Problem />
        <Solution />
        <UseCases />
        <HowItWorks />
        <PrivacyControl />
        <Technology />
        <Benefits />
        <Packages />
        <About />
        <FinalCTA />
        <ContactSection />
      </main>
      <Footer />
    </>
  );
}
