import { ClipStudio } from "../../components/clip-studio";

export default function SignupPage() {
  return (
    <ClipStudio
      initialSection="home"
      autoOpenAuth
      initialAuthMode="signup"
      pageLabel="Authentication"
      pageTitle="Create your LWA account"
      pageDescription="Start with a browser-first creator workspace that can expand into uploads, campaigns, wallet state, and premium packaging workflows."
    />
  );
}
