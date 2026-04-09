# LWA iPhone Launch Checklist

This repo is now prepared for an iPhone device build and App Store submission baseline.

## What Is Already Finished In The Repo

- Real production backend URL is configured for Release builds.
- Local development backend URL is configured for Debug builds.
- App Store build mode is enabled by default.
- The shipping app icon set now exists in the asset catalog.
- The bundle identifier is no longer the placeholder `com.example.lwa`.
- ATS is restricted to local-development networking instead of broad arbitrary loads.
- The app declares `ITSAppUsesNonExemptEncryption = NO`.
- External checkout prompts are hidden in the App Store build path to reduce App Review risk for a paid web companion app.

## Current Shipping Values

- Bundle ID: `com.jcamacho611.lwa`
- Release API base URL: `https://lwa-backend-production-c9cc.up.railway.app`
- Web storefront: `https://whop.com/lwa-app/lwa-ai-content-repurposer/`

## Apple Account Steps Still Required

These cannot be completed from the repo alone.

1. Join the Apple Developer Program for the Apple ID that will publish the app.
2. In Certificates, Identifiers & Profiles, register the App ID `com.jcamacho611.lwa` if it does not already exist.
3. In App Store Connect, create the iOS app record using the same bundle ID.
4. In Xcode, open the `LWA` target and select your real `Team` under Signing & Capabilities.
5. Let Xcode create the provisioning profile automatically.
6. Build to a physical iPhone once to confirm signing is valid.
7. Archive the Release build and upload it to App Store Connect.
8. Fill in App Store metadata, screenshots, privacy policy URL, support URL, age rating, and review notes.
9. Submit the uploaded build to TestFlight first, then to App Review.

## App Review Positioning

LWA should be submitted as a free companion app to a paid web-based service.

Why:

- Apple requires in-app purchase when app features or subscriptions are unlocked inside the app.
- Apple allows free stand-alone apps that act as companions to paid web-based tools, as long as there is no purchasing inside the app or calls to action for purchase outside the app.

The iOS target was adjusted for that posture by hiding direct checkout prompts in the App Store build configuration.

## Xcode Submission Steps

1. Open `lwa-ios/LWA.xcodeproj`.
2. Select the `LWA` target.
3. Under `Signing & Capabilities`, choose your Apple Developer team.
4. Keep `Automatically manage signing` enabled.
5. Confirm the bundle identifier remains `com.jcamacho611.lwa`.
6. Choose `Any iOS Device (arm64)` or a connected iPhone.
7. Run one device build.
8. Choose `Product > Archive`.
9. In Organizer, choose `Distribute App`.
10. Select `App Store Connect`.
11. Upload the archive.

## App Store Connect Metadata To Prepare

- Name: `LWA`
- Subtitle: `AI Clip Repurposer`
- Category: `Photo & Video` or `Productivity`
- Privacy Policy URL: your real policy URL
- Support URL: your real support URL
- Description: explain that the app turns long-form video URLs into clips, hooks, captions, and downloadable assets
- Review Notes: mention that backend services are live and explain any required demo flow

## Recommended Review Notes

Use this in App Review notes:

`LWA is a companion app for our hosted clip-generation service. The iOS app itself does not present in-app purchasing. The backend is live and reachable at https://lwa-backend-production-c9cc.up.railway.app. To review the clip-generation flow, enter a public video URL and tap Generate Clips.`

## Official Apple References

- App Review Guidelines: https://developer.apple.com/app-store/review/guidelines/
- Upload builds to App Store Connect: https://developer.apple.com/help/app-store-connect/manage-builds/upload-builds/
- Distribute your app for beta testing and releases: https://developer.apple.com/documentation/xcode/distributing-your-app-for-beta-testing-and-releases
