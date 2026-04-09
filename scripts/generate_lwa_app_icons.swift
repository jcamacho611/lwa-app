import AppKit

private extension NSBezierPath {
    var cgPath: CGPath {
        let path = CGMutablePath()
        var points = [NSPoint](repeating: .zero, count: 3)

        for index in 0..<elementCount {
            switch element(at: index, associatedPoints: &points) {
            case .moveTo:
                path.move(to: points[0])
            case .lineTo:
                path.addLine(to: points[0])
            case .curveTo:
                path.addCurve(to: points[2], control1: points[0], control2: points[1])
            case .cubicCurveTo:
                path.addCurve(to: points[2], control1: points[0], control2: points[1])
            case .quadraticCurveTo:
                path.addQuadCurve(to: points[1], control: points[0])
            case .closePath:
                path.closeSubpath()
            @unknown default:
                break
            }
        }

        return path
    }
}

let outputDirectory = CommandLine.arguments.count > 1
    ? URL(fileURLWithPath: CommandLine.arguments[1], isDirectory: true)
    : URL(fileURLWithPath: FileManager.default.currentDirectoryPath, isDirectory: true)

let fileManager = FileManager.default
try fileManager.createDirectory(at: outputDirectory, withIntermediateDirectories: true)

let canvasSize = CGSize(width: 1024, height: 1024)
let image = NSImage(size: canvasSize)

image.lockFocus()
guard let context = NSGraphicsContext.current?.cgContext else {
    fatalError("Could not create graphics context")
}

let bounds = CGRect(origin: .zero, size: canvasSize)

let background = CGGradient(
    colorsSpace: CGColorSpace(name: CGColorSpace.sRGB)!,
    colors: [
        NSColor(calibratedRed: 0.06, green: 0.08, blue: 0.14, alpha: 1).cgColor,
        NSColor(calibratedRed: 0.03, green: 0.04, blue: 0.08, alpha: 1).cgColor,
    ] as CFArray,
    locations: [0.0, 1.0]
)!

context.drawLinearGradient(
    background,
    start: CGPoint(x: 0, y: canvasSize.height),
    end: CGPoint(x: canvasSize.width, y: 0),
    options: []
)

context.saveGState()
let glowRect = CGRect(x: 110, y: 130, width: 804, height: 764)
let glowPath = NSBezierPath(roundedRect: glowRect, xRadius: 210, yRadius: 210)
context.addPath(glowPath.cgPath)
context.clip()

let glowGradient = CGGradient(
    colorsSpace: CGColorSpace(name: CGColorSpace.sRGB)!,
    colors: [
        NSColor(calibratedRed: 0.20, green: 0.83, blue: 0.92, alpha: 0.85).cgColor,
        NSColor(calibratedRed: 0.96, green: 0.67, blue: 0.24, alpha: 0.40).cgColor,
        NSColor(calibratedRed: 0.05, green: 0.08, blue: 0.14, alpha: 0.0).cgColor,
    ] as CFArray,
    locations: [0.0, 0.48, 1.0]
)!

context.drawLinearGradient(
    glowGradient,
    start: CGPoint(x: 160, y: 860),
    end: CGPoint(x: 860, y: 120),
    options: []
)
context.restoreGState()

let frameRect = CGRect(x: 132, y: 152, width: 760, height: 720)
let framePath = NSBezierPath(roundedRect: frameRect, xRadius: 172, yRadius: 172)
NSColor(calibratedWhite: 1.0, alpha: 0.10).setStroke()
framePath.lineWidth = 12
framePath.stroke()

let accentPath = NSBezierPath()
accentPath.move(to: CGPoint(x: 270, y: 250))
accentPath.line(to: CGPoint(x: 750, y: 770))
NSColor(calibratedRed: 0.20, green: 0.83, blue: 0.92, alpha: 0.58).setStroke()
accentPath.lineWidth = 28
accentPath.lineCapStyle = .round
accentPath.stroke()

let subAccentPath = NSBezierPath()
subAccentPath.move(to: CGPoint(x: 610, y: 212))
subAccentPath.line(to: CGPoint(x: 822, y: 424))
NSColor(calibratedRed: 0.96, green: 0.67, blue: 0.24, alpha: 0.82).setStroke()
subAccentPath.lineWidth = 22
subAccentPath.lineCapStyle = .round
subAccentPath.stroke()

let paragraph = NSMutableParagraphStyle()
paragraph.alignment = .center

let titleAttributes: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: 290, weight: .heavy),
    .foregroundColor: NSColor.white,
    .paragraphStyle: paragraph,
    .kern: -8,
]

let shadow = NSShadow()
shadow.shadowBlurRadius = 28
shadow.shadowOffset = NSSize(width: 0, height: -10)
shadow.shadowColor = NSColor(calibratedWhite: 0, alpha: 0.28)

let subtitleAttributes: [NSAttributedString.Key: Any] = [
    .font: NSFont.systemFont(ofSize: 58, weight: .semibold),
    .foregroundColor: NSColor(calibratedWhite: 1.0, alpha: 0.82),
    .paragraphStyle: paragraph,
    .kern: 10,
    .shadow: shadow,
]

NSGraphicsContext.current?.imageInterpolation = .high

let title = NSAttributedString(string: "LWA", attributes: titleAttributes)
let subtitle = NSAttributedString(string: "CLIPS", attributes: subtitleAttributes)

title.draw(in: CGRect(x: 150, y: 410, width: 724, height: 260))
subtitle.draw(in: CGRect(x: 210, y: 300, width: 604, height: 80))

image.unlockFocus()

guard
    let tiffData = image.tiffRepresentation,
    let bitmap = NSBitmapImageRep(data: tiffData),
    let pngData = bitmap.representation(using: .png, properties: [:])
else {
    fatalError("Could not encode app icon PNG")
}

let destination = outputDirectory.appendingPathComponent("AppIcon-1024.png")
try pngData.write(to: destination)

let normalize = Process()
normalize.executableURL = URL(fileURLWithPath: "/usr/bin/sips")
normalize.arguments = ["-z", "1024", "1024", destination.path, "--out", destination.path]
try normalize.run()
normalize.waitUntilExit()

guard normalize.terminationStatus == 0 else {
    fatalError("Could not normalize app icon to 1024x1024")
}

print(destination.path)
