import { ClipStudio } from "../../components/clip-studio";

export default function LoginPage() {
  return (
    <ClipStudio
      initialSection="home"
      autoOpenAuth
      initialAuthMode="login"
      pageLabel="Authentication"
      pageTitle="Sign in to your workspace"
      pageDescription="Access uploads, saved clip packs, campaigns, wallet state, and posting groundwork from any browser."
    />
  );
}
