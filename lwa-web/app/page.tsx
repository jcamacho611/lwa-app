import { ClipStudio } from "../components/clip-studio";
import InteractiveMythicScene from "../components/landing/InteractiveMythicScene";

export default function HomePage() {
  return (
    <div className="home-cinematic-shell relative min-h-screen overflow-hidden">
      <InteractiveMythicScene />
      <div className="relative z-10">
        <ClipStudio initialSection="home" />
      </div>
    </div>
  );
}
